# Bosun spec archive

### Opus modes slice (2026-09-22, verified)

Status: verified 2026-09-22, bosun_verifier PASS; completes the uncommitted September 18 slice. Live Claude agent execution remains untested.
Outcome: Add fable-opus (Fable leads/verifies, native Opus 5.5 worker implements) and opus (Opus 5.5 leads, implements, scouts, and verifies), preserving independent Claude verifier effort controls.
Done-conditions: O1–O6 below.
Out of scope: changing Sol/Luna routing; selectable Astra verifier effort; paid benchmarks; publishing/installing globally; unrelated follow-ups.
Assumptions: retain the unfinished fable-opus name, add opus; both run in Claude Code. Opus worker stays at high. Verifier effort precedence remains invocation, current slice, project default, high. Existing user-owned definitions are not overwritten. Session model must actually match the selected mode; spec edits do not change the running model.
Effort assumed: inherited session setting (not exposed); no picker change.
Checks: python3 scripts/configure-claude-agents.py --help; temporary-project generation across modes/efforts, transitions, invalid inputs and collision/symlink refusal; JSON/TOML/frontmatter parsing; bash -n scripts/*.sh codex/scripts/*.sh; claude plugin validate .; git diff --check; independent bosun_verifier review. Live Opus execution is separate from static configuration validation.
Branch: codex/fable-opus-verifier-effort, existing uncommitted work based on main (98d6025); preserve and complete that work.

O1. `verified 2026-09-22 bosun_verifier PASS` Six-mode tables, selection and host gates recognize fable-opus and opus. Default/legacy modes retain their meaning; Codex redirects both new modes to Claude Code.
O2. `verified 2026-09-22 bosun_verifier PASS` fable-opus pins the worker to Opus 5.5/high, with Fable lead/verifier, no nested delegation, spec edits, or commits by the worker; same-worker retries and evidence rules remain intact.
O3. `verified 2026-09-22 bosun_verifier PASS` opus uses Opus 5.5 for lead, direct implementation, scout, and both verifier variants; verifies in a fresh context; gates execution on the actual lead model and restores Fable agents when switching back.
O4. `verified 2026-09-22 bosun_verifier PASS` Claude verifier effort remains independently configurable; generator validates before writing, preserves tools/MCP, handles spaces, is idempotent, refuses symlinks/unrelated files, and does not change worker effort when verifier effort changes.
O5. `verified 2026-09-22 bosun_verifier PASS` Docs explain usage, host/model/reload requirements and validation limits; README and manifests consistently use 0.8.0 for the completed unpublished slice.
O6. `verified 2026-09-22 bosun_verifier PASS; live spawns untested` Static checks and independent review pass; live model verification limits are explicitly recorded without equating generated configuration to a successful spawn.

### Core rules rename slice (2026-09-25, verified)

Name: core-rules-rename (2026-09-25). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS 2026-09-25.
Outcome: Shared files are named for their role, not a model: the two core rules files become `rules/core.md` and `codex/rules/core.md`, and shared prose says "the lead" wherever it means whichever model is leading.
Done-conditions:
R1. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS` `rules/fable.md` is renamed (git mv) to `rules/core.md` with first heading `# Bosun core rules (Claude Code)`, and `codex/rules/astra.md` to `codex/rules/core.md` with `# Bosun core rules (Codex)`. The old paths no longer exist.
R2. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS` `scripts/session-start.sh` prints `rules/core.md` unless `~/.claude/CLAUDE.md` has a line `# Bosun core rules (Claude Code)`; `codex/scripts/session-start.sh` prints `codex/rules/core.md` unless `~/.codex/AGENTS.md` has `# Bosun core rules (Codex)`. Checked by running each hook with a temporary HOME, with and without the heading.
R3. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS` Outside SPEC.md history, no file names `rules/fable.md`, `codex/rules/astra.md`, `rules/astra.md`, `# Fable 5.1 agentic development`, or `# Astra agentic development` (grep), except the README sentence telling users who appended the old file how to migrate.
R4. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS` In both core rules files, the shared (not mode-specific) parts of `bosun-brief`, `bosun-verify`, and `bosun-mode` in both plugins, and README, "Fable" or "Astra" that means whichever model is leading reads "the lead". Model names remain only for mode names, model-specific agents (`bosun-worker-opus`), mode-specific sections, and facts about a specific model. The line "References to Fable in the shared rules below mean the selected Claude lead" is removed.
R5. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS` The spec records the user's decision superseding the 2026-09-04 naming rule, the Naming design paragraph matches, and a note says older entries refer to the old rules paths.
R6. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS` Version 0.9.0 in all three manifests and the README version line; manifests parse.
R7. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS` Checks pass: `bash -n scripts/*.sh codex/scripts/*.sh`; JSON parse of the three manifests and `hooks/hooks.json`, `codex/hooks/hooks.json`; `claude plugin validate .`; `git diff --check`.
Out of scope: the Tests and CI rules and `bosun-ci` changes (next slice); renaming mode values, agents, or the working directories; rewriting historical spec entries; fixing unrelated follow-ups.
Assumptions: "Fable"/"Astra" in the fable-crew, fable-opus, and Astra-mode sections stays where it names the model that holds that role in that mode. The minor version bump is because users who appended the old rules heading to their global file must re-append under the new heading. The user's global CLAUDE.md stale copy was removed by the user's approval on 2026-09-25 before this slice, so nothing on this machine still carries the old heading.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in R7, plus the R2 hook runs and the R3 grep.
Branch: rename-core-rules, from main (574003a); carries the uncommitted mode-line change astra -> opus.

### Tests and CI standard slice (2026-09-25, verified)

Name: tests-ci-standard (2026-09-25). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS WITH FOLLOW-UPS 2026-09-25. Stacked on rename-core-rules (PR #13, unmerged).
Outcome: Every Bosun role follows the same test and CI rules, and `bosun-ci` treats Blacksmith as the runner standard and carries the lessons from Linear's CI rework.
Done-conditions:
T1. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS on second verify` Both core rules files have a "Tests and CI" paragraph in "While working" stating: run the tests for what you touched before handoff or push, the full suite only for shared code, configuration, dependencies, or test setup, and never push to find out whether tests pass; never weaken, skip, or delete a test to make a change pass, and say so when a specified behavior change requires a test change; new tests make no real network calls, use no real sleeps or wall-clock time, and do not depend on order or leak global state; follow the repo's written test and CI conventions; a failure that passes on rerun with no change and unrelated to the change is a flake candidate, reported with name and message, never fixed with retries or longer sleeps, quarantined only with the user's approval; a workflow change states whether it adds or removes CI time and does not undo existing optimizations. Because every crew-mode worker prompt already includes the core rules' "While working" rules (`skills/bosun-brief` fable-crew and fable-opus step 1, `codex/skills/bosun-brief` astra-crew step 1), those prompts carry it with no template change.
T2. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS on second verify` `agents/bosun-worker-opus.md` and the four `codex/agents/bosun-worker-*.toml` carry the same rules as one compact bullet.
T3. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS on second verify` `agents/bosun-verifier.md`, `agents/bosun-verifier-mobile.md`, `codex/agents/bosun-verifier.toml`, and `codex/agents/bosun-verifier-mobile.toml` treat as findings: an existing test weakened, skipped, or deleted without a done-condition that changes that behavior and a report that says so; a new test with real network calls, real sleeps, or wall-clock or order dependence; a CI workflow change whose report does not state its CI-time effect.
T4. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS on second verify` Both `bosun-ci` skills: a "Runner standard" section makes Blacksmith the standard (GitHub-hosted runners are a finding; per-job sizing; org and Default runner group requirement, personal repos excluded; check current Blacksmith docs for labels and cache actions; after a migration, measure checkout time and look for hung or retried checkouts). The line keeping provider migrations and paid runner upgrades out of scope is replaced: migration is recommended, and implemented only when the user asked for it.
T5. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS on second verify` Both `bosun-ci` skills' "Choose a change": critical-path gate jobs rank first; candidates for gate-job fetch and checkout trimming, repeated setup (base image, filtered installs, schema snapshot, cache vs fresh install), batching small checks with per-task output, native typecheck and type-free lint rules, sharding only after setup is short with the setup-times-shards arithmetic and file splitting, per-file isolation opt-in with teardown and an isolated project for risky files, and affected-only tests with a full-run fallback.
T6. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS on second verify` Both `bosun-ci` skills' implementation done-conditions add: an optimization that constrains how code or tests are written is recorded where the project's agents read it (its CLAUDE.md or AGENTS.md, or the spec's lessons). References gain Linear's article and Blacksmith's docs.
T7. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS on second verify` `skills/bosun-brief/SKILL.md` step 6 says to follow the scope and edit rules in the core rules, not "the global CLAUDE.md" (follow-up from core-rules-rename, folded in because this slice edits those rules).
T8. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS on second verify` Version 0.10.0 in all three manifests and the README version line; checks pass: `bash -n scripts/*.sh codex/scripts/*.sh`; JSON parses; TOML parses (python3.12 tomllib) for every `codex/agents/*.toml`; `claude plugin validate .` and `codex`; `git diff --check`; `python3 scripts/configure-claude-agents.py` into a temp project regenerates verifiers containing the new rule.
Out of scope: Blacksmith Testbox (follow-up); migrating any project's CI; changes to fable-crew routing, verifier effort, or mode behavior; README beyond the version line, the core-rules row contents, and the bosun-ci scope sentence T4 contradicts.
Assumptions: the rules are Bosun-wide defaults; a project's own written conventions win where they differ, which is what "follow the repo's written conventions" means. The verifier runs before the PR exists and, in lead-implements modes, before any report, so both `bosun-verify` skills now pass it the implementer's test and CI statements (added after the first verify FAILed and found the gap). Blacksmith label examples are illustrative and the skill says to confirm against current docs.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in T8.
Branch: tests-ci-standard, stacked on rename-core-rules.

### CI research guidance slice (2026-10-07, verified)

Name: ci-research-guidance (2026-10-07). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS 2026-10-07 (first verify PASS WITH FOLLOW-UPS; its three wording follow-ups fixed in-slice at the user's request, then re-verified PASS).
Outcome: `bosun-ci` and the verifiers carry what the 2026-10-07 CI research changed: selection must not let misses land under auto-merge, identical-input skipping is a coverage-preserving candidate, and agent-written test bloat is a verifier finding.
Done-conditions:
C1. `verified 2026-10-07 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS, PASS on re-verify after wording fixes; skills/bosun-ci/SKILL.md:57, codex/skills/bosun-ci/SKILL.md:57` Both `bosun-ci` skills' change-based selection candidate says that when PRs merge automatically on green, a scheduled or post-merge full run finds a selection miss only after it lands, so anything the PR run skips still runs in a required check before merge (for example the full suite in a merge queue), and that on the PR run end-to-end tests stay full or path-gated because the import graph cannot select them.
C2. `verified 2026-10-07 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS, PASS on re-verify after wording fixes; skills/bosun-ci/SKILL.md:48, codex/skills/bosun-ci/SKILL.md:48` Both `bosun-ci` skills' "Choose a change" list has an identical-input candidate: skip a task whose inputs match a run that already passed, through a task or remote cache keyed on those inputs, with a caution that the key must cover every input the task reads, and that tasks reaching live services, reading the clock, or showing flakes stay uncached.
C3. `verified 2026-10-07 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS, PASS on re-verify after wording fixes; agents/bosun-verifier.md:23, agents/bosun-verifier-mobile.md:25, codex/agents/bosun-verifier.toml:16, codex/agents/bosun-verifier-mobile.toml:16` `agents/bosun-verifier.md`, `agents/bosun-verifier-mobile.md`, `codex/agents/bosun-verifier.toml`, and `codex/agents/bosun-verifier-mobile.toml` treat as a Tests and CI finding a new test that asserts the code's internal structure instead of a stated behavior (a boundary call is fine when it is the stated behavior), or checks a behavior an existing test already checks.
C4. `verified 2026-10-07 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS, PASS on re-verify after wording fixes; SPEC.md Follow-ups, two ci-research lines` The two ci-research deferrals (two-tier CI, scheduled `bosun-ci` runs) are in Follow-ups.
C5. `verified 2026-10-07 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS, PASS on re-verify after wording fixes; manifests and README:221 at 0.10.1; all C5 checks exit 0; regenerated verifiers carry the finding` Version 0.10.1 in all three manifests and the README version line; checks pass: `bash -n scripts/*.sh codex/scripts/*.sh`; JSON parses; TOML parses (python3.12 tomllib) for every `codex/agents/*.toml`; `claude plugin validate .`; `git diff --check`; the two `bosun-ci` skills' "Choose a change" sections are identical; `python3 scripts/configure-claude-agents.py` into a temp project regenerates verifiers containing the new finding.
Out of scope: the core rules' Tests and CI paragraph (user: the July-August targeted-test lessons are not a reason to change it); two-tier CI implementation and scheduled audits (deferred, C4); worker definitions; README beyond the version line; other follow-ups.
Assumptions: patch bump because the changes add guidance without changing any interface. The auto-merge sentence is conditional, since not every project auto-merges. No new reference links: the skill already says to consult current docs, and no Turborepo page was verified this session.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in C5.
Branch: ci-research-followups, from main (2750b37); carries the C4 follow-up lines.

### E2E cadence slice (2026-10-16, verified)

Name: e2e-cadence (2026-10-16). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS WITH FOLLOW-UPS 2026-10-16 (first verify FAIL: the fingerprint missed quoted untracked names, external diff tools, and subdirectory runs; the worker default and the verifier's shell allowance did not match; all fixed).
Decisions (user, 2026-10-16): "see if we're running the local E2E suite, the full suite, too often ... I don't want to do a bunch of unnecessary EDE if we don't have to." On the lead's assessment (the full suite ran three to six times per slice in cre-list, through the implementer, the verifier, every fix loop, and "No regression" done-conditions, while CI's required e2e check already runs it before auto-merge) and its four rule changes, with Blacksmith Testbox piloted later rather than built in: "Okay, let's proceed with your plan."
Outcome: Bosun runs end-to-end tests targeted during a slice and the full end-to-end suite at most once, which is CI's required check when the project has one; the verifier skips reruns on a tree the implementer already ran green, and a fix reruns only the checks it could affect.
Done-conditions:
E1. `verified 2026-10-16 bosun-verifier (claude-opus-5-5/high), first verify FAIL, second PASS WITH FOLLOW-UPS; rules/core.md:69, codex/rules/core.md:64` Both core rules files' "Tests and CI" paragraph says: end-to-end (browser or UI) tests run targeted, the specs for the routes and flows the change touches plus the specs the done-conditions name; after a fix, the failed specs rerun first (for example Playwright's `--last-failed`), then the targeted set; the full end-to-end suite runs at most once per slice: when a required CI check runs it before merge, that check is the full run and it is not run locally, and otherwise it runs once after the last code change; no done-condition requires a full local end-to-end run; after a fix, rerun only the checks the fix could change, so a fix to comments or documentation reruns typecheck and lint only. The paragraph is identical in both files.
E2. `verified 2026-10-16 bosun-verifier (claude-opus-5-5/high), first verify FAIL, second PASS WITH FOLLOW-UPS; agents/bosun-worker-opus.md:26, codex/agents/bosun-worker-*.toml:14` `agents/bosun-worker-opus.md` and the four `codex/agents/bosun-worker-*.toml` carry the same end-to-end rule in their Tests and CI bullet, identical across the five files.
E3. `verified 2026-10-16 bosun-verifier (claude-opus-5-5/high), first verify FAIL, second PASS WITH FOLLOW-UPS; skills/bosun-verify/SKILL.md:28,38, codex/skills/bosun-verify/SKILL.md:17,25` Both `bosun-verify` skills: the verifier prompt carries the implementer's check results (command, exit code) for checks run after the last edit, with the working-tree fingerprint they ran on and the exact fingerprint command; on FAIL, the fix reruns only the checks it could change, and the re-verify prompt names the files the fix changed and the checks rerun for them. The fingerprint command is read-only, runs from the repo root in bash, leaves out the spec file, and changes when any other tracked or untracked file changes, including untracked names git quotes and with an external diff tool configured.
E4. `verified 2026-10-16 bosun-verifier (claude-opus-5-5/high), first verify FAIL, second PASS WITH FOLLOW-UPS; agents/bosun-verifier.md:17,28, agents/bosun-verifier-mobile.md:19,30, codex/agents/bosun-verifier*.toml:10,21` `agents/bosun-verifier.md`, `agents/bosun-verifier-mobile.md`, `codex/agents/bosun-verifier.toml`, and `codex/agents/bosun-verifier-mobile.toml`: step 3 always runs typecheck, lint, build, and unit tests; for end-to-end or UI tests it runs the specs the done-conditions name and the route-or-screen re-checks, skips other end-to-end specs the prompt reports green on a fingerprint matching its own, runs the ones the prompt names as affected when the fingerprint differs, and never runs the full end-to-end suite when the prompt says a required CI check runs it.
E5. `verified 2026-10-16 bosun-verifier (claude-opus-5-5/high), first verify FAIL, second PASS WITH FOLLOW-UPS; skills/bosun-brief/SKILL.md:49, codex/skills/bosun-brief/SKILL.md:41` Both `bosun-brief` skills' brief template `Checks:` line says end-to-end checks name the targeted specs, not the full suite, and says whether a required CI check runs the full end-to-end suite.
E6. `verified 2026-10-16 bosun-verifier (claude-opus-5-5/high), first verify FAIL, second PASS WITH FOLLOW-UPS; manifests and README:231 at 0.13.0; all E6 checks exit 0; fingerprint temp-repo matrix` Version 0.13.0 in all three manifests and the README version line; checks pass: `bash -n scripts/*.sh codex/scripts/*.sh`; JSON parses; TOML parses (python3.12 tomllib) for every `codex/agents/*.toml`; `claude plugin validate .`; `git diff main --check`; the E1 and E2 identity checks; `python3 scripts/configure-claude-agents.py` into a temp project regenerates verifiers containing the E4 rule; the fingerprint command, in a temp repo, prints the same id twice on an unchanged tree and from a subdirectory, a different id after a tracked file, an untracked file, or an untracked `café.txt` changes (also under `GIT_EXTERNAL_DIFF=true`), the same id after a spec edit, and writes no objects.
Out of scope: Blacksmith Testbox (piloted by hand on cre-list first; follow-up); any project's CI or spec (cre-list's "No regression" conditions and Checks lines change when its next slices are briefed); `bosun-ci` selection guidance; test-impact tooling; README beyond the version line.
Assumptions: "required CI check runs the full suite" is judged from the repo's workflows and branch protection, and the brief states it; a project without one still gets exactly one full local run. Typecheck, lint, build, and unit tests stay unconditional in the verifier because they are cheap and are its independent evidence; the skip applies only to end-to-end specs. The fingerprint is a hash of HEAD, `git diff HEAD --binary`, and each untracked non-ignored file's name and blob hash, computed without writing objects. Minor version bump for a rule change.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in E6.
Branch: e2e-cadence, from main (8194f09).

### Agents gitignore slice (2026-10-19, verified)

Name: agents-gitignore (2026-10-19). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS WITH FOLLOW-UPS 2026-10-19.
Decisions (user, 2026-10-18): on the lead's recommendation to stop tracking Bosun-generated agent files in the seven projects that committed them and to make Bosun add the ignore itself: "Yes".
Outcome: `scripts/configure-claude-agents.py` keeps the agent files it generates out of git, so a plugin update never shows as a diff in a project.
Done-conditions:
A1. `verified 2026-10-19 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS; scripts/configure-claude-agents.py:16-17,56-59,69-70` When it writes agents (not on `--dry-run`), the script writes `.claude/agents/.gitignore` containing the Bosun marker comment, `bosun-*.md`, and `.gitignore` (so the ignore file itself stays untracked), creating it when absent and rewriting it only when it carries the marker; an existing `.gitignore` there without the marker is left unchanged and the script prints that it was left alone. It refuses a symlinked `.gitignore` like it refuses symlinked agents.
A2. `verified 2026-10-19 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS; scripts/configure-claude-agents.py:71-79` When git still tracks any generated `bosun-*.md` in the project, the script prints a note naming them and the `git rm --cached` command; it never runs git commands that change state.
A3. `verified 2026-10-19 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS; README.md:168` README's agent-setup sentence (line 168) says the generated files are git-ignored through `.claude/agents/.gitignore`.
A4. `verified 2026-10-19 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS; manifests and README:231 at 0.13.1; all A4 checks exit 0; 7-case lead matrix plus 15 verifier cases` Version 0.13.1 in all three manifests and the README version line. Checks pass: `bash -n scripts/*.sh codex/scripts/*.sh`; JSON parses; `claude plugin validate .`; `git diff main --check`; `python3 -m py_compile scripts/configure-claude-agents.py`; temp-repo runs show: a fresh repo gets the agents and the ignore file and `git status --porcelain` lists nothing under `.claude/`; a second run changes nothing; `--dry-run` writes nothing; a user-owned `.claude/agents/.gitignore` is left byte-identical with the printed note; a repo that tracks `bosun-verifier.md` gets the A2 note; a symlinked ignore file is refused before any write.
Out of scope: Codex agent files (`$bosun-mode` installs those; no project tracks them); changing which agents are generated; the projects' own `.gitignore` files (handled by their seven PRs on 2026-10-19).
Assumptions: a nested `.gitignore` is used instead of editing the project's root `.gitignore` so the script never modifies a tracked project file. Patch bump because no interface changes.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in A4.
Branch: agents-gitignore, from main (7e0b5fa).

### Parallel lanes slice (2026-10-20, verified; removed 2026-10-26 by remove-lanes)

Name: parallel-lanes (2026-10-20). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS WITH FOLLOW-UPS 2026-10-20 (first verify PASS WITH FOLLOW-UPS with seven text findings, fixed; second FAIL: lane end dropped statuses and slice log, L1 text stale, staged briefs and mid-slice sessions skipped the check, stale local default branch, core stop list; all fixed).
Decisions: see the 2026-10-20 entry under Decisions.
Outcome: Bosun says when slices may run as parallel lanes, keeps parallel lanes from conflicting in the spec, checks a new slice against other open work before it starts, and never lets a lane run migrations or data-resetting suites on a stack another session uses.
Done-conditions:
L1. `verified 2026-10-20 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second FAIL, third PASS WITH FOLLOW-UPS; rules/core.md:55,61-69, codex/rules/core.md:50,56-64` Both core rules files gain an identical "Parallel lanes" section after "Run policy" that says: what a lane is; run in parallel only when slices touch different files and tables and neither needs the other's result, one after the other when one depends on the other, either is a wide refactor, or both change migrations or the same schema; two lanes per project by default; every writing lane in its own worktree and branch; while more than one lane is active, each lane keeps everything it would write to the spec (brief, done-conditions and statuses, slice log, follow-ups, lessons and lesson corrections) in `lanes/<lane>.md` next to the spec and does not edit the spec file; the spec file plus every lane file in `lanes/` is the spec; lanes find each other through the lane files in the repo's other worktrees; at lane end its last PR moves everything in the lane file into the spec and deletes the lane file; a session mid-slice when a second lane starts finishes that slice in the spec and becomes a lane from its next slice; the optional `Stack isolation: <command>` line, claimed stacks recorded in the lane file and released at lane end, one lane at a time on a shared stack without the line; never an unapproved or unmerged migration on, or a reset or stop of, a stack or server another session uses; an optional hub that decides lanes and merge order, relays approvals in the user's words, alone edits the spec's shared sections, and does not hand out resources a command can claim. Both files' run-policy stop lists include the overlap stop.
L2. `verified 2026-10-20 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second FAIL, third PASS WITH FOLLOW-UPS; skills/bosun-brief/SKILL.md:38,62-73,85,96, codex/skills/bosun-brief/SKILL.md:31,54-65,76,87` Both `bosun-brief` skills: step 2 points to a new "Parallel lanes" section, identical in both, which says that when another worktree holds an active lane file or the repo has open PRs other than this session's own and the branch step 4 stacks on, the lead lists the files each other lane or mid-slice worktree changes against `origin/<default>` (committed or not) and expects to change per its lane file, and each such PR's files (leaving out the spec and lane files), compares them with the files this slice expects to change, adds `Lane:`, `Files expected:`, `Overlap:`, and `Stack:` lines to the brief, re-runs the check when a staged brief is re-validated, does not start a slice that overlaps or is a wide refactor alongside another lane (picks the next runnable slice with no overlap, or reports and stops when none, which is also a stop condition under "Until blocked"), and in a lane sends every spec write the skill describes (steps 3, 4, 6, 8, 9) to the lane file.
L3. `verified 2026-10-20 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second FAIL, third PASS WITH FOLLOW-UPS; README.md:190,198-208,238,243; manifests 0.14.0` README gains a short "Parallel lanes" section and its "Not covered on purpose" parallel-agents bullet says lanes are covered there; version 0.14.0 in all three manifests and the README version line.
L4. `verified 2026-10-20 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second FAIL, third PASS WITH FOLLOW-UPS; all L4 checks exit 0 on fingerprint 9b98b1b` Checks pass: `bash -n scripts/*.sh codex/scripts/*.sh`; JSON parses for the manifests and hooks; `claude plugin validate .`; `git diff main --check`; the L1 section is byte-identical in both core rules files; the L2 section in the two brief skills differs only in plugin naming (`bosun-scout`/`bosun_scout`, `/bosun-brief`/`$bosun-brief`).
Out of scope: stack-isolation scripts, port bands, and migration-numbering checks in any project (cre-list's per-lane stacks are its own slice); a lease or lock tool; changes to `bosun-triage`, `bosun-verify`, `bosun-checkpoint`, or the agents (they read "the spec", which L1 defines to include lane files); converting any project to lanes.
Assumptions: lane files sit in a `lanes/` directory next to the spec so they work for root and docs-convention specs alike. The hub is optional because two lanes can be coordinated by the user directly. Minor version bump for a new rule.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in L4. No end-to-end suite; CI's `checks` job is the required check.
Branch: parallel-lanes, from main (2361b96).

### Build mode slice (2026-10-25, verified)

Name: build-mode (2026-10-25). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS WITH FOLLOW-UPS 2026-10-25 (Michael: "we just created a new brief i would like to build"; first verify FAIL: take recommendations still stopped at undecided items, fable-opus two-FAIL stop, milestone triage branch base, no re-verify after follow-up fixes, approval drift in the core rules and README; all fixed).
Decisions: see the 2026-10-25 entry under Decisions.
Outcome: A project can let the lead act on its own recommendations and keep running. It stops only for decisions that are Michael's. It handles follow-ups and CI audits without being asked, arms auto-merge on verified PRs, and holds every screen to a design-fidelity loop whose approval gate the project chooses.
Done-conditions:
B1. `verified 2026-10-25 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS; fingerprint 86ef731` Both core rules files gain an identical "Decisions" section after "Provider mode", covering the following.
   - **The setting.** The `Decisions: ask | take recommendations` spec line; no line means `ask`, today's behavior.
   - **What the lead decides itself under `take recommendations`:**
     - an open question that comes up mid-run;
     - an undecided item the spec's outcome or decisions lean on;
     - a two-FAIL disagreement, taking the fix it recommends.
   - **How it records each one.** In the spec's decisions as "(build mode, <date>)" with the choice and one line of why, then it continues without ending the turn.
   - **What it never decides itself; the work that needs it is parked:**
     - credentials, accounts and sign-ins;
     - prices, fees and any live spend;
     - production data and anything sent to real people;
     - legal, naming and trademark questions;
     - new-design approval when `Design approval: me`;
     - anything the spec lists as the user's.

     Parking means recording a human-check, or an undecided item phrased as a question with the lead's recommendation, then taking the next runnable work.
   - **The limit.** A third FAIL on the same finding stops the run under either setting.
B2. `verified 2026-10-25 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS; fingerprint 86ef731` Both core rules files' "Run policy" section says the following.
   - `until blocked` without a `max` means `max 10 slices`.
   - Under `until blocked`, the lead never ends the turn between slices to ask whether to continue or to announce the next slice. The stop list is the only way a run ends.
   - **Merging.** After a slice verifies, the lead pushes, opens the PR and arms auto-merge with `gh pr merge <n> --auto --merge`. If GitHub refuses because every required check is already green, it merges with `gh pr merge <n> --merge`. It never merges past a red or missing required check and never bypasses protection. Where the repo has no required checks or disallows auto-merge, it leaves the PR open and says so. Where the project's spec or instructions say merging is the user's, those win.
   - **No waiting on CI.** While a PR's CI runs, the lead briefs and starts the next slice, stacked when it depends on the unmerged branch.
   - **The stop list.** "The next runnable done-condition depends on an undecided item", which can never fire, is replaced by "every remaining runnable item needs a decision the lead may not make (see Decisions)", and the two-FAIL entry reads per B1.

   This resolves the run-policy follow-up of 2026-09-03 about the stop that can never fire.
B3. `verified 2026-10-25 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS; fingerprint 86ef731` Both core rules files gain an identical "Follow-ups and milestones" paragraph. Every follow-up gets a home when it is written:
   - **Bugs and security issues in the slice's own work:** fixed in that slice.
   - **Bugs in shipped code:** fixed by the next slice that touches the file, or by a hygiene slice before the milestone closes. No bug outlives its milestone.
   - **Nits:** folded into the next slice that touches the file. Dropped at milestone end if still open and not cheap.
   - **Deferrals:** name their target done-condition or milestone.
   - **Items that need the user or gate a launch:** go to the spec's human-checks.
   - **A milestone** is a group of done-conditions the spec names as one, or every fifth slice in a spec without groups.
   - **At each milestone end, under `until blocked`, the lead runs:**
     - `/bosun-triage`;
     - a hygiene slice, own PR, for the open bugs;
     - a `/bosun-ci` audit against recent runs, with findings recorded as follow-ups and fixes as their own slice, never folded into a feature slice.
   - **More than five open bugs** makes the next slice a hygiene slice.
B4. `verified 2026-10-25 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS; fingerprint 86ef731` Both core rules files gain an identical "Design" section, which applies to any slice that adds or changes a screen.
   - **The setting.** A `Design approval: me | critique` spec line. With no line, a project with UI is `me`.
   - **The loop:**
     1. Read the screen's board, the design system and any motion and mock-data notes before writing UI code.
     2. Mock up a screen with no board first, in the project's design system: on a design canvas artifact when the session has one, with a copy in the repo's design folder.
     3. Get the mockup approved:
        - under `me`, Michael approves it before product UI is written, and a new design direction or new interaction pattern always waits for that;
        - under `critique`, a fresh agent critiques it and the board is revised, with an "After critique" note.
     4. Build the screen.
     5. Before the first verify, check it at 390, 768, 1024, 1280 and 1440 wide (or the project's named widths), with empty, loading, error, hover and focus states and the board's motion including exits and reduced motion.
     6. A fresh agent compares the screenshots with the board, and open differences block the done-condition.
   - **New directions start fresh:** several new options, not variations on an older approved mockup.
   - **Screenshot paths** go in the evidence lines.
B5. `verified 2026-10-25 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS; fingerprint 86ef731` Both `bosun-brief` skills carry the changes as follows.
   - **Step 5:** stop only when B1's list blocks, and otherwise park the item and take other work.
   - **Step 6:** run B4's loop for screen done-conditions.
   - **Step 7:** apply B1's two-FAIL handling.
   - **"Until blocked":** apply B2's merging, no waiting on CI, no asking between slices, the stop list and B3's milestone-end steps.
   - **"Exhausted roadmap":** under `take recommendations`, hygiene slices built from open bug follow-ups count as runnable work. New features are still never invented.
   - **Worker prompts** in fable-crew and fable-opus mode include the Design section when the slice touches a screen.
   - **The brief template** gains `Decisions:` and `Design approval:` lines, with the effective value and its source.
B6. `verified 2026-10-25 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS; fingerprint 86ef731` Both `bosun-triage` skills say triage also runs at milestone end under `until blocked`.
   - Under `Decisions: take recommendations`, the lead applies that triage itself:
     - removals and status corrections, with evidence;
     - draft slices from open bugs promoted to hygiene done-conditions.

     Everything else stays a draft, decisions are never reworded, and the result goes in a commit on its own branch and PR.
   - Under `ask`, triage reports and waits as it does today.
B7. `verified 2026-10-25 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS; fingerprint 86ef731` Both `bosun-verify` skills pass the board path, the widths and the states to check for every screen done-condition that names a board. The verifier compares its screenshots with the board and reports each difference as a finding.
B8. `verified 2026-10-25 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS; fingerprint 86ef731` README:
   - "Run policy" describes B2;
   - new short "Decisions" and "Design" sections;
   - the "lead never merges" wording is removed;
   - version 0.15.0 in all three manifests (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `codex/.codex-plugin/plugin.json`), `.agents/plugins/marketplace.json` if it carries a version, and the README version line.
B9. `verified 2026-10-25 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS; fingerprint 86ef731` Checks pass, and the new sections in the two core rules files are byte-identical:
   - `bash -n scripts/*.sh codex/scripts/*.sh`;
   - JSON parses for the manifests and hooks;
   - TOML parses for `codex/agents/*.toml`;
   - `claude plugin validate .`;
   - `git diff main --check`;
   - B1–B4 byte-identical in `rules/core.md` and `codex/rules/core.md`;
   - the changed sections of the two brief, triage and verify skills differ only in plugin naming (`bosun-scout`/`bosun_scout`, `/bosun-x`/`$bosun-x`).
Out of scope:
- Changing any project's spec. Quillery, RV Rez and CRE Launch adopt the lines in their next slice.
- Michael's global `~/.claude/CLAUDE.md`.
- The agent definition files, apart from what the verify prompt carries.
- A design skill, and any automated design-diff tooling.
- Scheduled `bosun-ci` runs (still deferred).
- The other open follow-ups, apart from the one B2 resolves.
Assumptions:
- **The two-FAIL limit.** Under `take recommendations` a two-FAIL disagreement is decided by the lead because Michael took its fix every time it reached him in Quillery. A third FAIL on the same finding still stops the run, so a wrong fix cannot loop.
- **Money stays with Michael.** Prices, fees and spend are on the never-decide list because they are where he overrode recommendations most.
- **The design default.** `Design approval: me` is the default, because two of three projects gate on his approval. `critique` is opt-in for projects with an approved design system.
- **Merging an already-green PR.** `gh pr merge --merge`, used only when GitHub refuses auto-merge because every required check is already green, does what auto-merge would have done at once. Michael answered this case "Merge green prs." on RV Rez on 2026-10-18. Michael approved it on 2026-10-25 (see Decisions); his global CLAUDE.md's "never merge by hand" line is to be reworded to match.
- **The default cap of 10.** Michael raised CRE Launch and RV Rez to 10.
- **The milestone fallback.** "Every fifth slice" is used when a spec names no milestones, so triage and audits still happen.
- **Versioning.** Minor version bump for new rules.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in B9. No end-to-end suite; CI's `checks` job is the required check.
Branch: build-mode, from main (be42956).

### Remove lanes slice (2026-10-26, verified)

Name: remove-lanes (2026-10-26). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS 2026-10-26 (first verify FAIL: default branch and no-commit branches passed the ancestry test; ignored files such as `.env` were deleted; cleanup wording overstated under `ask`; fetch/prune ran before approval; all fixed; second PASS WITH FOLLOW-UPS: merged-PR test ignored the PR's base, README prune wording; fixed in-slice; third PASS).
Decisions: see the 2026-10-26 entry under Decisions.
Outcome: Bosun no longer carries the parallel-lanes machinery, keeps its safety rules for other sessions, and cleans up merged worktrees and branches at each milestone end; the deferred milestone gaps and the launch-and-operate plan are on record.
Done-conditions:
W1. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint fc72ff1` Both core rules files lose the "Parallel lanes" section and the Run policy overlap stop. Their "Follow-ups and milestones" paragraph says `bosun-triage` also removes merged, clean, idle worktrees and branches, and stays byte-identical across the two files. "While working" gains an identical "Other sessions" paragraph: every writing session in its own worktree and branch, only read-only sessions share a checkout, never an unapproved or unmerged migration on a database another session uses, never a reset or stop of another session's stack or server, never stopping processes by name.
W2. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint fc72ff1` Both `bosun-brief` skills lose the step 2 lane trigger, the "Parallel lanes" section, the overlap stop in "Until blocked", and the lane parts of staged-brief re-validation. The milestone-end paragraph points to triage's "Git cleanup". The two files still differ only in plugin naming and their existing harness differences.
W3. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint fc72ff1` Both `bosun-triage` skills gain an identical "Git cleanup" section, before "Milestone end", covering the following.
   - **Steps.** `git fetch --prune`, `git worktree prune`, then `git worktree list --porcelain`.
   - **Removable worktree.** All of these hold:
     - it is not the main checkout, not this session's worktree, and not locked;
     - it is not under `.claude/worktrees/`;
     - it has a branch, not a detached HEAD, and not the default branch;
     - its work is merged: a PR merged into the default branch (`--base <default>`) whose head commit is the branch tip (ancestry alone is not enough);
     - `status --porcelain --ignored` shows no uncommitted or untracked files and no ignored files beyond dependency and build output;
     - no process has its working directory inside it.
   - **Branches.** A local branch with no worktree is removable by the same merge test, never the default branch or this session's branch.
   - **Removal.** `git worktree remove` without `--force`; `git branch -D`, safe because of the merged-PR test. Never a remote branch.
   - **Report and approval.** The report lists removable items with evidence and every other worktree with its reason. Removal waits for approval under `Decisions: ask`, and is applied by the lead at a milestone end under `Decisions: take recommendations`.
   - **Other edits.** "Milestone end", "Apply on approval", "Boundaries" and the description say the same.
W4. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint fc72ff1` README loses the "Parallel lanes" section and the run-policy overlap stop. It gains a short "Other sessions" section, and its triage and milestone text mentions cleanup. The "Not covered on purpose" bullet says lanes were removed. Version 0.16.0 in all three manifests and the README version line.
W5. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint fc72ff1` This spec records the removal and the deferrals.
   - The 2026-10-26 decision is added in Michael's words.
   - The build-mode slice is moved under history, and the parallel-lanes slice heading is marked removed.
   - The out-of-scope line about parallel slices is updated.
   - The seven parallel-lanes follow-ups are removed, resolved by the removal: verify fingerprint, overlap trigger, step-2 wording, lane end, migration overlap, lane-file visibility, and the Design stop list.
   - Two deferrals record the milestone gaps.
   - "Launch and operate (drafts)" records the plan as proposals, not done-conditions.
W6. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint fc72ff1` Checks pass:
   - `bash -n scripts/*.sh codex/scripts/*.sh`;
   - JSON parses for the manifests and hooks;
   - `claude plugin validate .`;
   - `git diff main --check`;
   - no `lane` or `Stack isolation` text outside SPEC.md and the README's not-covered bullet;
   - the core "Follow-ups and milestones" section and "Other sessions" paragraph are byte-identical in both files;
   - the brief and triage skill pairs differ only as before plus naming.
   - A scratch-repo run of the W3 commands removes a merged clean worktree, and keeps a dirty one, an unmerged one, and one with a process running inside it.
Out of scope: the hygiene-slice rules themselves; the two deferred milestone gaps; any project's spec or worktrees (cre-list's cleanup happens when its next milestone triage runs or when Michael asks); factory changes (Sentry, PostHog, Intercom); building the launch skill.
Assumptions:
- **Where cleanup lives.** Cleanup lives in triage, which already runs first at each milestone end. Michael said "the hygiene slice", but cleanup changes no file and a hygiene slice is a code slice with its own PR; this keeps the timing he asked for.
- **App-made worktrees.** Worktrees under `.claude/worktrees/` are left alone because the desktop app tracks and cleans them itself.
- **Whether a worktree is in use.** `lsof` working-directory checks are the signal that a session is using a worktree; an idle session parked in a worktree with no process is not detectable and loses only a merged checkout with no uncommitted, untracked, or non-regenerable ignored files.
- **Versioning.** Minor bump, because a rule is removed and a behavior added.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in W6. No end-to-end suite; CI's `checks` job is the required check.
Branch: remove-lanes, from main (8b1569a).

### Merge flow slice (2026-10-26, verified)

Name: merge-flow (2026-10-26). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS 2026-10-26 (first verify FAIL: a dependent slice could wait forever on a PR that never merges on its own; every slice writes the spec, so "independent" never held and spec edits conflicted; triage still stacked; red-PR fixes skipped verify; update-branch restarted every PR's CI; no check of the default branch's runs; no `one slice` rule; all fixed; second PASS WITH FOLLOW-UPS: triage could wait forever, the brief still said not to wait, required reviews block auto-merge, spec drift, the staged-brief diff ref, the flake rule; all fixed; third PASS).
Decisions: see the 2026-10-26 "Merge flow" entry under Decisions.
Outcome: Under `until blocked`, the lead builds ahead only on independent slices, never stacks on unmerged ones, fixes red PRs before going on, and works with a merge queue where one exists or keeps behind PRs moving where none does. `bosun-ci` reports a merge setup that piles PRs up.
Done-conditions:
M1. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d49d553` Both core rules files gain an identical "Merge flow" section after "Run policy", covering the following.
   - **Build ahead.** Only slices that need nothing from an unmerged slice are built while a PR's checks run, each in its own worktree from the latest default branch. A dependent slice is briefed during CI and built after its base merges, with independent work taken meanwhile. Branches are never stacked on unmerged slices.
   - **Red PRs.** The lead checks open PRs before each slice and after each verify. A red PR pauses the current slice, is fixed on its own branch in its own worktree, and then the lead resumes. Slices that depend on it wait for the fix to merge.
   - **Merge setup.** A merge queue is recommended where GitHub offers one, with required checks on `merge_group` and a `merge_group` fallback for any job that reads a PR number. Without a queue, the up-to-date requirement is off and CI runs on pushes to the default branch. A repo that requires up-to-date branches without a queue gets the oldest behind PR updated with `gh pr update-branch`, one at a time, and a `bosun-ci` finding.
   - **Waiting.** When only dependent slices remain, the lead waits for a base PR that merges on its own. If the base cannot merge on its own, the run stops: a new stop-list entry in both core rules files and both brief skills.
   - **Spec edits.** The spec does not count toward independence. A built-ahead slice writes its brief as its own subsection and appends its log lines. Spec conflicts are resolved by keeping both sides.
   - **Watching.** The lead checks open PRs and the default branch's latest run before each slice, after each verify, and while waiting. A red or conflicting PR is fixed in its worktree, and a code fix is verified. A red default branch is fixed first.
   - **Updating behind PRs.** Without a queue, only the oldest behind PR is updated, one at a time.
   - **Run policy.** Its CI sentence says the lead does not idle on CI and waits only where "Merge flow" says.
   - **Worktree wording.** The fable-opus worker uses the slice's worktree (Claude core rules and brief).
   - **Triage.** Both `bosun-triage` skills wait for the run's open PRs to merge before milestone-end triage, then branch from the latest default branch.
M2. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d49d553` Both `bosun-brief` skills: step 4 starts from the latest default branch, builds a dependent slice only after its base merges, uses a new worktree while another slice's PR is open, and never stacks. Under `one slice`, a dependent slice is not started and the PR it waits for is reported. Staged briefs record and compare the default branch's HEAD. The "Until blocked" text drops stacking and adds the open-PR check: update behind PRs where required, and fix red PRs first. The pair still differs only as before.
M3. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d49d553` Both `bosun-ci` skills' baseline reads the default branch's merge setup. Requiring up-to-date branches without a queue is a finding. Under a queue, a required workflow without `merge_group`, or a PR-number job without a fallback, is a blocking finding. The pair still differs only as before.
M4. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d49d553` README gains a "Merge flow" paragraph under "Run policy", and its run-policy sentence points to it. Version 0.17.0 in all three manifests and the README version line.
M5. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d49d553` Checks pass:
   - `bash -n scripts/*.sh codex/scripts/*.sh`;
   - JSON parse;
   - `claude plugin validate .`;
   - `git diff main --check`;
   - the "Merge flow" section is byte-identical in both core rules files;
   - no "stack on it" or "stacked on the previous" text remains in the brief or core rules;
   - skill-pair diff counts are unchanged.
Out of scope:
- `bosun-preflight`. It audits launch readiness, not repository merge settings; it already lists unreadable branch protection as unknown.
- Changing any project's repository settings. The lead does that outside this slice: for rv-rez, quillery and project-hearth, and for mom-ai once it has a repo; cre-list stays with its own session.
- A third-party merge queue.
Assumptions:
- **Never stacking.** "Stacking is only for real dependencies" in the relayed request is read together with "a dependent slice is briefed during CI and built only after its base merges": a dependent slice waits for its base to merge, so nothing is stacked. Stacked PRs are what piled up in cre-list.
- **When the lead looks at PRs.** Checking open PRs and the default branch's latest run before each slice, after each verify, and while waiting is how the lead notices a red PR without polling CI between those points.
- **Versioning.** Minor bump, because this changes run behavior.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in M5. No end-to-end suite; CI's `checks` job is the required check.
Branch: merge-flow, from main (6d2c26c).

### Remove Codex slice (2026-10-30, verified)

Name: remove-codex (2026-10-30). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS 2026-10-30 (first verify PASS WITH FOLLOW-UPS: the README checkpoint line rendered inside the plugin table, a missing "and", `/bosun-mode --verifier-effort` on a stored removed mode hit an argparse error, plural worker-mode wording, stale follow-up wording, "task routing"; all fixed; second PASS).
Decisions: see the 2026-10-30 entry under Decisions.
Outcome: Bosun is a Claude Code plugin only, with three provider modes (`fable`, `fable-opus`, `opus`); the Codex plugin, the Codex worker and the `fable-crew`, `astra-crew` and `astra` modes are gone, and a spec still naming one of them gets a clear message instead of a half-working run.
Done-conditions:
X1. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS; fingerprint e5f064c` Removed from the repo: `codex/` (the whole Codex plugin), `.agents/plugins/marketplace.json` (and the then-empty `.agents/`), and `scripts/codex-worker.sh`.
X2. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS; fingerprint e5f064c` `rules/core.md`: "Provider mode" lists three modes (`fable`, `fable-opus`, `opus`). The routing table, the `Route:` override, the `ultra` ban, the worker-never-commits and preflight text for crew workers, and the `astra*` and Codex sentences are gone. It says the values `codex`, `fable-crew`, `astra-crew` and `astra` were removed in 0.18.0 and that a spec naming one makes `/bosun-brief` and `/bosun-verify` stop and say to choose a mode with `/bosun-mode`. Staging under `until blocked` names `fable-opus` only. Nothing else in the file changes.
X3. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS; fingerprint e5f064c` Skills: `bosun-brief` loses the "Fable-crew mode" section, the fable-crew and astra handling in "Find the provider mode" (replaced by the removed-mode stop), fable-crew mentions in steps 3 and 6 and in staging, the No-spec step 2 mode list's removed values, and the codex-preflight stop. `bosun-verify` lists only the three modes, stops on a removed value with the same message, and loses its fable-crew worker bullets. `bosun-mode` (description, argument hint, table, steps and the routing table) offers only the three modes, refuses removed values naming the three, and has no Codex preflight. `scripts/configure-claude-agents.py` `MODES` has only the three. No other skill or agent mentions Codex, Astra, Sol, Luna or `fable-crew`.
X4. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS; fingerprint e5f064c` README, CONTRIBUTING, `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` describe a Claude Code plugin with three modes and no Codex install, worker, routing table or `$bosun-*` commands; README says in one sentence that the Codex plugin and crew modes were removed in 0.18.0. `.github/workflows/checks.yml` drops the `codex/` paths, the `.agents` manifest and the TOML step. Version 0.18.0 in both manifests and the README version line.
X5. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS; fingerprint e5f064c` Checks pass:
   - `bash -n scripts/*.sh`; JSON parses for both manifests and `hooks/hooks.json`; `python3 -m py_compile scripts/configure-claude-agents.py`;
   - `claude plugin validate .`;
   - `git diff origin/main --check`;
   - `grep -rniE 'codex|astra|fable-crew|gpt-5\.6|\bsol\b|luna|\$bosun' --exclude-dir=.git --exclude=SPEC.md .` prints only the removal notes X2–X4 call for;
   - `python3 scripts/configure-claude-agents.py --help` lists the three modes, and a dry invocation with `fable-crew` is refused.
X6. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS; fingerprint e5f064c` This spec: the decision entry; the merge-flow brief moved to history; Design gets a one-line note that its fable-crew, astra and Codex-plugin parts are superseded; Out of scope lines about Codex and crew workers marked superseded; Codex-only lessons removed; follow-ups about the removed files dropped as resolved by removal; the slice log line.
Out of scope:
- Lanes (the next slice).
- Editing other projects' specs. Four still name removed modes (`kurts-data`: astra; `Dev Projects/test`: astra-crew; `front-office` and `the-buildoff`: fable-crew); they get the stop message and Michael switches them when he next opens them.
- Uninstalling the Codex plugin from `~/.codex` or the `codex` CLI.
- Rewriting history sections of this spec beyond X6.
- Removing `fable` or `fable-opus`.
Assumptions:
- **Removed values stop, they don't map.** Mapping `fable-crew` to `fable-opus` or `opus` silently would change who implements and on which model; a stop with the fix named is safer and costs one command.
- **Staged briefs stay.** Staging exists for `fable-opus` too, so the rule stays with that mode only.
- **Versioning.** Minor bump, because modes are removed.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in X5. No end-to-end suite; CI's `checks` job is the required check.
Branch: remove-codex, from main (2a975fe).

### Lanes slice (2026-10-30, verified)

Name: lanes (2026-10-30). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS 2026-10-30 (first verify FAIL: the setup slice was unreachable, the no-start-session fallback contradicted itself, lane stops still went to the user, plus ten gaps on ownership, counting, milestones, model, proposal timing and wording; all fixed; second PASS WITH FOLLOW-UPS: red default branch, undecided items decided twice, hand-started lanes, hygiene vs lane areas, setup timing, woken hub, triage wording, spec text; all fixed; third PASS).
Decisions: see the 2026-10-30 "Lanes" entry under Decisions.
Outcome: Under `until blocked`, a lead whose spec has two or more independent areas can, with Michael's one approval per run, start lane sessions that each run their own Bosun loop in their own worktree on an isolated test stack, while the lead acts as the hub and the only channel to Michael, in the shape that worked in cre-list on 2026-10-29/30.
Done-conditions:
N1. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d3e6381` `rules/core.md` gains a "Lanes" section after "Merge flow", covering:
   - **What a lane is.** A separate Claude Code session the hub (the session running the run) starts in its own worktree, running its own Bosun loop on one area of the spec. Lanes are sessions, never subagents; subagents stay inside a slice as before.
   - **When.** All of: `Run policy: until blocked`; two or more areas, each with at least three runnable slices, that touch different files and tables and need nothing from each other; tests isolated or made so by the setup slice; and lane sessions can be started, by the hub or by the user from printed prompts. Otherwise there are no lanes.
   - **Approval.** The hub proposes lanes (areas, the shared files it keeps, lane count and slice caps) and starts them only after Michael approves, once per run, under either `Decisions:` value.
   - **Stack isolation.** When data-resetting checks share a stack and the spec has no `Stack isolation:` line, the first lane step is a setup slice that builds a per-lane stack command (own project id and port band generated from the committed config into an ignored folder, a holder record so one worktree holds a lane, refusal of plain data-resetting runs in a worktree that holds a lane, and a teardown that removes containers and volumes) and adds the line.
   - **Area split and shared files.** Lanes are split by area, not slice. The hub names the shared files it owns; a lane that needs a change there messages the hub instead of making it.
   - **Ceiling.** At most three sessions: the hub and one lane by default, a second lane only when a third independent area exists.
   - **Branches, PRs and the spec.** Each lane slice branches from the latest default branch, gets its own PR and auto-merge as "Run policy" says, and "Merge flow" applies inside each lane. Lanes write the spec directly as "Merge flow" "Spec edits" says (own subsection, appended lines, keep both sides on conflict).
   - **Michael goes through the hub.** A lane runs under the spec's `Decisions:` value. Anything only Michael can give is recorded in the slice and sent to the hub (what, why, where the screenshots are); the lane takes other runnable work. The hub batches these for Michael. Lanes never ask him directly.
   - **Checks in a lane.** A lane claims its stack before any data-resetting check, runs those checks only through it, tells its verifiers to do the same, gives every screenshot and output path as an absolute path inside its worktree, and releases the stack when it ends.
   - **Lane end.** At its slice cap, when its area has no runnable work, or at any "Run policy" stop, a lane releases its stack and reports to the hub: why it ended, each slice, PR, verify verdicts, follow-ups, and what waits on Michael. The hub checks those PRs before reporting them done.
   The "Other sessions" paragraph stays as is.
N2. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d3e6381` `skills/bosun-brief/SKILL.md` gains a "Lanes" section after "Until blocked", and "Until blocked" points to it at the start of a run and at each milestone end. The section holds:
   - the hub's check of the core rules' conditions;
   - the proposal it puts to Michael;
   - the setup slice when needed;
   - a fenced lane prompt template (area, done-conditions or spec rows, shared files the hub owns, the stack command and lane number, slice cap, protected paths, what goes to the hub, done and report);
   - starting each lane with the app's start-session tool (fresh context, its own worktree, wake the hub when done) after approval;
   - what the hub does while lanes run;
   - what a lane session does differently (it reads its prompt, runs `/bosun-brief` under the spec's policies with its own cap, messages the hub, and does not ask Michael).
   - Where the session cannot start sessions, the hub prints the lane prompt for Michael to start one by hand, and does not run lanes itself.
N3. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d3e6381` `skills/bosun-verify/SKILL.md` step 1: in a lane, the prompt names the lane's stack command for data-resetting checks and requires absolute paths inside the lane's worktree for screenshots and output.
N4. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d3e6381` README:
   - gains a "Lanes" section;
   - its "Not covered on purpose" first bullet no longer says parallel sessions are uncovered (parallel builders inside one slice stay uncovered);
   - version 0.19.0 in both manifests and the README version line.
N5. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d3e6381` Checks pass:
   - `bash -n scripts/*.sh`;
   - JSON parses for both manifests and `hooks/hooks.json`;
   - `python3 -m py_compile scripts/configure-claude-agents.py`;
   - `claude plugin validate .`;
   - `git diff origin/main --check`;
   - `grep -n '^## Lanes' rules/core.md skills/bosun-brief/SKILL.md README.md` finds one heading in each.
N6. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d3e6381` This spec:
   - the decision entry;
   - the remove-codex brief moved to history;
   - the Out of scope line on parallel slices updated to point here;
   - the slice log line.
Out of scope:
- Any project's own stack script or spec. cre-list already has `scripts/lane.sh` and rv-rez has `scripts/instance.sh`; converting projects happens in their own sessions.
- A lock or lease tool in Bosun, or a shared stack script; stack commands stay per project.
- Changes to the agents, `bosun-triage`, `bosun-checkpoint`, `bosun-ci`, `bosun-preflight` or `bosun-mode`.
- Lanes inside Codex (removed) or a lane mode.
- Parallel builder agents inside one slice.
Assumptions:
- **Approval even under `take recommendations`.** Lanes cost tokens and add to Michael's review queue, and in cre-list he made the call himself; the chat agreed the hub proposes and he approves once per run.
- **Lane runs keep the spec's policies.** In cre-list, Lane B ran under the spec's `until blocked`, `take recommendations` and design setting with its own cap of 5; the hub's prompt sets the cap.
- **The tool is named by what it does.** The rules say "the app's start-session tool" rather than a tool id, since the id belongs to the host.
- **The proposal is not a stop.** `until blocked` forbids stops between slices, so the hub states the proposal in its first slice report and at each milestone end and keeps working; a yes covers the rest of the run, a no stands until the next run.
- **Ownership while lanes run** (from the first verify). A lane's area belongs to it; each session counts, watches and fixes only its own slices and PRs; milestone-end work is the hub's alone; a lane's every stop ends it with a report to the hub; and anything Bosun would ask or report to the user goes to the hub. When only lane work is left, the hub ends its turn and the app wakes it.
- **Ownership, second verify.** A lane decides only its own area's undecided items; the default branch is the hub's to fix; the hub's hygiene slice skips a running lane's area; the setup slice runs only after Michael's yes; a woken hub continues the same run; hand-started lanes relay through Michael.
- **"Several" means at least three** runnable slices per area: fewer does not repay a lane's setup and review overhead.
- **No separate skill.** With the Codex copy gone, lanes live in the core rules and `/bosun-brief`, where the hub already is.
- **Versioning.** Minor bump: new behavior.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in N5. No end-to-end suite; CI's `checks` job is the required check.
Branch: lanes, from main (60b259e).

### Planning hub slice (2026-10-30, verified)

Name: planning-hub (2026-10-30). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS 2026-10-30 (first verify PASS WITH FOLLOW-UPS: a lane could fix a red default branch itself, no milestones once lanes started, the hub's spec edits had no path to main, lane end with work left, caps past `max N`, hygiene ownership, shape precedence, README; all fixed; second PASS WITH FOLLOW-UPS: unscoped "no code", re-pick of parked work, held files; fixed; third PASS).
Decisions: see the 2026-10-30 "Planning hub" entry under Decisions.
Outcome: Once lanes start, the hub stops building and becomes the session Michael plans and decides in. It keeps the spec, reviews with him, watches the default branch, and hands every code change to a lane. A run uses one of three shapes: hub plus one lane, hub plus two lanes, or one session.
Done-conditions:
H1. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS, third PASS; fingerprint f3806ae` `rules/core.md` "Lanes" is rewritten around a hub that does not build:
   - **The hub's job.** While lanes run, the hub writes no code. It plans, decides with the user, keeps the spec, runs milestone triage and the CI audit, reviews screens with the user, watches the default branch, and relays between the user and the lanes.
   - **Shapes.** One session as before: fewer than five runnable slices in the run, or the user says they won't be steering (takes precedence). Hub plus two lanes: two independent areas, each with at least three runnable slices; work fitting neither goes to the first lane to finish. Otherwise hub plus one lane, taking all the run's work. At most three sessions run.
   - **Before the yes.** Until the user approves, the hub runs as one session as before. After the yes, it finishes its current slice and then stops building.
   - **Code goes to lanes.** Every change goes to a lane as a slice the hub assigns, at the top of that lane's queue: a shared-file change (one lane at a time holds a shared file), a red default branch (assigned as the next slice of one lane; a lane that sees it red tells the hub and finishes its current slice), the milestone hygiene slice and CI-audit fixes (given to the lane whose area holds the files).
   - **Count.** The run's `max N` bounds the slices the hub built before lanes started plus every lane's cap.
   - **Idle hub.** With lanes running and no planning work, the hub ends its turn. This is a pause, not a stop. A lane's message, a lane's end or the user wakes it, and it continues the same run.
   - Stack isolation, the user-only items, checks in a lane, lane end and hand-started lanes carry over.
H2. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS, third PASS; fingerprint f3806ae` The "Run policy" stop list in `rules/core.md` and the "Until blocked" stop list in `skills/bosun-brief/SKILL.md` drop the "hub's own area has no runnable work while lanes still run" stop. Each instead says that a hub with lanes running and no planning work pauses as H1 says.
H3. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS, third PASS; fingerprint f3806ae` `skills/bosun-brief/SKILL.md` "Lanes" follows H1:
   - step 1 chooses the shape;
   - step 2's proposal names the shape;
   - the hub stops building after the yes;
   - the template says the hub plans and does not build, that shared-file changes, red-default-branch fixes and hygiene come as hub-assigned slices at the top of the queue, and that a lane works only its own area and those assigned slices;
   - the "While lanes run" paragraph describes the planning hub.
H4. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS, third PASS; fingerprint f3806ae` README "Lanes" describes the planning hub and the three shapes. Version 0.20.0 in both manifests and the README version line.
H5. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS, third PASS; fingerprint f3806ae` Checks pass:
   - `bash -n scripts/*.sh`;
   - JSON parses for both manifests and `hooks/hooks.json`;
   - `python3 -m py_compile scripts/configure-claude-agents.py`;
   - `claude plugin validate .`;
   - `git diff origin/main --check`;
   - `grep -n "own area has no runnable work" rules/core.md skills/bosun-brief/SKILL.md README.md` finds nothing.
H6. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS, third PASS; fingerprint f3806ae` This spec:
   - the decision entry;
   - the lanes brief moved to history;
   - the three lanes follow-up nits (stop vs pause, bugs outliving a milestone, waking the hub on a red default branch) removed as resolved by H1;
   - a deferral follow-up for a third lane;
   - the slice log line.
Out of scope:
- A third lane, or a `Lanes: max N` spec line (deferred by Michael).
- Any project's spec or stack script.
- Changes to agents or to other skills.
- Running this on a project.
Assumptions:
- **"Short" means fewer than five runnable slices.** Below that, a lane's cold start and the extra session cost more than a planning hub saves.
- **The hub still edits the spec.** Bookkeeping, decisions and triage are planning, not code. A slice's own brief and statuses stay with the lane that runs it.
- **Shared files are held one lane at a time.** The hub assigns the change to one lane as a slice, so two lanes never edit a shared file at once.
- **A red default branch goes to one lane.** It becomes that lane's next slice. The other lane finishes its current slice and keeps going; its PRs merge once the fix lands, as "Merge flow" says.
- **From the first verify.** A lane that sees a red default branch never fixes it unassigned and keeps working its area. Without milestone groups, milestones count every fifth slice merged across the run. The hub lands its spec edits through short spec-only PRs. When lanes end with work left, the hub picks the shape again under the same yes, building again as one session if no lane shape fits. Caps are set at lane start within `max N`. Hygiene and CI work spanning areas or shared files goes to one lane, and a lane's own hygiene trigger counts only its area's bugs. From the second verify: "no code" applies while lanes run; the re-pick after the last lane leaves out work parked on two FAILs or a user-only item; the hub tells a lane which of its files another lane holds.
- **Lane messages wake the hub.** In the cre-list run, Lane B's messages arrived as new turns in the hub, which resolves the third nit.
- **Versioning.** Minor bump, because behavior changes.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in H5. No end-to-end suite; CI's `checks` job is the required check.
Branch: planning-hub, from main (2422d2a).

### CI practices slice (2026-11-05, verified)

Name: ci-practices (2026-11-05). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS 2026-11-05 (first verify PASS WITH FOLLOW-UPS: migrations trigger and environments too loose, no actor for approval, automatic mode had no order, missing concurrency and red-on-error guards, undo reopened the path-gate gap, cost understated, stale runbook note; all fixed; second PASS WITH FOLLOW-UPS: five small gaps, including CI needing to run on `push`; fixed; third PASS).
Decisions: see the 2026-11-05 "CI practices" entry under Decisions.
Outcome: Bosun carries the CI practices proven in a real project on GitHub Enterprise Cloud as generic guidance, including tested steps for turning on a merge queue, so future and existing projects can adopt them.
Done-conditions:
Q1. `verified 2026-11-05 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS, third PASS; fingerprint 65f663b` `skills/bosun-ci/SKILL.md` gains "Turning on a merge queue": only on request and one repository at a time, with the order (workflows first and merged, then the queue, then one proving PR read back through GraphQL), the ruleset API and the classic setting, starting values, how a diff-only required check reports in the queue, and how to undo it. The baseline says a personal-account repository cannot have a queue.
Q2. `verified 2026-11-05 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS, third PASS; fingerprint 65f663b` `skills/bosun-ci/SKILL.md` adds the flake quarantine (owner, reason, added, expiry of at most 14 days, non-blocking step, a required test that fails on bad entries) and the nightly hunt (repeat each test, one standing issue, says when reports are missing).
Q3. `verified 2026-11-05 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS, third PASS; fingerprint 65f663b` `skills/bosun-ci/SKILL.md` adds the end-to-end path gate (scope map, full suite for anything unmapped, a test that keeps the map honest), the Playwright apt fixes (archive mirror, `.deb` cache that never fails a shard), and judging balancing or runner changes on real runs, recording what was not adopted.
Q4. `verified 2026-11-05 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS, third PASS; fingerprint 65f663b` `skills/bosun-ci/SKILL.md` gains "Migrations deploy (opt-in)" with two modes, approval and automatic, approval recommended once a project has real users or money, automatic only by explicit choice. Both share the guards: a trigger limited to `push` on the default branch, environments limited to the default branch, sandbox before production, one push per database, dry runs, holds, ahead-of-main handling, and app and migration order. Approving is the user's, never a session's.
Q5. `verified 2026-11-05 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS, third PASS; fingerprint 65f663b` `rules/core.md` "Merge setup" says turning a queue on comes last, only when asked, and points to `bosun-ci`; "Tests and CI" points to the quarantine and hunt. README's `bosun-ci` section names the new guidance. Version 0.21.0 in both manifests and the README version line.
Q6. `verified 2026-11-05 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS, third PASS; fingerprint 65f663b` Checks pass: `bash -n scripts/*.sh`; JSON parses for both manifests and `hooks/hooks.json`; `python3 -m py_compile scripts/configure-claude-agents.py`; `claude plugin validate .`; `git diff origin/main --check`; `grep -n -i -E 'rigrez|rv-rez|amdg' rules/ skills/ README.md .claude-plugin/` (recursive) finds nothing.
Q7. `verified 2026-11-05 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS, third PASS; fingerprint 65f663b` This spec: the decision entry, the planning-hub brief moved to history, the promoted two-tier follow-up removed, new follow-ups, the slice log line, and the queue test recorded as a lesson.
Out of scope:
- Any project's repository, workflows or settings, including Skipline, Crelaunch and Ruthie rollouts and correcting the source project's runbook.
- Factory: the owner change, Blacksmith in generated workflows, a queue step, and teardown (its own brief in that repo).
- Project-specific shard counts, thresholds, or the source project's scripts.
- Scheduled `bosun-ci` audits and an agent routine that fixes nightly flakes.
- Stacked PRs (`gh stack`).
Assumptions:
- **Public plugin.** The repo is public, so rules, skills and README name no organization or project; this spec keeps the evidence. This is the lead's reading, not Michael's decision.
- **The migrations choice is prose, not a parsed line.** Nothing in Bosun reads it, so the project's spec records it in the user's words.
- **Build concurrency.** The source project's runbook says 2 and its live setting is 5. The starting value is 2 for expensive suites, raised after measuring, because concurrency multiplies runner cost.
- **A diff-only required check passes in the queue.** A PR enters only after its own required checks pass, so this drops no review.
- **Versioning.** Minor bump, because new guidance changes what the skill recommends and does.
Decisions setting: ask (default).
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in Q6. No end-to-end suite; CI's `checks` job is the required check.
Branch: ci-practices, from main (52783c2).

### Machine load slice (2026-11-05, verified)

Name: machine-load (2026-11-05). Mode: opus (Opus 5.5 leads and implements). Status: verified 2026-11-05 (first verify PASS WITH FOLLOW-UPS: an environment failure could hide a real bug and conflicted with "Merge flow", "owns" was ambiguous, no record of intermittent failures, no path after a failed retry, loose triage matching; all fixed; second FAIL: the open-PR path still said to fix the PR; fixed; third PASS WITH FOLLOW-UPS: summary wording in the brief and README, updated without a further verify).
Decisions: see the 2026-11-05 "Machine load" entry under Decisions.
Outcome: Parallel work stays within what one machine can hold: stacks start light and go away when done, sessions check the load before heavy work, leftovers get reported, and environment failures are named as such.
Done-conditions:
K1. `verified 2026-11-05 bosun-verifier (claude-opus-5-5/high), third verify; fingerprint 18b58d5, plus the summary wording` `rules/core.md` "Stack isolation": the command starts only the services the project's tests need, the list CI uses; a slice that needs another adds it for that run; lanes use the command rather than copying the stack by hand.
K2. `verified 2026-11-05 bosun-verifier (claude-opus-5-5/high), third verify; fingerprint 18b58d5, plus the summary wording` `rules/core.md` "While working" gains "Shared machine": a session stops the dev servers and stacks it started or holds when done, a lane removes its stack when it ends, the load is checked before a stack or full test run, under pressure a session stops only what it started and isn't using and reports the rest, including anything it's unsure of, and the check never blocks.
K3. `verified 2026-11-05 bosun-verifier (claude-opus-5-5/high), third verify; fingerprint 18b58d5, plus the summary wording` `rules/core.md` gains "Environment failures": check first whether the change could have caused it, which makes it a code failure; otherwise one retry, with the machine's state noted at the first failure and reported either way; never a test result, and nothing changes in the slice to get past it; a blocked step is recorded and other work continues; a run stops when it blocks everything. "Merge flow" and both stop lists agree. Flaky tests stay under "Tests and CI".
K4. `verified 2026-11-05 bosun-verifier (claude-opus-5-5/high), third verify; fingerprint 18b58d5, plus the summary wording` `skills/bosun-triage/SKILL.md` gains "Leftover stacks and servers": report only, including at a milestone end.
K5. `verified 2026-11-05 bosun-verifier (claude-opus-5-5/high), third verify; fingerprint 18b58d5, plus the summary wording` README names the rules. Version 0.22.0 in both manifests and the README version line.
K6. `verified 2026-11-05 bosun-verifier (claude-opus-5-5/high), third verify; fingerprint 18b58d5, plus the summary wording` Checks pass: `bash -n scripts/*.sh`; JSON parses for both manifests and `hooks/hooks.json`; `python3 -m py_compile scripts/configure-claude-agents.py`; `claude plugin validate .`; `git diff origin/main --check`; `grep -rn -i -E 'rigrez|rv-rez|amdg|skipline|cre-list|crelaunch' rules skills README.md .claude-plugin` finds nothing new.
K7. `verified 2026-11-05 bosun-verifier (claude-opus-5-5/high), third verify; fingerprint 18b58d5, plus the summary wording` This spec: the decision entry, the ci-practices brief moved to history, new follow-ups, the slice log line.
Out of scope:
- Changing any project's stack command, script or spec; projects change when their next slice touches them.
- A `--full` option as a required script feature; Michael's pick adds a service for a run only where a project needs it.
- Thresholds or numbers for memory or swap, and machine-specific commands.
- Stopping any running stack today.
- Agent definitions, and the migration and direct-push gaps in the follow-ups.
Assumptions:
- **Cleanup is report-only in triage.** Volumes can hold data and stacks can belong to a running session, so even `Decisions: take recommendations` doesn't remove them.
- **The rules go in "While working".** They apply to every session, with or without lanes.
- **Not proven:** the intermittent `supabase start` error is unproven to be swap. These rules reduce load and record the machine's state, which would confirm or rule it out.
- **Versioning.** Minor bump, because behavior changes.
Decisions setting: ask (default).
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in K6. No end-to-end suite; CI's `checks` job is the required check.
Branch: machine-load, from main (37bce73).

### Fewer PRs slice (2026-11-15, verified)

Name: fewer-prs (2026-11-15). Mode: opus (Opus 5.5 leads and implements). Status: verified 2026-11-15 (first verify FAIL: triage sent lane milestone records to a slice branch and opened records-only PRs during a run, plus ten gaps; all fixed; second PASS WITH FOLLOW-UPS: four wording gaps, fixed; third PASS WITH FOLLOW-UPS: one drift, recorded as a follow-up under the new verify limit).
Decisions: see the 2026-11-15 "Fewer PRs" entry under Decisions.
Outcome: A run opens fewer PRs and spends fewer verify rounds for the same work, and verification gets sharper: records ride along on slice PRs, finished work moves to an archive, a FAIL needs a reachable release-blocking defect, a slice gets at most three verify runs, the implementer checks the project's recurring failures first, and a check that could not run is never reported as passed.
Done-conditions:
F1. `verified 2026-11-15 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS; fingerprint 08f2e27` Records ride along: `rules/core.md` "Run policy" says a records-only change (spec, docs, design boards) gets no PR of its own during a run, rides on the slice in flight or the next, is pushed so it is not lost, is carried into briefs that need it until it merges, and gets one PR at the run's end only when no slice follows; outside a run a requested records change keeps its own PR. "Lanes" has the hub send decisions to the lane that needs them, which records them on its slice branch, and open one records PR per milestone end and at the run's end. `bosun-brief` ("Until blocked", the lane prompt, the hub's duties) and `bosun-triage` ("Milestone end", "Apply on approval") agree.
F2. `verified 2026-11-15 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS; fingerprint 08f2e27` Archive: `rules/core.md` "The spec" says the current-slice section holds only unmerged slices, and that triage moves finished slice briefs and old slice-log entries verbatim to an archive file with a pointer, read only when an item points into it. `bosun-triage` proposes the move under "Spec health", keeps decisions, lessons, open items and anything cross-referenced by number, and proves the move with the sorted-lines comparison across both files.
F3. `verified 2026-11-15 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS; fingerprint 08f2e27` What blocks: `rules/core.md` "Finishing", `bosun-verify` and both verifier agents say a FAIL needs an unmet done-condition, a failing check, or a release-blocking defect (security, lost or wrong data, wrong money, a broken core flow) shown reachable through input the app accepts; other reachable defects make PASS WITH FOLLOW-UPS; nits are reported only for the slice's own diff, never change the verdict, and are fixed (without a further verify only when the fix cannot change behavior) or dropped, never written down. "The spec" and "Follow-ups and milestones" agree for new nits; nits already listed keep their current handling.
F4. `verified 2026-11-15 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS; fingerprint 08f2e27` The verify limit: `rules/core.md` "Finishing" caps a slice at three verify runs counting every FAIL and re-verify, repeating findings or not, a rerun for a check that could not run excluded; a third PASS WITH FOLLOW-UPS ships with slice-own non-blocking bugs recorded as `bug` follow-ups; a third FAIL stops the slice and the run as two FAILs on one finding do. Both stop lists, "Decisions", lane end, `bosun-brief` (step 7, the stop list, fable-opus step 4, the hub) and `bosun-verify` agree. This resolves the build-mode follow-up on the uncapped PASS WITH FOLLOW-UPS loop.
F5. `verified 2026-11-15 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS; fingerprint 08f2e27` Recurring verify failures: `rules/core.md` "The spec" defines the standing lesson (at most ten kinds seen in two or more slices, each with an example, empty for a new project), checked by the implementer before every verify and carried in the verify prompt. `bosun-brief` step 7 and the fable-opus worker prompt include the check, step 9's slice-log line names each blocking finding's kind, and `bosun-triage` keeps the lesson at each milestone end and reports it.
F6. `verified 2026-11-15 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS; fingerprint 08f2e27` No silent downgrade: `rules/core.md` "Finishing", `bosun-verify` and both verifier agents say a check the verifier could not run leaves its done-conditions not verified, never met; the lead reruns (outside the limit) or records the step blocked, and never reports the slice verified on a reduced check.
F7. `verified 2026-11-15 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS; fingerprint 08f2e27` README describes F1–F6 in "Milestones", "Records ride along" and "Verification". Version 0.23.0 in both manifests and the README version line.
F8. `verified 2026-11-15 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS; fingerprint 08f2e27` Checks pass: `bash -n scripts/*.sh`; JSON parses for both manifests and `hooks/hooks.json`; `python3 -m py_compile scripts/configure-claude-agents.py`; `claude plugin validate .`; `git diff origin/main --check`; `grep -rn -i -E 'rigrez|rv-rez|amdg|skipline|cre-list|crelaunch' rules skills agents README.md .claude-plugin` finds nothing new.
F9. `done` This spec: the decision entry, the machine-load brief moved to history, the build-mode follow-up on the uncapped PASS WITH FOLLOW-UPS loop removed as resolved by F4, the "Run policy" design note's stale `max 3 slices` default corrected, new follow-ups, the slice log line.
Out of scope:
- Sizing slices by risk; Michael and the lead dropped it for lack of evidence.
- Changing any project's spec, archive or lessons; projects change when their next slice or triage touches them.
- CI changes in any project, staging, and QA after merge.
- Agent definitions beyond the two verifiers' verdict and report text, and one line in their rules saying ride-along records the prompt names are not unrequested changes (added after verify run 1, because ride-along records would otherwise be reported as findings).
Assumptions:
- **Release-blocking** is named by kind (security, lost or wrong data, wrong money, a broken core flow) rather than by a severity scale, so the verifier can apply it from the code.
- **Design differences still FAIL.** "Design" says open differences block the done-condition, so they are unmet done-conditions, not nits.
- **A third PASS WITH FOLLOW-UPS ships** rather than stopping, because its remaining bugs are non-blocking by definition and a `bug` follow-up gives them a home.
- **The archive is a move, not a condensation,** in line with the 2026-10-11 triage decision that history stays verbatim.
- **Versioning.** Minor bump, because behavior changes.
Decisions setting: ask (default).
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in F8. No end-to-end suite; CI's `checks` job is the required check.
Branch: fewer-prs, from main (ad25bb1).

## Public readiness slice — September 15, 2026

Authority: Michael approved reviewing and cleaning Bosun for public sharing; selected MIT explicitly.
Outcome: clear public onboarding, accurate validation limits, MIT license, and contribution guidance.
Done-conditions: P1 README explains intended user, role split, quickstart and prerequisites; P2 stale blanket untested claims replaced with evidence-linked limitations; P3 MIT license and contribution checks present; P4 manifest/shell/parser checks and CLI install-command availability checked with results reported; P5 tracked-file/history pattern scan reports findings without exposing secrets.
Out of scope: runtime/model routing changes, paid model runs, broad refactoring, production changes, automatic merge.
Assumptions: public-readiness changes are based on published main, excluding the separate uncommitted CI skill work.
Mode: astra. Branch: codex/public-readiness. Status: verified, ready for PR review.
Validation limits: clean installation and full live runs in every supported mode remain unverified. Static checks do not establish those outcomes.

Verification (2026-09-15): independent verifier PASS after correcting quickstart order and shell escaping. Shell syntax, both Claude validators, 12 JSON/TOML parses, worker dry-run, CLI install-command help, and diff whitespace checks all passed. Pattern screening was independently repeated across 27 reachable commits, 140 unique blobs, and 32 working files with no matches; public author email remains in metadata. Screening excludes unreachable objects and external artifacts and is not proof of absence. No runtime, global installation, model execution, or production changes were made. Next action: review and merge this documentation-only PR before sharing the updated onboarding.
