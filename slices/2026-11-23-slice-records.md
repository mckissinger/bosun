# Slice records (2026-11-23)

Status: verified 2026-11-23 (first FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS; two drifts recorded below)
Mode: opus (Opus 5.5 leads and implements).
Decisions: Michael, after the plan named it as the next Bosun slice before lanes per project grow: "start the Bosun slice now". Lane lesson 3 (2026-11-17) and the throughput-rules deferral record the problem: every slice wrote its log, decisions and evidence into one spec section, so each merge left every other open PR conflicting, and one PR merged main three times only for SPEC.md.

## Brief

Outcome: Parallel slices stop conflicting in the spec: each slice keeps its brief, evidence, verify verdicts, log line and follow-ups in its own record file next to the spec, and the spec changes per slice only in its done-condition statuses and lessons. The open lane-end and conformance-check bugs are fixed alongside.

Done-conditions:
R1. `verified 2026-11-23 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS; fingerprint 063338d` `rules/core.md` "The spec" defines slice records: one file per slice, `slices/<date>-<slice-name>.md` beside the spec, holding its brief, evidence lines, verify verdicts, its log line (`Log:`) and its follow-ups. The current slices are the records not yet on the default branch; the slice log is the records' log lines plus any older entries the spec holds; open follow-ups are the spec's follow-ups section plus each record's Follow-ups. Per slice the spec changes only in done-condition statuses and lessons. A spec without the folder gets it with its first slice, plus one pointer line in the current-slice section, the slice log and the follow-ups section. The spec section's requirement for a current-slice section, follow-ups and the move of merged briefs to history read accordingly.
R2. `verified 2026-11-23 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS; fingerprint 063338d` Every rule and skill that reads or writes the current slice, the slice log or follow-ups agrees with R1: core "Run policy" (records ride along, exhausted roadmap), "Merge flow" ("Spec edits"), "Lanes" ("Branches and the spec", lane end), "Follow-ups and milestones" and "Finishing"; `bosun-brief` ("No spec yet", steps 1, 3, 6, 9, "Until blocked", the lane template's "Spec:" line, the hub bullets, "Exhausted roadmap"); `bosun-verify` (where the brief and its `Verifier effort:` are, the log line, marking verified); `bosun-triage` (active-slice check, follow-ups, missed items, spec health, archive, recurring verify failures, bookkeeping); `bosun-checkpoint`; `bosun-mode` (current-slice override); `bosun-ci` (slice log); `scripts/session-start.sh` (the compaction reminder names the open record); README.
R3. `verified 2026-11-23 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS; fingerprint 063338d` Lane end (throughput-rules bugs): core "Lane end" and the lane template's "Done" line count a PR parked on a red check the lane has stopped fixing (verify limit, an environment failure after its rerun) as one that cannot merge on its own; `bosun-brief` "In a lane session" carries the "once each of its PRs has merged or closed or cannot merge on its own" clause.
R4. `verified 2026-11-23 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS; fingerprint 063338d` `scripts/ci-conformance.py` (ci-conformance bugs): the push-skip gate is a job whose `if:` requires `github.event_name == 'push'`; a classic-protection 404 counts as "no protection" only when the `gh` login is a repository admin (else settings unknown), and `skills/bosun-ci/SKILL.md` "Establish the baseline" says the same; the Ruby fallback permits dates and times, and a parse FAIL does not add a second "no workflows" FAIL; retry findings are deduplicated by file and line and ignore numbers in comments; pytest `--reruns` and RSpec retry settings are read, and the skill and README name the runners it reads.
R5. `verified 2026-11-23 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS; fingerprint 063338d` Version 0.31.0 in both manifests and the README version line.
R6. `verified 2026-11-23 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS; fingerprint 063338d` This repository adopts records: this slice's record is this file; SPEC.md gains the three pointer lines and the ci-conformance brief moves to history; the seven follow-ups R3 and R4 fix (two throughput-rules bugs, five ci-conformance bugs) are removed from SPEC.md.
R7. `verified 2026-11-23 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS; fingerprint 063338d` Checks pass: `bash -n scripts/*.sh`; JSON parses for both manifests and `hooks/hooks.json`; `python3 -m py_compile scripts/*.py`; `claude plugin validate .`; `git diff origin/main --check`; the project-name grep over added lines in rules, skills, agents, scripts, README.md and .claude-plugin finds nothing; `scripts/ci-conformance.py` gives the same rv-rez and crelaunch results as before plus fixtures for each R4 fix.

Out of scope:
- Moving existing projects' old slice logs or briefs into records; they stay where they are, and records start with each project's next slice.
- Decisions, undecided and out-of-scope items, which stay in the spec (the hub's records branch already serialises them).
- The planning-hub third-lane deferral and the "At most three sessions" cap.

Assumptions:
- **Statuses stay in the spec.** Done-condition status lines are distinct lines per slice and area, so they rarely conflict; moving them out would split the roadmap.
- **Follow-ups stay where they are found.** A follow-up lives in the record of the slice that found it; triage, promotion and removal edit that record. Collecting them back into the spec would reintroduce the shared list.
- **History is the record.** A merged record is the slice's history, so there is no brief to move; the archive rule applies to the spec's older entries only.
- **Versioning.** Minor bump: a new spec layout rule.

Decisions setting: ask (default).
Effort assumed: high.
Verifier effort: high (no override at any scope).
Checks: as in R7. No end-to-end suite; CI's `checks` job is the required check.
Branch: slice-records, from main (208dad6).

## Evidence

- R4 fixture (scratchpad `fx`, merge setup stubbed to an organization repo with a queue): a PR-only `changes` job (`if: github.event_name != 'push' && ...`) read by `e2e` gave no push-skip FAIL and showed the "no repeat-run skip" WARN; `retries: 1 // see #1234` gave no finding; `jest.setup.ts` `retryTimes(2` reported once; `pytest --reruns 3` in a workflow reported; an unquoted `FREEZE_DATE: 2026-01-01` parsed under `/usr/bin/python3 -I` (Ruby).
- R4 non-admin: a checkout pointing at cli/cli (not an admin) reports "repository settings unknown", not "no protection".
- Fix round 1: a commented-out `// jest.retryTimes(4)` and `# run: pytest --reruns 3` give no finding while the live lines are still read (fixture `fx2`: 0 FAIL).
- R7 regression: rv-rez 1 FAIL 1 WARN, crelaunch 1 FAIL 3 WARN, bosun 1 FAIL 2 WARN, the same under PyYAML and Ruby as before this slice.

## Verify

- 1st (53271be, fingerprint 42764c5), bosun-verifier claude-opus-5-5 / high: FAIL. R2 unmet: bosun-verify still wrote the next brief into the spec; bosun-ci still wrote deferred candidates into the spec's follow-ups; triage's active-slice check stopped on any lane's open record. Follow-ups, fixed in the same round: "only statuses and lessons" left no room for decisions, drafts and blocked steps; commented-out retry lines were read; statuses for a brief's own done-conditions had no home; the implemented per-slice-records deferral still open; pointer dates; README records-ride-along copy; verifier agents and triage spec-health still named the spec section.
- 2nd (50045fb, fingerprint 2d9a9a8), bosun-verifier claude-opus-5-5 / high: PASS WITH FOLLOW-UPS. All ten round-1 findings resolved except two lane-facing copies (core "Branches and the spec", the lane template) still listing only statuses and lessons; the fingerprint excluding only the spec while bookkeeping now goes in the record; README's status rule and follow-ups bullet; the verify description. Fixed in round 2, with the fingerprint now excluding the record too.
- 3rd (7812598, fingerprint 063338d), bosun-verifier claude-opus-5-5 / high: PASS WITH FOLLOW-UPS. All round-2 findings resolved; two drifts recorded below; a README nit (evidence now lives in slice records) fixed without a further verify.

## Follow-ups

- slice-records, 2026-11-23, drift: `skills/bosun-brief/SKILL.md` "Until blocked" lists records riding along as "(spec, docs, design boards)" without core's "slice records"; add it in the next slice that touches the brief.
- slice-records, 2026-11-23, drift: the lane template's "Spec:" line closes core's open list of spec-level entries and leaves out human-checks (core, "Follow-ups and milestones"); reword it to defer to "Slice records" in the next slice that touches the lane template.

Log: 2026-11-23, slice-records, opus (implemented by lead), first verify FAIL (kinds: skills still writing per-slice content into the spec; a check reinterpreted so it stalls a milestone step), second PASS WITH FOLLOW-UPS (lane-facing copies missing the new carve-out; a fingerprint not excluding the new bookkeeping file), third PASS WITH FOLLOW-UPS (two drifts recorded); all bosun-verifier on claude-opus-5-5 / high; R1–R7 verified; route-or-screen done-conditions: 0 of 0.
