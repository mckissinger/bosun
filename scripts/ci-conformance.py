#!/usr/bin/env python3
"""Check a repository's GitHub Actions setup against bosun-ci's standard.

Stack-agnostic: it reads workflow structure, test-runner retry settings and the
default branch's merge setup, not test commands. Detections of change-based
selection, the push-run skip and the flake hunt are heuristics; confirm a WARN
before acting on it.

Exit status: 1 when any FAIL is found, 0 otherwise, 2 on a usage error.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

FAIL, WARN, INFO, OK = "FAIL", "WARN", "INFO", "OK"


def load_yaml(path):
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        pass
    if not shutil.which("ruby"):
        raise SystemExit("needs PyYAML or ruby to parse YAML")
    out = subprocess.run(
        ["ruby", "-ryaml", "-rjson", "-e", "puts JSON.generate(YAML.safe_load(STDIN.read, aliases: true))"],
        input=text, capture_output=True, text=True, check=True,
    ).stdout
    return json.loads(out)


def triggers(wf):
    """Return {event: config} from a workflow's `on:` (YAML 1.1 reads `on` as True)."""
    on = wf.get("on", wf.get(True))
    if isinstance(on, str):
        return {on: None}
    if isinstance(on, list):
        return {e: None for e in on}
    if isinstance(on, dict):
        return on
    return {}


def gh_json(args):
    if not shutil.which("gh"):
        return None
    r = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def repo_from_remote(repo_dir):
    r = subprocess.run(["git", "-C", str(repo_dir), "remote", "get-url", "origin"], capture_output=True, text=True)
    m = re.search(r"github\.com[:/]([^/]+/[^/.]+)", r.stdout.strip())
    return m.group(1) if m else None


def merge_setup(repo, branch):
    """Required checks, strict flag, queue and owner type; None values mean unknown."""
    owner, name = repo.split("/", 1)
    info = {"owner_type": None, "required": None, "strict": None, "queue": None}
    meta = gh_json([f"repos/{repo}"])
    if meta:
        info["owner_type"] = meta.get("owner", {}).get("type")
        branch = branch or meta.get("default_branch")
    info["branch"] = branch or "main"
    required, strict = set(), False
    prot = gh_json([f"repos/{repo}/branches/{info['branch']}/protection"])
    if prot and prot.get("required_status_checks"):
        rsc = prot["required_status_checks"]
        required |= set(rsc.get("contexts") or [])
        required |= {c.get("context") for c in rsc.get("checks") or [] if c.get("context")}
        strict = strict or bool(rsc.get("strict"))
    rules = gh_json([f"repos/{repo}/rules/branches/{info['branch']}"])
    queue = False
    for rule in rules or []:
        if rule.get("type") == "required_status_checks":
            p = rule.get("parameters") or {}
            required |= {c.get("context") for c in p.get("required_status_checks") or [] if c.get("context")}
            strict = strict or bool(p.get("strict_required_status_checks_policy"))
        if rule.get("type") == "merge_queue":
            queue = True
    q = gh_json(["graphql", "-f",
                 f'query=query{{repository(owner:"{owner}",name:"{name}"){{mergeQueue(branch:"{info["branch"]}"){{id}}}}}}'])
    if q is not None:
        queue = queue or bool(((q.get("data") or {}).get("repository") or {}).get("mergeQueue"))
    if meta is not None:
        info.update(required=required, strict=strict, queue=queue)
    return info


def job_names(job_id, job):
    names = {job_id}
    n = job.get("name") if isinstance(job, dict) else None
    if isinstance(n, str):
        names.add(n)
        names.add(re.sub(r"\$\{\{.*?\}\}", "", n).strip(" ()"))
    return {x for x in names if x}


def max_number(text):
    nums = [int(n) for n in re.findall(r"\b(\d+)\b", text)]
    return max(nums) if nums else None


def retry_settings(repo_dir):
    """(file, key, max value) for Playwright `retries` and Vitest/Jest `retry` settings."""
    found = []
    pats = [("playwright.config.*", r"^\s*retries\s*:\s*([^,\n]+)"),
            ("vitest.config.*", r"^\s*retry\s*:\s*([^,\n]+)"),
            ("vitest.workspace.*", r"^\s*retry\s*:\s*([^,\n]+)"),
            ("jest.config.*", r"retryTimes\(\s*(\d+)")]
    tracked = subprocess.run(["git", "-C", str(repo_dir), "ls-files"], capture_output=True, text=True).stdout.splitlines()
    for glob, pat in pats:
        for rel in tracked:
            f = repo_dir / rel
            if not f.match(glob) or "node_modules" in f.parts:
                continue
            for m in re.finditer(pat, f.read_text(encoding="utf-8", errors="ignore"), re.M):
                v = max_number(m.group(1))
                if v is not None:
                    found.append((str(f.relative_to(repo_dir)), m.group(0).strip(), v))
    return found


def check(repo_dir, repo, branch, spec, offline):
    findings = []

    def add(level, check_id, msg):
        findings.append({"level": level, "check": check_id, "detail": msg})

    wf_dir = repo_dir / ".github" / "workflows"
    workflows = {}
    for f in sorted(list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml"))):
        try:
            wf = load_yaml(f) or {}
        except Exception as e:  # noqa: BLE001 - report any parse failure as a finding
            add(FAIL, "workflow-parse", f"{f.name}: does not parse ({e.__class__.__name__})")
            continue
        workflows[f.name] = (wf, f.read_text(encoding="utf-8"))
    if not workflows:
        add(FAIL, "workflows", "no workflows in .github/workflows")
        return findings, {}

    setup = {"owner_type": None, "required": None, "strict": None, "queue": None, "branch": branch or "main"}
    if not offline and repo:
        setup = merge_setup(repo, branch)
    default = setup["branch"]

    # Merge setup.
    if setup["queue"] is None:
        add(INFO, "merge-setup", "repository settings unknown (offline, or gh could not read them)")
    else:
        q = "on" if setup["queue"] else "off"
        add(INFO, "merge-setup", f"merge queue {q}; up-to-date branches {'required' if setup['strict'] else 'not required'}; "
            f"required checks: {', '.join(sorted(setup['required'])) or 'none'}")
        if setup["strict"] and not setup["queue"]:
            add(FAIL, "merge-setup", "branches must be up to date but there is no merge queue: every merge leaves open PRs behind")
        if not setup["queue"]:
            add(WARN, "merge-setup", "no merge queue (recommended where GitHub offers one)")

    # Required checks map to jobs whose workflow runs on PRs (and in the queue).
    by_name = {}
    for fname, (wf, _) in workflows.items():
        for jid, job in (wf.get("jobs") or {}).items():
            for n in job_names(jid, job):
                by_name.setdefault(n, []).append(fname)
    for ctx in sorted(setup["required"] or []):
        base = re.sub(r"\s*\(.*\)$", "", ctx).strip()
        files = by_name.get(ctx) or by_name.get(base)
        if not files:
            add(WARN, "required-checks", f"'{ctx}' maps to no workflow job (an app's check, or a renamed job)")
            continue
        for fname in sorted(set(files)):
            trig = triggers(workflows[fname][0])
            if "pull_request" not in trig and "pull_request_target" not in trig:
                add(FAIL, "required-checks", f"'{ctx}' ({fname}) has no pull_request trigger, so it never reports on PRs")
            if setup["queue"] and "merge_group" not in trig:
                add(FAIL, "required-checks", f"'{ctx}' ({fname}) has no merge_group trigger, so queued PRs hang")

    # Runners.
    for fname, (wf, _) in workflows.items():
        for jid, job in (wf.get("jobs") or {}).items():
            if not isinstance(job, dict) or "uses" in job:
                continue
            ro = job.get("runs-on")
            label = json.dumps(ro) if not isinstance(ro, str) else ro
            if ro is None or "blacksmith" in label:
                continue
            if setup["owner_type"] == "User":
                add(INFO, "runners", f"{fname}:{jid} on {label} (personal repository: Blacksmith not available)")
            else:
                add(WARN, "runners", f"{fname}:{jid} on {label}, not a Blacksmith runner")

    # Retries.
    retries = retry_settings(repo_dir)
    for f, line, v in retries:
        if v > 1:
            add(FAIL, "retries", f"{f}: '{line}' allows {v} retries (the standard is at most one)")
    if not retries:
        add(INFO, "retries", "no Playwright/Vitest/Jest retry setting found")

    # Change-based selection on PR workflows.
    sel = re.compile(r"paths-filter|changed-files|--changed|--only-changed|affected|\bscope\b|git diff[^\n]*(base|origin)", re.I)
    pr_wfs = [n for n, (wf, _) in workflows.items() if "pull_request" in triggers(wf)]
    for fname in pr_wfs:
        wf, text = workflows[fname]
        pr = triggers(wf).get("pull_request") or {}
        if isinstance(pr, dict) and (pr.get("paths") or pr.get("paths-ignore")):
            continue
        if not sel.search(text):
            add(WARN, "selection", f"{fname}: no change-based selection detected; PRs run everything (heuristic)")

    # Concurrency on PR workflows.
    for fname in pr_wfs:
        wf, _ = workflows[fname]
        c = wf.get("concurrency")
        if not (isinstance(c, dict) and c.get("cancel-in-progress")):
            add(WARN, "concurrency", f"{fname}: no workflow-level concurrency with cancel-in-progress for superseded PR runs")

    # Push runs the queue already proved.
    if setup["queue"]:
        for fname, (wf, text) in workflows.items():
            trig = triggers(wf)
            if "push" not in trig or "merge_group" not in trig:
                continue
            push = trig.get("push") or {}
            branches = push.get("branches") if isinstance(push, dict) else None
            if branches and default not in branches:
                continue
            jobs = {j: job for j, job in (wf.get("jobs") or {}).items() if isinstance(job, dict)}

            def needs(job):
                n = job.get("needs") or []
                return [n] if isinstance(n, str) else list(n)

            # A skip gate: a push-only job whose outputs other jobs read in their `if:`.
            gates = [g for g, job in jobs.items()
                     if "push" in str(job.get("if", ""))
                     and any(g in needs(k) and f"needs.{g}.outputs" in str(k.get("if", "")) for k in jobs.values())]
            if not gates:
                add(WARN, "push-skip", f"{fname}: push runs on {default} repeat what the queue proved; no repeat-run skip detected (heuristic)")
                continue
            for g in gates:
                job = jobs[g]
                perms = job.get("permissions") or wf.get("permissions") or {}
                if not (isinstance(perms, dict) and perms.get("actions") in ("read", "write")) and perms not in ("read-all", "write-all"):
                    add(FAIL, "push-skip", f"{fname}:{g} looks up queue runs without `actions: read`, so every lookup is refused")
                if not job.get("continue-on-error"):
                    add(FAIL, "push-skip", f"{fname}:{g} lacks job-level continue-on-error; a failed lookup turns the push run red")
                # Without always() or a cancelled() check, GitHub adds an implicit success()
                # over the whole needs chain, so the job skips whenever the gate is skipped.
                for k, kjob in jobs.items():
                    cond = str(kjob.get("if", ""))
                    if g in needs(kjob) and not re.search(r"always\(\)|cancelled\(\)", cond):
                        add(FAIL, "push-skip", f"{fname}:{k} needs {g} but its `if:` has no `!cancelled()` or `always()`, "
                            "so it is skipped on every PR and queue run")

    # Flake hunt.
    hunt = [n for n, (wf, text) in workflows.items()
            if "schedule" in triggers(wf) and re.search(r"repeat|--repeat-each|rerun", text, re.I)]
    if hunt:
        add(INFO, "flake-hunt", f"scheduled repeat run in {', '.join(hunt)}; confirm it covers every required suite")
    else:
        add(WARN, "flake-hunt", "no scheduled workflow that repeats tests (heuristic)")

    # CI budget.
    if spec and spec.exists():
        if not re.search(r"^\s*CI budget:", spec.read_text(encoding="utf-8"), re.M):
            add(WARN, "ci-budget", f"{spec.name} has no `CI budget:` line")
    else:
        add(INFO, "ci-budget", "no spec found; budget not checked")

    return findings, setup


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo-dir", default=".", help="repository checkout (default: .)")
    ap.add_argument("--repo", help="owner/name (default: from the origin remote)")
    ap.add_argument("--branch", help="default branch (default: from GitHub, else main)")
    ap.add_argument("--spec", help="spec path (default: SPEC.md in the checkout)")
    ap.add_argument("--offline", action="store_true", help="skip GitHub settings")
    ap.add_argument("--json", action="store_true", help="print JSON")
    a = ap.parse_args()

    repo_dir = Path(a.repo_dir).resolve()
    if not (repo_dir / ".git").exists():
        print(f"{repo_dir} is not a git checkout", file=sys.stderr)
        return 2
    repo = a.repo or repo_from_remote(repo_dir)
    spec = Path(a.spec) if a.spec else repo_dir / "SPEC.md"
    findings, setup = check(repo_dir, repo, a.branch, spec, a.offline or not repo)
    fails = sum(f["level"] == FAIL for f in findings)
    warns = sum(f["level"] == WARN for f in findings)

    if a.json:
        print(json.dumps({"repo": repo, "fails": fails, "warns": warns, "findings": findings}, indent=2))
    else:
        print(f"CI conformance: {repo or repo_dir.name} — {fails} FAIL, {warns} WARN")
        order = {FAIL: 0, WARN: 1, INFO: 2, OK: 3}
        for f in sorted(findings, key=lambda f: order[f["level"]]):
            print(f"  {f['level']:4}  {f['check']:15}  {f['detail']}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
