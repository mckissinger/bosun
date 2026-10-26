# Bosun core rules (Codex)

Rules for autonomous coding runs in Codex; GPT-6 Astra leads in both Codex modes. This is the Codex half of Bosun; the Claude Code half, `rules/core.md`, carries the same contract for the Claude leads. Rationale: the Bosun README.

## Effort

Effort is chosen in the app's picker when the session starts and held for the session. You cannot change it mid-run and should not ask for a change; state the level you are assuming in the brief.

- `low`: fully specified one-line changes. Never for anything that needs fresh information from the repo.
- `medium`: routine implementation slices: behavior is specified, the repo has tests for this kind of change, and the design is settled. Most slices belong here.
- `high`: the default. Debugging, design-heavy features, ambiguous scope, long deliverables.
- `xhigh`: runs over thirty minutes, migrations, hard bugs, reviewing large diffs.
- `max`: only when xhigh has measurably fallen short.
- `ultra`: never. It auto-delegates, which fights the single-context slice design. Delegation in this harness is explicit: the scout, the verifier, and in astra-crew the worker agents.

## The spec

Every project with substantial work has a spec file: `SPEC.md` at the repo root, or wherever the repo's docs convention puts it. It is the durable record of expectations and the only input a fresh session needs. It must contain, findably: the outcome; decisions in the user's own words; done-conditions with a status, each checkable by the verifier's tools (git diff, reading files, running the repo's checks, and a browser for a done-condition that names a route or screen) or marked human-check; undecided items; out-of-scope items; the current slice; follow-ups (things noticed and not done, one line each with the slice, the date, and one tag: `bug`, `drift`, `nit`, or `deferral`; removed when promoted to a done-condition, dropped by the user, or shown resolved by `bosun-triage` in a batch the user approves (or that the lead applies at a milestone end under `Decisions: take recommendations`); a nit is folded into the next slice that touches its file, named as a done-condition in that slice's brief so it is in scope, or dropped through triage); and lessons. The layout is yours to choose per project. Keep it reviewable by a person in one sitting, and reorganize or split it when it stops being that, saying so in your report. Update status in the spec as work lands, not only at the end. Never build an undecided item; propose wording for it as a draft and leave the decision to the user, unless `Decisions: take recommendations` lets the lead decide it (see Decisions).

Lessons are what this codebase needs a fresh session to know that the repo and git history do not already record: corrections, confirmed approaches, environment quirks, and why each mattered. One entry per lesson with a one-line summary first. Read them before starting a slice. Update an existing entry rather than adding a duplicate, delete entries that turn out to be wrong, and do not record what the code, the checks, or the spec already say.

## Provider mode

The mode is a line in the project's spec, `Provider mode: <mode>`. Six values exist; two run here.

| Mode | Lead | Implementation | Runs in |
| --- | --- | --- | --- |
| `fable` | Claude Fable 5.1 | Fable 5.1 | Claude Code (the sibling plugin) |
| `fable-crew` | Claude Fable 5.1 | Sol / Luna by task class | Claude Code |
| `fable-opus` | Fable 5.1 | Opus 5.5 at high as a native subagent | Claude Code |
| `opus` | Opus 5.5 | Opus 5.5 (also scout and verifier) | Claude Code |
| `astra-crew` | GPT-6 Astra | Sol / Luna by task class as subagents | Codex |
| `astra` | GPT-6 Astra | GPT-6 Astra | Codex |

A spec with no line, or with `fable`, `fable-crew`, `fable-opus`, `opus`, or the old value `codex`, belongs to Claude Code: `$bosun-brief` stops and says to open the project there. `$bosun-mode` sets the line and installs the agent files. In both astra modes you brief, keep the spec, commit, and verify through `$bosun-verify`. In `astra-crew` each slice's implementation is delegated to one worker agent chosen by task class:

| Task class | When | Agent | Model / effort |
| --- | --- | --- | --- |
| `small` | Fully specified change, one or two files, existing tests cover it | `bosun_worker_small` | `gpt-5.6-luna` / `max` |
| `routine` | Behavior specified, repo has tests for this kind of change, design settled | `bosun_worker_routine` | `gpt-5.6-sol` / `medium` |
| `feature` | Multi-file feature, refactor, or debugging with a clear goal | `bosun_worker_feature` | `gpt-5.6-sol` / `high` |
| `hard` | Migrations, hard bugs, slices expected to run over thirty minutes | `bosun_worker_hard` | `gpt-5.6-sol` / `xhigh` |

A slice overrides the table with a `Route: <agent>` line in the spec's current-slice section. Workers never commit and never edit the spec; you review the diff and commit. Verification always runs in a fresh read-only context (`bosun_verifier`, or `bosun_verifier_mobile` when the brief says `Surface: ios`; Astra at high), never in the session that wrote the code.

## Decisions

The decisions setting is a line in the project's spec next to the provider mode: `Decisions: ask` or `Decisions: take recommendations`. A spec without the line is `ask`: the lead stops for the user wherever these rules say to stop.

Under `take recommendations`, the lead decides these itself, taking the option it would recommend:

- an open question that comes up mid-run;
- an undecided item, when the spec's outcome or decisions point to an answer;
- a disagreement after two FAILs on the same finding, by taking the fix it recommends and verifying again.

It records each one in the spec's decisions as "(build mode, <date>)" with the choice and one line of why, moves a decided undecided item out of the undecided list, and continues without ending the turn.

The lead never decides these itself, under either setting:

- credentials, accounts, and sign-ins;
- prices, fees, and any live spend;
- production data, and anything sent to real people;
- legal, naming, and trademark questions;
- approval of a new design when `Design approval: me` (see Design);
- anything the spec lists as the user's.

Work that needs one of these is parked: the lead records it as a human-check, or as an undecided item phrased as a question with the lead's recommendation, and takes the next runnable work. Under `ask`, two FAILs on the same finding stop the run; under `take recommendations`, a third FAIL on the same finding stops it.

## Run policy

The run policy is a line in the spec next to the provider mode: `Run policy: one slice` or `Run policy: until blocked, max N slices`. No line means `one slice`; `until blocked` without a `max` means `max 10 slices`.

Under `one slice`, `$bosun-brief` runs one slice, verifies, reports, and stops. Under `until blocked`, after a slice verifies (PASS or PASS WITH FOLLOW-UPS), you record lessons, commit, push, open a PR for the slice's branch, report the slice, and then brief and run the next slice in the same turn. Every slice has its own branch and its own PR, merged as the next paragraph says. The run stops, with a report saying why, at the first of: no runnable done-condition remains; every remaining runnable item needs a decision the lead may not make (see Decisions); a verify produced two FAILs on the same finding (three under `Decisions: take recommendations`; see Decisions); every remaining runnable slice waits on an unmerged PR that cannot merge on its own (see Merge flow); N slices have been started in this run, counting the first.

Under `until blocked`, the lead never ends the turn between slices to ask whether to continue or to announce the next slice; the stop list is the only way a run ends. After a slice verifies, the lead pushes its branch, opens its PR, and arms auto-merge with `gh pr merge <n> --auto --merge`. If GitHub refuses because every required check is already green, the lead merges with `gh pr merge <n> --merge`. It never merges past a red or missing required check and never bypasses branch protection. Where the repo has no required checks or does not allow auto-merge, it leaves the PR open and says so in the report. Where the project's spec or the user's instructions say merging is the user's, those win. The lead does not idle on CI: while a PR's checks run, it briefs the next slice and builds what "Merge flow" allows, and waits only where that section says.

A done-condition is runnable when its status is `todo` or `in progress`, it is not `human-check`, and nothing it needs is on the undecided list. Under `Decisions: take recommendations`, before concluding that none remains, the lead decides the undecided items the Decisions section lets it decide, which makes the work that waited on them runnable. When no runnable done-condition remains, do not invent work: report that the roadmap is exhausted, list every open human-check condition and every undecided item as the question the spec records, propose candidate next slices drawn from the spec's follow-ups section as draft done-conditions marked as proposals, and end the turn asking what next. A proposal becomes a done-condition only when the user says so.

In astra-crew under `until blocked`, use the worker's run time to stage the next slice's brief when that slice does not depend on the running one, and re-validate the staged brief against what actually landed before running it. `$bosun-brief` holds the details.

## Merge flow

These rules apply under `Run policy: until blocked`.

Building ahead. While a PR's checks run, the lead may build the next slice when that slice needs nothing from any unmerged slice: no code or configuration file that slice changes, no interface it defines, no behavior that must land first. The spec does not count, since every slice writes it. Each such slice works in its own worktree and branch, cut from the latest default branch, and never takes a done-condition that an open PR of the run already covers. A slice that depends on an unmerged slice is briefed while CI runs and built only after its base merges, from the updated default branch. Branches are never stacked on unmerged slices.

Waiting. When every remaining runnable slice depends on an unmerged slice, the lead waits for that PR to merge, watching its checks. It waits only for a PR that merges on its own: auto-merge armed, required checks present, and no required review. When the base cannot merge on its own (the repo has no required checks, disallows auto-merge, or requires an approving review, or merging is the user's), the run stops and names the PR it waits for.

Spec edits. A slice built ahead writes its brief as its own subsection under the spec's current-slice section, and appends its slice-log lines, follow-ups, and lessons. When two of the run's PRs then conflict, the lead merges the default branch into the later PR's branch, keeps both sides (both slices' text, and every status either one set), and pushes.

Watching open PRs. Before each slice, after each verify, and while waiting, the lead checks the run's open PRs and the latest CI run on the default branch. A PR with a failing required check or a merge conflict pauses the current slice, whose work stays in its worktree. The lead pulls that PR's branch in that PR's worktree, fixes it there, reruns the checks the fix could change, runs `/bosun-verify` on a fix that changes code (see Finishing), pushes, and resumes. A slice that depends on that PR waits until the fix merges. A red run on the default branch is fixed before any other work, as its own slice and PR from the latest default branch, unless it is a flake candidate (see Tests and CI), which is reported instead.

Merge setup. The recommended setup is a merge queue on the default branch, where GitHub offers one (public repositories owned by an organization, or GitHub Enterprise Cloud), with the required checks also triggered on `merge_group`; auto-merge then puts each PR in the queue. A required check whose workflow lacks the `merge_group` trigger never reports, so queued PRs hang; a job that reads a PR number, for example a changed-files gate on `pulls/{n}/files`, needs a `merge_group` fallback that runs everything, or queued PRs fail or skip it. Where no queue is available, the default branch does not require branches to be up to date before merging, and CI also runs on every push to the default branch. A repo that requires up-to-date branches without a queue leaves every other open PR behind after each merge, and auto-merge does not update them. There the lead updates the oldest behind PR whose checks are not failing (`gh pr update-branch <n>`), one at a time, because each update restarts that PR's CI and only one can merge per round, and pulls before pushing anything else to it. The `bosun-ci` audit reports the setting.

## Follow-ups and milestones

Every follow-up gets a home when it is written. A bug or security issue in the slice's own work is fixed in that slice. A bug in shipped code is fixed by the next slice that touches its file, or by a hygiene slice before its milestone closes; no bug outlives its milestone. A nit is folded into the next slice that touches its file, and dropped at milestone end if it is still open and not cheap. A deferral names the done-condition or milestone it waits for. An item that needs the user or gates a launch goes to the spec's human-checks. A milestone is a group of done-conditions the spec names as one; in a spec without groups, every fifth slice ends one. At each milestone end under `until blocked`, the lead runs the `bosun-triage` skill, which also finds worktrees and local branches whose work is merged and that are clean and idle, and removes them when the triage is applied, then a hygiene slice with its own PR for the open bugs, then a `bosun-ci` audit against recent runs, recording its findings as follow-ups and running any fixes as their own slice, never folded into a feature slice. When more than five bugs are open, the next slice is a hygiene slice. Under `Decisions: take recommendations`, a hygiene slice built from open bug follow-ups is runnable work, and the lead promotes those bugs to done-conditions itself; it still never invents features.

## Design

These rules apply to every slice that adds or changes a screen. The approval gate is a line in the spec next to the provider mode: `Design approval: me` or `Design approval: critique`. A project with UI and no line is `me`.

1. Before writing UI code, read the screen's board, the design system, and any motion and mock-data notes the project keeps.
2. Mock up a screen that has no board first, in the project's design system: on a design canvas artifact when the session has one, with a copy in the repo's design folder.
3. Get the mockup approved before writing product UI. Under `me`, the user approves it, and a new design direction or a new interaction pattern always waits for that approval (parked as Decisions describes). Under `critique`, a fresh agent critiques the mockup, the board is revised, and it gains an "After critique" note.
4. Build the screen.
5. Before the first verify, check it at 390, 768, 1024, 1280, and 1440 pixels wide, or the widths the project names, in its empty, loading, error, hover, and focus states, with the board's motion, including exits and reduced motion.
6. A fresh agent compares the screenshots with the board. Open differences block the done-condition.

A new direction starts fresh: several new options, not variations on an older approved mockup. Screenshot paths go in the evidence lines.

## Starting substantial work

Anything beyond a few tool calls starts with `$bosun-brief`. With no spec, it creates one from what the user supplied and stops for review; that is the one planned stop. With a spec, it takes the next slice and runs to completion. Small tasks get a three-line brief, not a ceremony. If context was compacted, or a checkpoint was printed at session start, re-read the spec before doing anything else.

## While working

If, while working or testing, you find a pre-existing bug, a performance concern, or behavior the task doesn't mention, don't fix, optimize or extend it in this change unless the requested behavior cannot work without it; report it as a follow-up in your summary. Where the task is ambiguous, implement the reading its wording and the surrounding code most directly support, state that assumption in your summary, and don't build for the other readings as well. Verify your work however you like; scratch scripts and quick checks need not be kept. Commit tests only where the task asks for them or this repository already keeps tests for this kind of change, sized like the neighboring test files, roughly one focused test per stated behavior, and don't turn scratch checks into additional permanent test files. Implement every behavior the task asks for, completely.

Tests and CI. Before handing work off or pushing, run the tests for the code you touched; run the full unit suite only when the change touches shared code, configuration, dependencies, or the test setup. Run end-to-end (browser or UI) tests targeted: the specs for the routes and flows the change touches, plus the specs the done-conditions name. Run the full end-to-end suite at most once per slice: when a required CI check runs it before merge, that check is the full run and you do not run it locally; otherwise run it once, after the last code change. No done-condition requires a full local end-to-end run. After a fix, rerun only the checks the fix could change, failed end-to-end specs first (Playwright's `--last-failed`), then the targeted set; a fix to comments or documentation reruns typecheck and lint only. Do not push to find out whether tests pass: CI is the final gate, not the feedback loop. Never weaken, skip, or delete a test to make a change pass; when a specified behavior change requires changing a test, say so in the report. New tests make no real network calls, use no real sleeps or wall-clock time, and do not depend on test order or leak global state. Follow the repository's written test and CI conventions, such as which files opt into shared state, file size limits, and which job a test belongs in; where they differ from these rules, they win. A failure that passes on rerun with no code change and is unrelated to the change is a flake candidate: report the test name and failure message, do not change code for it, never fix it with retries or longer sleeps, and quarantine it only with the user's approval. A change to CI workflows states in the report and the PR whether it adds or removes CI time, and does not undo optimizations already in place.

Other sessions. Every session that writes code works in its own worktree and branch; only a read-only session may share a checkout. Never apply an unapproved or unmerged migration to a database another session uses, never reset or stop another session's stack or server, and never stop processes by name.

Edit files surgically rather than rewriting them whole when the result is the same.

If a done-condition names a route or web screen, run the app and check it in a browser before calling it done: the built-in browser in the desktop app, or Playwright MCP where a worker has it. A route-or-screen done-condition may name a viewport width; check it at that width and carry the viewport in the evidence line so the verifier can re-check it in Playwright at the same width. Record one evidence line per such done-condition: the route, the viewport when named, what was checked, and a screenshot path if one was taken. Screenshots are evidence when appearance matters; the accessibility snapshot is the cheaper check for text and structure. Do not walk the whole app.

Delegate independent investigation to the `bosun_scout` agent (read-only, Luna at medium) with a self-contained prompt, and keep working while it runs. It has none of this conversation: give it the question, the paths, and the branch. Collect its result when you need it, not before, and read the lines it cites before acting on them.

## Finishing

Before reporting anything non-trivial as done, run `$bosun-verify` and act on its verdict. After two FAILs on the same finding, stop and report both positions to the user instead of looping, unless `Decisions: take recommendations` lets the lead decide it (see Decisions). The verifier re-checks route-or-screen done-conditions in its own browser, or in its own simulator when the brief says `Surface: ios`, following your evidence lines. Report the outcome first, tie every claim to a tool result from this session, and list follow-ups separately from the delivered work. If stopping mid-slice, run `$bosun-checkpoint`.
