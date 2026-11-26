#!/usr/bin/env python3
"""Wake a Bosun hub (or a lane) when a watched PR or lane changes.

Run it in the background. It exits, printing one line per event, the first
time any of these happens after it starts:

  - a watched PR merges or closes;
  - a watched PR's checks turn red, or it starts to conflict;
  - a watched PR leaves the merge queue unmerged, or its auto-merge turns off;
  - a watched lane's transcript goes quiet for --stale-minutes.

With nothing to report it exits after --max-minutes with a heartbeat line, so
the hub looks again. --status prints the current state and exits at once.

Uses only `gh` and the lane's transcript folder under ~/.claude/projects.
No GNU `timeout` is needed, so it runs on macOS as it is.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time

QUERY = """query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){pullRequest(number:$n){
state isInMergeQueue mergeable autoMergeRequest{enabledAt}
commits(last:1){nodes{commit{statusCheckRollup{state}}}}}}}"""


def pr_state(repo, number):
    owner, name = repo.split("/", 1)
    out = subprocess.run(
        ["gh", "api", "graphql", "-f", "query=" + QUERY, "-F", "o=" + owner,
         "-F", "r=" + name, "-F", "n=%d" % number],
        capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or "gh failed")
    pr = json.loads(out.stdout)["data"]["repository"]["pullRequest"]
    nodes = pr["commits"]["nodes"]
    rollup = (nodes[0]["commit"]["statusCheckRollup"] or {}).get("state") if nodes else None
    return {
        "state": pr["state"],                      # OPEN, MERGED, CLOSED
        "queued": bool(pr["isInMergeQueue"]),
        "auto": pr["autoMergeRequest"] is not None,
        "conflict": pr["mergeable"] == "CONFLICTING",
        "red": rollup in ("FAILURE", "ERROR"),
        "checks": rollup or "NONE",
    }


def transcript_dir(worktree):
    path = os.path.abspath(os.path.expanduser(worktree))
    return os.path.join(os.path.expanduser("~/.claude/projects"), re.sub(r"[^A-Za-z0-9]", "-", path))


def quiet_minutes(worktree):
    files = glob.glob(os.path.join(transcript_dir(worktree), "*.jsonl"))
    if not files:
        return None
    return (time.time() - max(os.path.getmtime(f) for f in files)) / 60


def describe(n, s):
    flags = [s["state"].lower(), "checks " + s["checks"].lower()]
    flags.append("queued" if s["queued"] else "not queued")
    flags.append("auto-merge on" if s["auto"] else "auto-merge off")
    if s["conflict"]:
        flags.append("conflicting")
    return "PR #%d: %s" % (n, ", ".join(flags))


def changes(n, old, new):
    events = []
    if new["state"] != old["state"]:
        events.append("PR #%d %s" % (n, new["state"].lower()))
        return events
    if new["state"] != "OPEN":
        return events
    if new["red"] and not old["red"]:
        events.append("PR #%d checks turned red" % n)
    if new["conflict"] and not old["conflict"]:
        events.append("PR #%d now conflicts with its base" % n)
    if old["queued"] and not new["queued"]:
        events.append("PR #%d left the merge queue without merging (read its timeline for the reason)" % n)
    if old["auto"] and not new["auto"]:
        events.append("PR #%d auto-merge turned off" % n)
    return events


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True, help="owner/name")
    ap.add_argument("--pr", type=int, action="append", default=[], help="PR number to watch (repeatable)")
    ap.add_argument("--lane", action="append", default=[], help="NAME=WORKTREE_PATH of a lane to watch (repeatable)")
    ap.add_argument("--stale-minutes", type=float, default=45)
    ap.add_argument("--interval", type=float, default=90, help="seconds between looks")
    ap.add_argument("--max-minutes", type=float, default=120)
    ap.add_argument("--status", action="store_true", help="print the current state and exit")
    a = ap.parse_args()
    if "/" not in a.repo:
        ap.error("--repo must be owner/name")
    lanes = []
    for item in a.lane:
        if "=" not in item:
            ap.error("--lane takes NAME=WORKTREE_PATH")
        lanes.append(tuple(item.split("=", 1)))
    if not a.pr and not lanes:
        ap.error("give at least one --pr or --lane")

    try:
        base = {n: pr_state(a.repo, n) for n in a.pr}
    except Exception as e:  # noqa: BLE001 - report and stop
        print("error: %s" % e)
        return 1
    for n in a.pr:
        print(describe(n, base[n]))
    active = set()
    for name, wt in lanes:
        q = quiet_minutes(wt)
        print("lane %s: %s" % (name, "no transcript found" if q is None else "last activity %d min ago" % q))
        if q is not None and q < a.stale_minutes:
            active.add(name)
    if a.status:
        return 0
    sys.stdout.flush()

    start, failures = time.time(), 0
    while True:
        time.sleep(a.interval)
        events = []
        for n in a.pr:
            if base[n]["state"] != "OPEN":
                continue
            try:
                new = pr_state(a.repo, n)
                failures = 0
            except Exception as e:  # noqa: BLE001
                failures += 1
                if failures >= 3:
                    print("error: gh failed three times in a row: %s" % e)
                    return 1
                continue
            events += changes(n, base[n], new)
            base[n] = new
        for name, wt in lanes:
            q = quiet_minutes(wt)
            if q is None:
                continue
            if q < a.stale_minutes:
                active.add(name)
            elif name in active:
                active.discard(name)
                events.append("lane %s quiet for %d min" % (name, q))
        if events:
            print("\n".join(events))
            return 0
        if (time.time() - start) / 60 >= a.max_minutes:
            print("heartbeat: no change in %d min; run --status and look again" % a.max_minutes)
            return 0


if __name__ == "__main__":
    sys.exit(main())
