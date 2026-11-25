# Findings to checks (2026-11-25)

Status: in progress
Mode: opus (Opus 5.5 leads and implements).

## Decisions

From a read-only review of four weeks of verify findings in RigRez and crelaunch (2026-10-28 to 2026-11-25), the lead recommended dropping risk-tiered verification and building these changes instead:
- **Risk tiers dropped.** Only 0–6% of slices were low risk by path. In RigRez, 200 of 257 high-risk slices were high only for carrying a migration. Medium-risk slices still failed first verify 29–41% of the time.
- **Red checks were the top finding.** About 25 RigRez slices and 10 crelaunch slices failed first verify on an existing repo check left red, such as a catalogue list, generated types or derived config.
- **Triage step 7 never fired.** RigRez triage ran on 2026-11-24 without it, because `Log:` lines only began around 2026-11-23.

Michael asked whether the project-specific checks could be generalized and whether they could cause harm later ("Just be honest with me"). The lead answered that the habit generalizes and the specific checks belong in each project. It also named the harms: CI cost, agents working around checks, noise on existing code, stale checks, and tests that are rightly green on the old code.

Michael said "Yes, I'd like to fold all three in": a check considered at each FAIL fix, triage reading the records' verify sections, and a weekly schedule. Then, to the full breakdown: "Yes, start building and send them to the hubs". The project checks went to the RigRez and crelaunch hubs as draft done-conditions.

## Brief

Outcome: A slice can't reach the verifier with an existing repository check red. Each fixed verify FAIL is turned into a check where a small one would have caught it. Triage, by hand or on a weekly schedule, reads the real verify findings and proposes checks for repeated kinds. New checks follow rules that keep them cheap, honest and removable.

Size: about 150–250 changed lines, all prompt text and docs, under the cap.

Done-conditions:
C1. **Pre-verify gate.**
- `rules/core.md` "Self-check" names the gate: the full unit suite, typecheck, lint, the repository's consistency and catalogue tests (database ones included), and checks that generated or derived files are current.
- These run on the slice's commit before the first verify, whatever the change touched. The spec may list them on a `Pre-verify gate:` line.
- `skills/bosun-verify/SKILL.md` refuses to launch the first run until each gate command has a reported exit 0 on the current fingerprint. It recomputes the fingerprint to compare.
- A red gate is the lead's to fix, and it is not a verify run.
- "Tests and CI" no longer contradicts the gate.

C2. **A check for each fixed FAIL.**
- `rules/core.md` "Corrections become checks" covers verify FAILs as well as the user's corrections. When the lead fixes a FAIL, it asks whether a mechanical check would have caught it.
- A small check (a test or lint rule within the slice's own area) goes into the fix. A bigger one becomes a draft done-condition.
- A FAIL that an existing check would have caught had it run needs no new check; the gate covers it.
- For a bug fix, the new test is shown failing on the pre-fix code once, and that result goes in the evidence.
- `bosun-verify`'s FAIL step points to this.

C3. **Rules for new checks,** in `rules/core.md`:
- a new check states its CI time cost;
- a check that lands on existing code covers new and changed code only, unless the user asks for a full sweep;
- each check added under this rule names the finding kind and date it came from, in a comment;
- a new lint suppression, skipped test or disabled check needs a stated reason, and both verifier agents report one without a reason as a finding (PASS WITH FOLLOW-UPS, `drift`).

C4. **Triage reads real data.**
- `skills/bosun-triage/SKILL.md` step 7 reads the FAIL findings in the slice records' verify sections, not only `Log:` lines. It counts kinds by slice and proposes a candidate check for each repeated kind as a draft done-condition.
- For each candidate, it notes whether a check already exists, and the check's rough cost.
- Every two months it lists the checks added under C2 and C3 that are older than two months, for the user to keep or retire. It never removes one itself.
- The README's "Corrections become checks" text matches.

C5. **Weekly triage task.**
- `templates/weekly-checks-triage.md` is the saved prompt for a Claude Code cloud scheduled task, run weekly on one repository. It runs only triage step 7 and the C4 two-month listing.
- It writes the lesson update and the draft done-conditions on a records branch and opens one PR. It arms auto-merge only when the spec says `Decisions: take recommendations`.
- It writes nothing when nothing changed, and never edits code, tests or configuration.
- `skills/bosun-ci/SKILL.md` gains a "Weekly checks triage (opt-in)" section like "PR watcher (opt-in)": the user's go, the first-run confirmation of `gh` access, and the limits.

C6. **General checks to suggest.** `skills/bosun-ci/SKILL.md`'s audit suggests, when a project's stack fits and the project has not declined them:
- a second unit-test run in a far time zone, limited to date-handling files;
- a lint against super-linear regexes;
- the bug-fix failing-first practice from C2 as a lead step, never a CI gate.

C7. **Records.** README paragraphs and the table row for the new template. Version 0.36.0 in both manifests and the README version line. A SPEC.md decision entry for this slice, with the risk-tiers drop.

C8. **Checks pass:**
- `bash -n scripts/*.sh`;
- JSON parses for both manifests and `hooks/hooks.json`;
- `python3 -m py_compile scripts/*.py`;
- `python3 scripts/ci-conformance.py --help` exits 0.

Out of scope:
- risk-tiered verification;
- the project checks themselves (sent to the hubs);
- setting up the weekly task or the PR watcher on any repository;
- delta re-check effort rules.

Assumptions:
- Weekly triage opens a records PR rather than commenting on an issue, because the lesson and drafts belong in the spec, and a PR is how the user approves a records change outside a run.
- "Small" check means one test or lint rule inside the files the slice already touches.

Decisions: ask (Bosun's spec has no `Decisions:` line).
Effort assumed: the session's level.
Verifier effort: high (no override at any scope).
Checks: as C8. Pre-verify gate: C8's commands (Bosun has no test suite; its gate is these static checks).
Branch: findings-to-checks

## Verify runs

Run 1 (2026-11-25, bosun-verifier claude-opus-5-5/high, HEAD b9e559d, fingerprint 1d8ca083): FAIL.
- F1 (blocking): `/bosun-verify` step 0 stopped for good when a repository has no gate-type checks, or when verifying without a spec or brief. Fixed: `Pre-verify gate: none`, and with no spec or brief the gate is the repository's own checks, possibly none.
- F2: the weekly window was the shorter of "since last run" and four weeks, and the commit message it keys on was never set. Fixed: it now takes whichever reaches further back, the two-month read is used only for dropping quiet kinds, and the commit message is set.
- F3: checks due with no spec change could force an empty commit; the template merged the default branch into an open PR every week; and it never said how to find the earlier PR. Fixed: due checks go to the standing issue in such a week; the merge happens only when that PR conflicts; the earlier PR is found by its `checks-triage/` branch prefix.
- F4: step 8 re-listed kept checks at every triage. Fixed: a check is listed once, when it turns two months old.
- F5: a check added while fixing a FAIL could be flagged as an extra test. Fixed: an exception in core's "Commit tests only…" and in both verifier agents, and the verify prompt names such checks.
- F6: the README copy dropped clauses (disabled check, evidence and exemption, date). Fixed.
- Nit: the bosun-ci audit deliverables didn't name the defect checks. Fixed.
- Pre-existing: the verifier's loaded definition predated the regenerated one (agents load at session start). This is not a slice defect.
