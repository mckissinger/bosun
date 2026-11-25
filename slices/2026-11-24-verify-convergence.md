# Verify convergence (2026-11-24)

Status: in progress
Mode: opus (Opus 5.5 leads and implements).
Decisions: Michael asked why verification takes so long and runs so many rounds in rv-rez and crelaunch ("Do you think it's normal? Do you think there are improvements that could be made?"). The lead analysed 4,423 verifier and security-review runs and 120 classified reports, and read current practice, including Anthropic's Oct 15 code-review post. It then recommended seven changes to Bosun's verification. Asked "So then, what are all the changes that you recommend we make?", the lead listed them as items 1–7 of its list. Michael: "Proceed."

## Brief

Outcome: Verify rounds after the first check only what the fix changed, and a passing slice no longer pays a full verify round for each follow-up. Rounds per slice fall from about 2–2.5 toward Anthropic's published 1.3, while the fresh verifier, the three-run cap and the security review stay.

Done-conditions:
V1. `todo` (after the first verify: a findings ledger across runs, new findings numbered after it, a rerun because a check could not run repeats that run, and a later PR fix starts with a delta re-check) `rules/core.md` "Finishing" defines the delta re-check:
- Every verify run after a slice's first is a delta re-check.
- The lead commits the slice's work before each verify run, so the fix diff is `git diff <commit the previous run checked>`.
- The re-check gets the previous run's numbered findings, that diff, and the checks rerun for the fix.
- It confirms each previous finding resolved or not, with evidence.
- It reviews the fix diff and the code that diff changes or calls.
- It never reports a finding that an earlier run already reported.
- It reports a new finding on slice code the fix did not change only when that finding is release-blocking.
- The verify limit counts delta re-checks as runs, as before.
V2. `todo` `rules/core.md` and `skills/bosun-verify/SKILL.md` change what follows PASS WITH FOLLOW-UPS:
- A reachable bug or security issue in the slice's own work is fixed and gets a delta re-check.
- Drift, records, wording and evidence that was still pending (a check that hadn't finished) are fixed or confirmed by the lead, who reruns the checks the fix could change, with no verify run.
- The third-run rule is unchanged.
- "Follow-ups and milestones" stays consistent with this.
V3. `todo` Pre-existing defects, in `rules/core.md` "What blocks" and both verifier agents:
- A defect on lines the slice did not change, which the slice also does not make reachable or worse, is reported under its own Pre-existing heading.
- It never changes the verdict.
- It becomes a `bug` follow-up, and a release-blocking one is named to the user in the report.
V4. `todo` Both verifier agents name the pattern when a finding is one instance of a repeated mistake, and list every instance in the slice's diff, found by searching.
V5. `todo` The self-check before the first verify:
- `rules/core.md` "Finishing" requires the lead, after the last edit, to commit the slice's work and then run the brief's checks on that commit: typecheck, lint, build, and the tests the change could affect.
- It also requires the full unit suite when "Tests and CI" calls for it, the full database suite when the change touches the schema, migrations or database functions, and the repository's consistency tests.
- The lead reports each result on the fingerprint taken after the commit.
- Both verifier agents' step 3 says: a whole-repository check or full suite the prompt reports passing on a matching fingerprint is not rerun, and the verifier says so. It runs every other check it is asked to run, and always runs the existing tests for the changed files and for the flows the done-conditions name.
- Changed after the first verify: commit before the checks, because the fingerprint includes HEAD; and the database-suite trigger, so the self-check agrees with "Tests and CI".
V6. `todo` `skills/bosun-verify/SKILL.md` effort and prompt:
- A delta re-check runs at `medium`, or at the resolved effort when that is lower.
- It keeps the resolved effort when the slice touches money, authentication or permissions, migrations, or security-sensitive code.
- This replaces "carry the resolved effort through FAIL retries", and the effort is recorded per run as before.
- The prompt list adds what a delta re-check needs: the previous run's numbered findings, the commit it checked, the fix-diff command, and the checks rerun.
V7. `todo` Copies match:
- The `bosun-brief` copies of the verify loop (step 7, the "Until blocked" stop list, the lane template) and README's "Verification" paragraph carry V1–V6 where they restate them.
- Nothing contradicts the fresh verifier, the three-run cap, the security review, or "Recurring verify failures".
- The version is 0.33.0 in both manifests and the README version line.
V8. `todo` Checks pass:
- `bash -n scripts/*.sh`
- JSON parses for both manifests and `hooks/hooks.json`
- `python3 -m py_compile scripts/*.py`
- `claude plugin validate .`
- `python3 scripts/configure-claude-agents.py --project <tmp> --verifier-effort high` regenerates both agents with the new text
- `git diff origin/main --check`
- the project-name grep over added lines finds nothing

Out of scope:
- Changing the verifier's model, or splitting the verifier into several reviewers.
- A cross-family (Gemini) second reviewer.
- The `ci-conformance.py` follow-ups.
- crelaunch's first-pass FAIL rate, which is that project's to investigate.
- Rolling the change out to running sessions; they pick it up on restart.

Assumptions:
- **No CI-before-verify gate.** Bosun verifies before pushing and forbids pushing to find out whether tests pass. The self-check is therefore the lead's full local run, not green CI on a pushed head.
- **Commit before each verify.** A delta re-check needs a fixed point to diff against. Committing early changes nothing else, because step 9 still commits the records and pushes afterwards.
- **Medium for delta re-checks.** A re-check reads a small diff against a list of findings, which needs less reasoning than a first pass. Risky areas keep full effort, because the evidence shows cheaper review missing security bugs.
- **Skipping reruns is safe.** The fingerprint proves the tree is the one the checks ran on, and CI reruns every required check before merge.
- **Versioning.** A minor bump, because the verify loop's behavior changes.

Decisions setting: ask (default).
Effort assumed: high.
Verifier effort: high (no override at any scope).
Checks: as in V8. There is no end-to-end suite; CI's `checks` job is the required check.
Branch: verify-convergence, from main (3f0c3ff).

## Evidence

- The analysis: Bosun-verifier runs grouped by slice ID in each run's description.
  - Extra rounds after PASS WITH FOLLOW-UPS rose from 0.16 per slice (rv-rez) and 0.22 (crelaunch) in Oct 1–24 to 0.49 and 0.71 in Nov 8–24, following 0.15.0 (Oct 25), which added fix-then-re-verify for follow-ups.
  - About 35% of a verifier's time goes to re-running suites the implementer already ran (unit and DB tests 14%, waiting 8%, typecheck and lint 7%, end-to-end 4%).
  - Of 60 re-verified PASS WITH FOLLOW-UPS reports, 31 had no bug or security finding.
  - 15% of FAIL findings could have been caught by a machine check, for example a suite left red.
- Anthropic, "How the Claude Code team does code review" (Oct 15), checked by fetching it: mean reviews-to-pass fell from 2.08 to 1.32 after diff-only re-review, no repeated findings, and flagging bug classes.

- V8: all pass.
  - `bash -n`, the three JSON files and `py_compile` pass.
  - `claude plugin validate .` reports "Validation passed".
  - `configure-claude-agents.py --project <tmp git repo> --verifier-effort high` regenerates both agents at `effort: high`, each with 7 lines carrying the delta re-check, pre-existing and pattern rules.
  - `git diff --check` is clean and the project-name grep is clean.
- Stale-wording grep over rules, skills, agents, README, CONTRIBUTING and scripts finds no remaining copy of the old wording ("same resolved verifier effort", "re-verify", "Typecheck, lint, build, and unit tests always run").

## Verify

## Follow-ups
