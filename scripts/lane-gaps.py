#!/usr/bin/env python3
"""Measure how long a project's started sessions (lanes and other sessions a
hub started) sat idle, and why, from their Claude Code transcripts.

  python3 lane-gaps.py --project ~/rv-rez [--days 14] [--repo owner/name] [--gap-minutes 30]

It reads ~/.claude/projects folders for the project and its worktrees, keeps
transcripts whose first message says another session started them, and finds
gaps of --gap-minutes or more between entries. Each gap is put in a bucket by
the session's last message before it (a rough text match, so read the
examples before trusting a bucket):

  context    the session stopped saying its context was heavy or full
  merge      it was waiting for a named PR to merge
  decision   it was waiting on the user or the hub
  other      anything else, often a finished session or a night

With --repo, it also looks up each PR a merge gap names and reports how long
the session stayed idle after that PR actually merged.
"""
import argparse
import glob
import json
import os
import re
import statistics
import subprocess
import time
from collections import Counter, defaultdict
from datetime import datetime

BUCKETS = [
    ("context", r"context (is|window|budget|limit|running|nearly|almost|is getting|getting)|heavy after|fresh lane|hand-?over note|handover"),
    ("merge", r"(#\d+)[^.]{0,60}merge|merge[sd]?[^.]{0,40}#\d+|when the hub says[^.]*merged"),
    ("decision", r"Michael|the user|hub's (answer|word|yes|go)|approv|your (yes|OK|answer|call)|\?\s*$"),
]


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def text(msg):
    c = msg.get("content") if isinstance(msg, dict) else msg
    if isinstance(c, str):
        return c
    return " ".join(b.get("text", "") for b in c or [] if isinstance(b, dict) and b.get("type") == "text")


def sessions(project, days):
    root = os.path.expanduser("~/.claude/projects")
    prefix = re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(os.path.expanduser(project)))
    cutoff = time.time() - days * 86400
    for d in os.listdir(root):
        if d != prefix and not d.startswith(prefix + "-"):
            continue
        for f in glob.glob(os.path.join(root, d, "*.jsonl")):
            if os.path.getmtime(f) < cutoff:
                continue
            ents, first, compactions = [], None, 0
            for line in open(f, errors="ignore"):
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if e.get("isCompactSummary"):
                    compactions += 1
                if not e.get("timestamp"):
                    continue
                if e.get("type") in ("user", "assistant"):
                    body = text(e.get("message", {}))
                elif e.get("type") == "queue-operation":
                    body = str(e.get("content", ""))
                else:
                    body = ""
                if first is None and body:
                    first = body
                ents.append((ts(e["timestamp"]), e.get("type"), body))
            if first and ("started this one" in first or "You are Lane" in first):
                ents.sort(key=lambda x: x[0])
                yield f, ents, compactions


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True, help="the project's main checkout")
    ap.add_argument("--days", type=float, default=14)
    ap.add_argument("--gap-minutes", type=float, default=30)
    ap.add_argument("--repo", help="owner/name, to measure idle time after merges")
    a = ap.parse_args()

    count = compacted = compactions = 0
    gaps = []
    for f, ents, c in sessions(a.project, a.days):
        count += 1
        compacted += c > 0
        compactions += c
        for i in range(1, len(ents)):
            g = ents[i][0] - ents[i - 1][0]
            if g < a.gap_minutes * 60:
                continue
            said = [x[2] for x in ents[:i] if x[1] == "assistant" and x[2].strip()]
            before = said[-1][-400:] if said else ""
            bucket = next((n for n, p in BUCKETS if re.search(p, before, re.I)), "other")
            gaps.append(dict(bucket=bucket, start=ents[i - 1][0], end=ents[i][0], before=before, file=f))

    print("started sessions: %d (%d compacted, %d compactions)" % (count, compacted, compactions))
    totals, mins = Counter(), Counter()
    for g in gaps:
        totals[g["bucket"]] += 1
        mins[g["bucket"]] += (g["end"] - g["start"]) / 60
    for name in ("decision", "merge", "context", "other"):
        print("  %-9s %4d gaps, %5.0f hours idle" % (name, totals[name], mins[name] / 60))
    examples = defaultdict(list)
    for g in sorted(gaps, key=lambda g: g["start"] - g["end"]):
        examples[g["bucket"]].append(g)
    for name in ("context", "merge"):
        for g in examples[name][:3]:
            print("  e.g. %s %s, %d min: ...%s" % (name, datetime.utcfromtimestamp(g["start"]).strftime("%Y-%m-%d %H:%M"),
                                                 (g["end"] - g["start"]) / 60, g["before"][-160:].replace("\n", " ")))

    if not a.repo:
        return 0
    merged_at = {}
    lags = []
    for g in (g for g in gaps if g["bucket"] == "merge"):
        best = None
        for n in set(re.findall(r"#(\d+)", g["before"])):
            if n not in merged_at:
                out = subprocess.run(["gh", "pr", "view", n, "-R", a.repo, "--json", "mergedAt"],
                                     capture_output=True, text=True)
                try:
                    m = json.loads(out.stdout).get("mergedAt")
                except ValueError:
                    m = None
                merged_at[n] = ts(m) if m else None
            t = merged_at[n]
            if t and g["start"] <= t <= g["end"]:
                best = (g["end"] - t) / 60
        if best is not None:
            lags.append(best)
    if lags:
        print("merge gaps whose PR merged during the gap: %d; idle after the merge: %.0f hours in all, median %.0f min, worst %.0f min"
              % (len(lags), sum(lags) / 60, statistics.median(lags), max(lags)))
    else:
        print("merge gaps whose PR merged during the gap: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
