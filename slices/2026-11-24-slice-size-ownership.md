# Slice size and lane ownership (2026-11-24)

Status: in progress
Mode: opus (Opus 5.5 leads and implements).

## Decisions

Michael asked how Bosun could raise throughput and quality, based on a month of rv-rez and crelaunch data and current practice on X ("how can we improve bosun and get more throughput and higher quality work"). The lead ranked ten changes and proposed its first three as one slice: a size cap, lane ownership and batched records. Michael: "Brief it".

This supersedes the 2026-11-15 "Fewer PRs" outcome "Slices are not resized". The lead dropped sizing then for lack of evidence. The evidence now:
- First verifies fail far more often on big slices:

| Changed lines | crelaunch | rv-rez |
|---|---|---|
| under 300 | 19–34% | 16% |
| over 1,000 | 67–71% | 40% |

- Anthropic's Oct 15 code-review post found that most changes over 1,000 lines draw review findings.

## Brief

Outcome: Slices stay small enough to pass verification on the first try, parallel lanes don't collide on files or contracts, and records stop paying for CI runs of their own.

Done-conditions:
S1. `todo` Slice size, in `rules/core.md`:
- A slice brief states its estimated size in changed lines of source and tests.
- Generated files, lockfiles, snapshots and records (spec, slice records, docs, boards) don't count.
- A slice estimated above about 400 lines is split into parts before building. Each part stands alone as its own slice and PR, and the next part starts once the previous one merges ("Following a PR" already does this).
- If the diff passes about 400 lines before the done-conditions are met, the lead stops adding, finishes the part that stands alone, and moves the rest into the next part's brief.
- A mechanical change (a rename, a codemod, a generated migration) may exceed the cap, with the reason in the brief.
- The Nov 15 "Slices are not resized" outcome is noted as superseded.
S2. `todo` `skills/bosun-brief/SKILL.md`'s brief template gains a `Size:` line (an estimate, and the parts when split), and step 6 carries the mid-build re-split.
S3. `todo` Lane ownership, in `rules/core.md` ("Approval" and "Areas and assigned slices") and `skills/bosun-brief/SKILL.md` ("Lanes" step 2, the lane template):
- The hub's proposal declares, for each lane, the files and directories, tables, and shared contracts (types, schemas, migrations, API shapes) it plans to touch.
- The hub does not run two lanes whose declarations overlap.
- A shared contract both areas need lands first, as its own small slice. The hub runs it itself before the lanes start, like the setup slice, or once lanes run, assigns it to one lane while the other waits for it to merge.
- A lane that finds it must touch something outside its declaration asks the hub first.
- The lane template carries the lane's declaration.
S4. `todo` Batched records: `rules/core.md` "Records ride along" and the hub's bullet in `skills/bosun-brief/SKILL.md` say the hub's own log entries (production pushes, refunds, approvals and other events it records) are records. They go on the hub's records branch, which is pushed, and never get a PR of their own, inside or outside a run. That branch's PR opens at a milestone end, at the run's end, or when the user asks.
S5. `todo` README's "Lanes" and run-policy text names S1, S3 and S4 where it describes them. The version is 0.34.0 in both manifests and the README version line.
S6. `todo` Checks pass:
- `bash -n scripts/*.sh`
- JSON parses for both manifests and `hooks/hooks.json`
- `python3 -m py_compile scripts/*.py`
- `claude plugin validate .`
- `git diff origin/main --check`
- the project-name grep over added lines finds nothing

Out of scope:
- Stacked PRs. GitHub's are generally available, but their interaction with the merge queue is untested.
- A PR watcher, the findings-to-checks routine, metrics, the decision queue, and moving lanes off the Mac.
- Changing lane counts.
- Any project's own spec.

Assumptions:
- **About 400 lines.** It sits between the measured buckets: under 300 lines fails 19–34% of first verifies, and 300–1,000 fails 46–52% in crelaunch. Counting source and tests matches what the measured diffs contained, minus records.
- **Parts merge in order.** Bosun never stacks on unmerged branches, so a dependent part waits for its base's merge. The added merge latency is the price; independent parts can run meanwhile.
- **The hub's records branch outside a run.** A hub session is usually in a run. When it isn't, its log entries still ride its pushed records branch, so nothing is lost if the session ends.
- **Versioning.** Minor, because the behavior changes.

Decisions setting: ask (default).
Effort assumed: high.
Verifier effort: high (no override at any scope).
Checks: as in S6.
Branch: slice-size-ownership, from main (87195d0).

## Evidence

## Verify

## Follow-ups
