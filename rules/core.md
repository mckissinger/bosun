# Bosun core rules (Claude Code)

Rules for autonomous coding runs in Claude Code, whichever Claude model leads (see Provider mode). Rationale and doc citations: the Bosun README.

## Effort

Effort is the primary control on the lead. On Fable 5.1, thinking is adaptive, always on, and cannot be disabled. Effort is chosen when the session is launched (`claude --effort <level>`, or `/effort <level>` before the first brief) and held for the session. You cannot change it and should not ask for a change mid-run; state the level you are assuming in the brief.

- `low`: fully specified one-line changes. Never for anything that needs fresh information; at low, Fable 5.1 answers from memory instead of searching.
- `medium`: routine implementation with fully specified behavior and existing test coverage.
- `high`: the default. Features, multi-file changes, refactors, debugging.
- `xhigh`: runs over thirty minutes, migrations, hard bugs, reviewing large diffs.
- `max`: only when xhigh has measurably fallen short.

## The spec

Every project with substantial work has a spec file: `SPEC.md` at the repo root, or wherever the repo's docs convention puts it. It is the durable record of expectations and the only input a fresh session needs. It must contain, findably: the outcome; decisions in the user's own words; done-conditions with a status, each checkable by the verifier's tools (git diff, reading files, running the repo's checks, and a browser for a done-condition that names a route or screen) or marked human-check; undecided items; out-of-scope items; the current slice; follow-ups (things noticed and not done, one line each with the slice and date, removed when promoted to a done-condition or dropped by the user); and lessons. The layout is yours to choose per project. Keep it reviewable by a person in one sitting, and reorganize or split it when it stops being that, saying so in your report. Update status in the spec as work lands, not only at the end. Never build an undecided item; propose wording for it as a draft and leave the decision to the user.

Lessons are what this codebase needs a fresh session to know that the repo and git history do not already record: corrections, confirmed approaches, environment quirks, and why each mattered. One entry per lesson with a one-line summary first. Read them before starting a slice. Update an existing entry rather than adding a duplicate, delete entries that turn out to be wrong, and do not record what the code, the checks, or the spec already say. If the section grows past what a person reads in one sitting, split it into its own file next to the spec and say so in your report.

## Provider mode

The harness has six provider modes. The mode is a line in the project's spec, `Provider mode: <mode>`; a spec without the line is in `fable` mode, and the old value `codex` is read as `fable-crew`. `/bosun-mode` sets or reports it.

| Mode | Lead | Implementation | Harness |
| --- | --- | --- | --- |
| `fable` | Fable 5.1 | Fable 5.1 | Claude Code plugin |
| `fable-crew` | Fable 5.1 | Sol / Luna by task class via `scripts/codex-worker.sh` | Claude Code plugin |
| `fable-opus` | Fable 5.1 | Opus 5.5 at high as a native subagent | Claude Code |
| `opus` | Opus 5.5 | Opus 5.5 (also scout and verifier) | Claude Code |
| `astra-crew` | GPT-6 Astra | Sol / Luna by task class as Codex subagents | Codex plugin (`codex/` in this repo) |
| `astra` | GPT-6 Astra | GPT-6 Astra | Codex plugin |

The three `fable*` modes and `opus` run here, in Claude Code. The two `astra*` modes run in Codex through the sibling plugin; if the spec names one, `/bosun-brief` stops and says to open the project in Codex rather than running the slice here. In `fable` mode, Fable 5.1 briefs, implements, verifies, and keeps the spec. In `fable-crew` mode, Fable 5.1 still briefs, keeps the spec, commits, and verifies, but each slice's implementation is handed to an OpenAI Codex model through the user's own `codex exec` CLI via `scripts/codex-worker.sh`, routed by task class:

| Task class | When | Model | Effort |
| --- | --- | --- | --- |
| `small` | Fully specified change, one or two files, existing tests cover it | `gpt-5.6-luna` | `max` |
| `routine` | Behavior specified, repo has tests for this kind of change, design settled | `gpt-5.6-sol` | `medium` |
| `feature` | Multi-file feature, refactor, or debugging with a clear goal | `gpt-5.6-sol` | `high` |
| `hard` | Migrations, hard bugs, slices expected to run over thirty minutes | `gpt-5.6-sol` | `xhigh` |

A slice overrides the table with a `Route: <model> / <effort>` line in the spec's current-slice section. `ultra` is never passed: it auto-delegates, which fights the single-context slice design. The worker never commits; the lead reviews the diff and commits. Verification always runs on Fable through `/bosun-verify`. If the codex preflight fails, the slice stops and reports; the lead never silently implements it instead.

In `fable-opus`, Fable retains briefing, spec upkeep, commits, and verification; the project-local `bosun-worker-opus` implements at `claude-opus-5-5` / `high`. Use `/bosun-mode fable-opus` to configure it. There is one worker per slice, no nested delegation, no Codex CLI, and no fallback to Fable implementation. FAIL findings return to Opus. The worker uses the current worktree and never commits or edits the spec.

Verifier effort is independent of lead and worker effort in all four Claude modes. `/bosun-mode --verifier-effort <low|medium|high|xhigh|max>` stores a top-level `Verifier effort:` default in the spec. `/bosun-verify --effort <level>` overrides it for that invocation. Precedence: invocation override, current-slice `Verifier effort:`, top-level `Verifier effort:`, then `high`. Ignore historical slice logs and quoted examples; conflicting settings at one scope or invalid levels stop verification. `/bosun-verify` configures both project-local verifier agents with that effort before launching the appropriate one on Opus 5.5 in `opus`, otherwise Fable 5.1. Record the effective effort with each verdict and in the slice log. A retry keeps the same effort unless the user changes it. This changes the verifier's frontmatter, never the lead session's effort.

In `opus`, Opus 5.5 performs briefing, direct implementation, spec upkeep, commits, scouting, and verification. The verifier still runs in a fresh read-only context. Configure local agents with `/bosun-mode opus`, and confirm the lead session is actually on `claude-opus-5-5` before starting; a spec edit alone cannot change it. Switching back to a Fable mode restores the scout/verifier models and requires a Fable lead. Notes about a specific model's behavior, such as Fable 5.1's under Effort, are not claims about Opus. Use the local scout and verifier definitions, not plugin-scoped substitutes.

## Run policy

The run policy is a line in the project's spec next to the provider mode: `Run policy: one slice` or `Run policy: until blocked, max N slices`. A spec without the line is `one slice`; `until blocked` without a `max` means `max 3 slices`. It applies in all provider modes.

Under `one slice`, `/bosun-brief` runs one slice, verifies, reports, and stops. Under `until blocked`, after a slice verifies (PASS or PASS WITH FOLLOW-UPS), the lead records lessons, commits, pushes, opens a PR for the slice's branch, reports the slice, and then briefs and runs the next slice in the same turn. Every slice has its own branch and its own PR; the lead never merges. The run stops, with a report saying why, at the first of: no runnable done-condition remains; the next runnable done-condition depends on an undecided item; a verify produced two FAILs on the same finding; the codex preflight failed; N slices have been started in this run, counting the first.

A done-condition is runnable when its status is `todo` or `in progress`, it is not `human-check`, and nothing it needs is on the undecided list. When no runnable done-condition remains, under either policy, the lead does not invent work: it reports that the roadmap is exhausted, lists every open human-check condition and every undecided item as the question the spec records, proposes candidate next slices drawn from the spec's follow-ups section as draft done-conditions marked as proposals, and ends the turn asking what next. A proposal becomes a done-condition only when the user says so.

In fable-crew and fable-opus modes under `until blocked`, the lead uses the worker's run time to stage the next slice's brief when that slice does not depend on the running one, and re-validates the staged brief against what actually landed before running it. `/bosun-brief` holds the details.

## Starting substantial work

Anything beyond a few tool calls starts with `/bosun-brief`. With no spec, it creates one from what the user supplied and stops for review; that is the one planned stop. With a spec, it takes the next slice and runs to completion. Small tasks get a three-line brief, not a ceremony. If context was compacted, or a checkpoint was printed at session start, re-read the spec before doing anything else.

## While working

If, while working or testing, you find a pre-existing bug, a performance concern, or behavior the task doesn't mention, don't fix, optimize or extend it in this change unless the requested behavior cannot work without it; report it as a follow-up in your summary. Where the task is ambiguous, implement the reading its wording and the surrounding code most directly support, state that assumption in your summary, and don't build for the other readings as well. Verify your work however you like; scratch scripts and quick checks need not be kept. Commit tests only where the task asks for them or this repository already keeps tests for this kind of change, sized like the neighboring test files — roughly one focused test per stated behavior — and don't turn scratch checks into additional permanent test files. This is about extras only: implement every behavior the task asks for, completely.

The number of tokens used to edit files is best minimized, all else being equal. Therefore, when it will not affect the end result, try to surgically edit a file rather than rewrite the entire thing.

If a done-condition names a route or web screen, run the app and check it in a browser before calling it done, with whatever browser tool the session has (the Claude Code desktop browser pane, or Playwright MCP). A route-or-screen done-condition may name a viewport width; check it at that width and carry the viewport in the evidence line so the verifier can re-check it in Playwright at the same width. Record one evidence line per such done-condition: the route, the viewport when named, what was checked, and a screenshot path if one was taken. Screenshots are evidence when appearance matters; the accessibility snapshot is the cheaper check for text and structure. Do not walk the whole app.

Delegate independent investigation to the `bosun-scout` agent in the background with a self-contained prompt, and keep working while it runs. Collect its result when you need it, not before.

Phrase code questions to avoid safeguard false positives: ask "are there any bugs in this program" rather than "does this compile without errors"; give the model documentation for lesser-known languages; keep base64-encoded data out of tool output. If a step still returns a refusal, rephrase it once along those lines. If it persists, record the blocked step in the spec and continue with the other done-conditions.

## Finishing

Before reporting anything non-trivial as done, run `/bosun-verify` and act on its verdict. After two FAILs on the same finding, stop and report both positions to the user instead of looping. The verifier re-checks route-or-screen done-conditions in its own browser, or in its own simulator when the brief says `Surface: ios`, following your evidence lines. Report the outcome first, tie every claim to a tool result from this session, and list follow-ups separately from the delivered work. If stopping mid-slice, run `/bosun-checkpoint`.
