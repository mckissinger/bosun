# PR watcher (2026-11-25)

Status: in progress
Mode: opus (Opus 5.5 leads and implements).

## Decisions

From the 2026-11-24 throughput analysis, item 4: "an always-on PR watcher". Tonight these PRs sat stuck because nothing watches a PR once its session goes quiet:
- rv-rez #1266, #1289 and #1290;
- crelaunch #1172, which sat green and unqueued for about 30 minutes.

Asked "What now?", the lead recommended the watcher next. Asked "Are you sure 1 hasn't been done?", the lead checked and found most of item 1 already done. Michael: "Yes" to sending the leftovers and starting the watcher.

## Brief

Outcome: A PR that is stuck after its owning session went quiet gets handled within about an hour without anyone watching. Stuck means removed from the merge queue, green but left unqueued, red, or conflicting. It is re-queued, re-armed or cleanly updated where that is safe, and otherwise labelled `needs-owner` with a diagnosis that any session's open-PR check picks up.

Size: about 150 changed lines, all prompt text and docs, under the cap.

Done-conditions:
W1. `todo` `templates/pr-watcher.md` is the saved prompt for a Claude Code cloud scheduled task.
- **Triggers:** a GitHub `pull_request` `labeled` trigger filtered to the `queue-ejected` label, plus an hourly schedule as a sweep.
- **Classes it handles** (open, non-draft PRs on the default branch):
  - (a) removed from the queue (latest `RemovedFromMergeQueueEvent` not `merged`, actor `github-merge-queue`) and not back in;
  - (b) green, not queued, auto-merge off, after auto-merge had been armed by the repository owner's account and was last turned off by the queue or a push, not by a person;
  - (c) red required check on the PR's own head;
  - (d) conflicting.
- **It leaves a PR alone when:**
  - its title or labels say do not arm, or it carries `hold`;
  - it comes from a fork or another author;
  - it had a push, comment or review in the last 30 minutes, since its own session may be on it;
  - the watcher already acted on it for the same reason.
- **Allowed actions:**
  - re-queue once for `invalid_merge_commit`, `branch_protection_failure` or `checks_timed_out`;
  - re-queue once for `failed_checks` only when every failed job also failed on another queue entry or on the default branch in the last 24 hours, which makes it a flake candidate;
  - re-arm (b);
  - for (a) `merge_conflict` or (d), merge the default branch in and push only when the merge has no conflicts;
  - otherwise comment a diagnosis (reason, failed jobs with links, what it checked) and add `needs-owner`.
- **It never:** changes code beyond that clean merge, merges a PR directly, pushes to the default branch, arms a PR that was never armed, or re-queues twice for one reason.
- **Reporting:** each run comments its actions on the PRs it touched and appends a summary to one standing issue.
W2. `todo` `skills/bosun-ci/SKILL.md` gains "PR watcher (opt-in)", set up per repository when the user asks:
- create the scheduled task from the template (`/schedule` or claude.ai/code/routines);
- confirm in its first run that the cloud session can read and act on PRs with `gh` or the GitHub connector, and record where it runs;
- the limits: research preview, hourly caps, and runs that count toward the user's usage;
- the queue ejection notice is a prerequisite, because its label is the trigger;
- "Select the outcome" names it.
W3. `todo` `rules/core.md` "Watching open PRs": a PR labelled `needs-owner` counts as one to fix. The session that owns it, or the hub when that session is gone, takes it and removes the label once it is handled. `skills/bosun-brief/SKILL.md`'s open-PR sentence in "Until blocked" carries the same.
W4. `todo` README names the watcher where it describes opt-in `/bosun-ci` setups and in the merge flow. The version is 0.35.0 in both manifests and the README version line.
W5. `todo` Checks pass:
- `bash -n scripts/*.sh`
- JSON parses for both manifests and `hooks/hooks.json`
- `python3 -m py_compile scripts/*.py`
- `claude plugin validate .`
- `git diff origin/main --check`
- the project-name grep over added lines finds nothing

Out of scope:
- Creating the scheduled task in any repository. That is a per-repository setup on the user's request, and it changes persistent configuration on their account.
- The watcher fixing code or tests.
- Metrics and the decision queue.

Assumptions:
- **Cloud scheduled tasks** are the host. Per code.claude.com/docs/en/routines (read 2026-11-25), they offer GitHub `pull_request` triggers with a label filter, run on Pro, Max, Ultra, Team and Enterprise, and have hourly caps of 100 scheduled runs per account. GitHub webhook events beyond the caps are dropped, which is why the hourly sweep backs the label trigger.
- **Thirty quiet minutes.** A live session usually acts within minutes of a removal, and waiting avoids two actors on one PR.
- **The flake test.** "The same job failed elsewhere in the last day" is conservative and needs no test run. A real failure goes to the owner.
- **Re-arm only what was armed.** "Do not arm" PRs are never armed. A PR whose auto-merge a person turned off stays off.

Decisions setting: ask (default).
Effort assumed: high.
Verifier effort: high (no override at any scope).
Checks: as in W5.
Branch: pr-watcher, from main (a5cae57).

## Evidence

## Verify

## Follow-ups
