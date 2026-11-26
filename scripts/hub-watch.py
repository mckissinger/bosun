#!/usr/bin/env python3
"""Wake a Bosun hub (or a lane) when a watched PR or lane changes.

Run it in the background. It exits, printing one line per event, the first
time any of these happens after it starts:

  - a watched PR merges or closes (or already has when it starts);
  - a watched PR's checks turn red, or it starts to conflict;
  - a watched PR stops merging: it is open, not in the merge queue and its
    auto-merge is off (a queue removal, or green but not merging), or it is
    green with auto-merge on but behind a base that requires up-to-date
    branches; each is confirmed by a second look before it is reported;
  - a watched lane's transcript goes quiet for --stale-minutes.

With nothing to report it exits after --max-minutes with a heartbeat line, so
the hub looks again. --status prints the current state and exits at once.
A new watcher for the same repo stops the one before it, so a hub never has
two running; the stopped one prints that it was replaced and exits 0.

Uses only `gh` and the lane's transcript folder under ~/.claude/projects.
No GNU `timeout` is needed, so it runs on macOS as it is.
"""
import argparse
import glob
import tempfile
import json
import os
import re
import signal
import subprocess
import sys
import time

QUERY = """query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){pullRequest(number:$n){
state isInMergeQueue mergeable mergeStateStatus autoMergeRequest{enabledAt}
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
        "behind": pr["mergeStateStatus"] == "BEHIND",
    }


def stalled(s):
    if s["state"] != "OPEN" or s["red"] or s["conflict"]:
        return False
    if not s["queued"] and not s["auto"]:
        return True
    return s["auto"] and s["behind"] and s["checks"] == "SUCCESS"


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
    if stalled(new) and not stalled(old):
        if new["auto"]:
            events.append("PR #%d is green with auto-merge on but behind its base; update it" % n)
        else:
            events.append("PR #%d stopped merging: open, not queued, auto-merge off (read its timeline for a queue removal)" % n)
    return events


def with_retries(repo, n, tries=3):
    for i in range(tries):
        try:
            return pr_state(repo, n)
        except Exception as e:  # noqa: BLE001
            last = e
            if i < tries - 1:
                time.sleep(5)
    raise RuntimeError("gh failed %d times in a row for PR #%d: %s" % (tries, n, last))


def replace_previous(repo):
    pidfile = os.path.join(tempfile.gettempdir(), "bosun-hub-watch-%s.pid" % re.sub(r"[^A-Za-z0-9]", "-", repo))
    try:
        old = int(open(pidfile).read().strip())
        cmd = subprocess.run(["ps", "-p", str(old), "-o", "command="], capture_output=True, text=True).stdout
        if old != os.getpid() and "hub-watch.py" in cmd:
            os.kill(old, 15)
            print("stopped the previous watcher (pid %d)" % old)
    except (OSError, ValueError):
        pass
    with open(pidfile, "w") as f:
        f.write(str(os.getpid()))


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
    if a.interval < 15 or a.stale_minutes <= 0 or a.max_minutes <= 0:
        ap.error("--interval must be at least 15 seconds, and --stale-minutes and --max-minutes above 0")

    try:
        base = {n: with_retries(a.repo, n) for n in a.pr}
    except Exception as e:  # noqa: BLE001 - report and stop
        print("error: %s" % e)
        return 1
    for n in a.pr:
        print(describe(n, base[n]))
    done = ["PR #%d already %s" % (n, base[n]["state"].lower()) for n in a.pr if base[n]["state"] != "OPEN"]
    active = set()
    for name, wt in lanes:
        q = quiet_minutes(wt)
        print("lane %s: %s" % (name, "no transcript found" if q is None else "last activity %d min ago" % q))
        if q is not None and q < a.stale_minutes:
            active.add(name)
    if a.status:
        return 0
    if done:
        print("\n".join(done))
        return 0
    replace_previous(a.repo)
    signal.signal(signal.SIGTERM, lambda *_: (print("replaced by a newer watcher; nothing to do"), sys.exit(0)))
    sys.stdout.flush()

    start, failures = time.time(), {n: 0 for n in a.pr}
    while True:
        time.sleep(a.interval)
        events = []
        for n in a.pr:
            if base[n]["state"] != "OPEN":
                continue
            try:
                new = pr_state(a.repo, n)
                failures[n] = 0
            except Exception as e:  # noqa: BLE001
                failures[n] += 1
                if failures[n] >= 3:
                    print("error: gh failed three times in a row for PR #%d: %s" % (n, e))
                    return 1
                continue
            found = changes(n, base[n], new)
            if found and stalled(new) and new["state"] == "OPEN" and not (new["red"] and not base[n]["red"]):
                time.sleep(15)  # a merging PR leaves the queue a moment before it merges
                try:
                    new = pr_state(a.repo, n)
                except Exception:  # noqa: BLE001
                    pass
                found = changes(n, base[n], new)
            events += found
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
            print("heartbeat: no change in %g min; run --status and look again" % a.max_minutes)
            return 0


if __name__ == "__main__":
    sys.exit(main())
