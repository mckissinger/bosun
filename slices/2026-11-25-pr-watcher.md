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
W1. `todo` `templates/pr-watcher.md` is the saved prompt for a Claude Code cloud scheduled task. Reworded after the first verify.
- **Triggers:** a GitHub `pull_request` `labeled` trigger filtered to `queue-ejected`, plus an hourly sweep.
- **Candidates:** open, non-draft PRs from the owner's account and this repository, targeting the default branch.
  - Excluded: "do not arm" titles or labels, `hold`, and `needs-owner`.
  - Excluded: any sign of the PR's own session in the last 30 minutes. The notice's and the watcher's own comments don't count as signs.
- **Classes, taken in order:** (a) removed from the queue; (d) conflicting; (c) red; (b) armed but stuck unqueued for 30 minutes.
- **Earlier attempts** are counted from the timeline's queue entries on the current head.
- **Actions:**
  - re-queue on the first attempt for `invalid_merge_commit` or `branch_protection_failure`;
  - for `failed_checks` or `checks_timed_out`, re-queue once only when every failing test also failed in the last day somewhere this PR couldn't reach, naming the tests;
  - merge the default branch into the PR's own branch and push, when the merge is clean;
  - toggle auto-merge once for (b);
  - otherwise, including a second removal, hand off with `needs-owner` and a diagnosis.
- **Never:** change code, merge directly, push to the default branch, arm a PR the queue didn't disarm, approve deployments, submit reviews, rerun workflows, or touch other labels.
- **Reporting:** a standing-issue comment only when the run acted or skipped a candidate.

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

- W5 self-check after the commit at 1e550f7 (fingerprint 7447e59): `bash -n`, JSON, `py_compile`, `claude plugin validate .`, `git diff --check` and the project-name grep all pass.

## Verify

- 1st (1e550f7, fingerprint 7447e59), bosun-verifier claude-opus-5-5 / high: FAIL. Findings:
  1. Blocking: class (b) overlapped (a), so a `failed_checks` removal could be re-armed, which meant re-queued, with no flake test, and could loop with the notice.
  2. Blocking: `checks_timed_out` was re-queued blindly, against core "Queue removal". The rule now follows core.
  3. The once-only limit ignored sessions' re-queues, and second removals were skipped.
  4. The notice's own comment made the label trigger skip the PR it fired for.
  5. (b) lacked the data to tell a person's disarm apart.
  6. The flake test counted queue runs that contained the PR.
  7. The "never" list missed approvals, reviews and reruns.
  8. Copies missed clauses.
  9. Deferral: the 30-minute window can't see a session's unpushed work.
  10. The standing issue would get noise.

  Plus two nits. Fixed in the next commit: (b) became "armed but stuck"; the classes are ordered; attempts are counted from the timeline. The verifier couldn't fetch the scheduled-tasks docs; the lead read them (code.claude.com/docs/en/routines, 2026-11-25).

- 2nd (53c3501, fingerprint 377f421), delta re-check, bosun-verifier claude-opus-5-5 / high: FAIL. Ledger findings 1 and 3–10 were resolved. Finding 2 was still open: the flake gate's "every failed test" was true when no test failed, so timeouts and non-test failures were re-queued with no evidence.
  - New bugs: 11, the toggle against the never list, which could leave a PR disarmed; 12, no memory of "toggle once"; 13, the label run racing a live session; 14, attempt counting with no commit on the queue event; 15, (a) looser than core.
  - This was the second FAIL on one finding, so the slice stopped for Michael under `Decisions: ask`. Michael: "Fix it".
  - All fixed in the next commit:
    - a flake needs at least one named failing test;
    - the toggle is an exception in the never list, comments itself, and hands off if re-enabling fails;
    - a removal must be 30 minutes old;
    - attempts are counted by time since the latest commit;
    - the watcher acts on a PR at most twice;
    - (a) needs auto-merge off and no commit since the removal;
    - other reasons follow core.

## Follow-ups

- pr-watcher, 2026-11-25, deferral: the watcher's 30-minute quiet window can't see a session's local, unpushed work. If a session's push is rejected because the watcher merged the default branch into its PR, the session must pull first. Add that to "Following a PR" if it happens in practice.
