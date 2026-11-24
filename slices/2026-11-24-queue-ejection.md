# Queue ejection (2026-11-24)

Status: in progress
Mode: opus (Opus 5.5 leads and implements).
Decisions: Michael asked what happens when a PR falls out of the merge queue on a failing test ("Does it automatically go to be fixed, or does our Claude session or agent have to monitor that? What's the best setup here?"). The lead found that nothing fixes it unless the PR's own session is alive and waiting, and that the rule then says to re-arm auto-merge, and recommended a rule change plus a `dequeued` notice workflow, with no dedicated fixing agent. Michael: "Yes, brief it".

## Brief

Outcome: A PR the merge queue removes is noticed and handled by its reason, by the session that owns it or, when that session is gone, by whoever reads the run's open PRs, instead of sitting open with green checks or being re-queued unread.

Done-conditions:
Q1. `todo` `rules/core.md`: "Following a PR" names removal from the merge queue as its own wake event (an open PR, not queued, auto-merge off, whose latest queue event is a removal whose reason is not `merged`), read from the PR's timeline (`RemovedFromMergeQueueEvent.reason`) and the failed `merge_group` run, and acts by reason: `failed_checks` and `checks_timed_out` are handled as a failing required check (fixed in that PR's worktree, verified when code changes, pushed, auto-merge armed again), except a flake candidate or environment failure, which is re-queued once and reported; `merge_conflict` merges the default branch in; any other reason re-queues once and, if removed again, is reported; a removal a person made is reported, never re-queued. It never re-arms auto-merge after `failed_checks` without reading the failed run. "Watching open PRs" counts such a PR, and a PR carrying the `queue-ejected` label, as one to fix, so the hub or any later session picks it up.
Q2. `todo` `skills/bosun-brief/SKILL.md`: the "Until blocked" open-PR sentence and the lane prompt template's "Following a PR" sentence carry the same event and the same no-blind-re-arm clause (no copy left without it).
Q3. `todo` `templates/queue-ejected.yml` is a workflow that runs on `pull_request_target` `dequeued` and `enqueued` (changed from `pull_request` after the first verify: GitHub runs no `pull_request` workflow on a PR with a merge conflict; it never checks out PR code): on `dequeued` with a reason other than `merged`, from the queue rather than a person, it comments on the PR with the reason (read from the timeline) and the names and links of the failed jobs of that PR's latest `merge_group` runs, and adds the `queue-ejected` label (creating it if missing); on `enqueued` it removes the label. It uses `GITHUB_TOKEN` only, with the least permissions it needs, and passes `actionlint`. `skills/bosun-ci/SKILL.md` adds it to "Turning on a merge queue" step 1 and describes it, and lists its absence among the WARNs.
Q4. `todo` `scripts/ci-conformance.py` reports a WARN when the repository has a merge queue and no workflow triggers on `pull_request_target` or `pull_request` with `dequeued`; rv-rez gives the new WARN and otherwise its earlier results, a fixture with the template gives none, and this repository (no queue) is unchanged.
Q5. `todo` README names the new behavior where it describes the merge flow and `/bosun-ci`; version 0.32.0 in both manifests and the README version line.
Q6. `todo` Checks pass: `bash -n scripts/*.sh`; JSON parses for both manifests and `hooks/hooks.json`; `python3 -m py_compile scripts/*.py`; `claude plugin validate .`; `actionlint templates/queue-ejected.yml`; `git diff origin/main --check`; the project-name grep over added lines in rules, skills, agents, scripts, templates, README.md and .claude-plugin finds nothing.

Out of scope:
- Installing the workflow in rv-rez, Ruthie or Skipline, and fixing rv-rez #1266; each is the project's own session's work.
- A scheduled routine that fixes ejected PRs on its own.
- The push-ci follow-ups on `ci-conformance.py` (the concurrency drift and two pattern bugs); they stay open.

Assumptions:
- **Reason values.** GitHub documents the `dequeued` payload's `reason` only as a required string, so the template and the rule read the reason from the GraphQL timeline, whose values were observed on rv-rez, Ruthie and Skipline: `merged`, `failed_checks`, `merge_conflict`, `invalid_merge_commit`, `branch_protection_failure`, `checks_timed_out`.
- **Finding the failed run.** A queue run's head branch is `gh-readonly-queue/<base>/pr-<n>-<sha>`, so the template filters `merge_group` runs by `/pr-<n>-`. The queue removes a PR on its first required failure, so the run can still be in progress; the template lists failed jobs whatever the run's state.
- **WARN, not FAIL.** The workflow is a notice; a queue works without it.
- **Template file.** The plugin had no templates; a real file can be linted and copied exactly, where prose cannot.
- **Versioning.** Minor bump: new rule behavior and a new file.

Decisions setting: ask (default).
Effort assumed: high.
Verifier effort: high (no override at any scope).
Checks: as in Q6. No end-to-end suite; CI's `checks` job is the required check.
Branch: queue-ejection, from main (8635529).

## Evidence

- Before the slice (2026-11-24): rv-rez #1266 removed with `failed_checks` at 21:39 UTC (queue run 45490703710: `unit` and `unit-component` failed); at 22:49 it was open with every PR check green or skipped, merge state `CLEAN`, auto-merge off. Ruthie #416 was re-queued 11 hours after its removal; Skipline #127 was re-queued with no change and removed again with `failed_checks`.

- Q3 dry run: the template's script, with label and comment writes stubbed to print, run against rv-rez: #1266 gives reason `failed_checks` and links `unit` and `unit-component` in queue run 45490703710; #1219 and #1220 (merged) exit with nothing; Skipline #84 (`merge_conflict`, open) gives the reason and the "none found" line; `enqueued` only removes the label. `actionlint` 1.7.12 (with shellcheck) clean.
- Q4: rv-rez (queue) went from 1 FAIL 0 WARN to 1 FAIL 1 WARN, the new `queue-ejection` WARN; with the template copied in, the WARN becomes INFO, and so does a `types: dequeued` string form. A first version counted the template as a PR CI workflow and added selection and concurrency WARNs; PR-workflow checks now skip a `pull_request` workflow whose `types` leave out opened, synchronize and reopened. The template's `ubuntu-latest` still gives the runners WARN in an organization repository, as the skill says to set the label. crelaunch went from 1 FAIL 3 WARN to 1 FAIL 4 WARN, the new WARN only; its merge queue is now on. This repository: 0 FAIL 2 WARN, unchanged.
- Q6: `bash -n`, the three JSON files, `py_compile`, `claude plugin validate .` ("Validation passed"), `actionlint`, `git diff origin/main --check` and the project-name grep all pass.

- Fix round 1: dry run with writes stubbed: rv-rez #1266 and Skipline #84 as before, #1219 (merged) and `enqueued` exit with no notice; a lookup error (PR 99999999 with payload reason `failed_checks`) now gives reason `failed_checks` and the "none found" line instead of error JSON. Conformance after the fix: rv-rez 1 FAIL 1 WARN, the fixture INFO (runners WARN only), crelaunch 1 FAIL 4 WARN, this repository 0 FAIL 2 WARN; all Q6 checks pass.

## Verify

- 1st (85e8b21, fingerprint bbe8058), bosun-verifier claude-opus-5-5 / high: PASS WITH FOLLOW-UPS. Q1–Q6 met, all checks exit 0. Bugs in this slice, fixed: an API error's JSON, which `gh --jq` prints on stdout, was read as the reason or as run ids; `pull_request` workflows do not run while a PR has a merge conflict (the most common removal), so the template moved to `pull_request_target` (no checkout, API only). Drift, fixed: two "Following a PR" sentences had moved into "Queue removal"; "Watching open PRs" pointed at the wrong section; README's merge-flow and lane copies left out clauses. Follow-up taken: a removal a person made is reported, never re-queued, and gets no notice. Nit fixed: "core rules'" prefix. Not verifiable without a live write: the label and comment calls under `GITHUB_TOKEN`, and least permissions.
- 2nd (9389fb6, fingerprint d5d6a9e), bosun-verifier claude-opus-5-5 / high: PASS WITH FOLLOW-UPS. Q1–Q6 met, all first-verify findings fixed; `pull_request_target` safety confirmed (no checkout, no expression in `run:`), and simulated timeline outcomes all exit 0. Drift, fixed: the two bosun-brief copies left out the person-removal clause, and "Watching open PRs" would pause a slice for a removal it only reports. Not verifiable without a live write: label and comment calls, least permissions (`pull-requests: read` may suffice), a real `pull_request_target` run on a conflicted PR, a removal by a person.

## Follow-ups
