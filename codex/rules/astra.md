# Astra agentic development

Rules for autonomous coding runs led by GPT-6 Astra in Codex. This is the Codex half of the Bosun; the Claude Code half carries the same contract for Fable 5.1. Rationale: the bosun README.

## Effort

Effort is chosen in the app's picker when the session starts and held for the session. You cannot change it mid-run and should not ask for a change; state the level you are assuming in the brief.

- `low`: fully specified one-line changes. Never for anything that needs fresh information from the repo.
- `medium`: routine implementation slices: behavior is specified, the repo has tests for this kind of change, and the design is settled. Most slices belong here.
- `high`: the default. Debugging, design-heavy features, ambiguous scope, long deliverables.
- `xhigh`: runs over thirty minutes, migrations, hard bugs, reviewing large diffs.
- `max`: only when xhigh has measurably fallen short.
- `ultra`: never. It auto-delegates, which fights the single-context slice design. Delegation in this harness is explicit: the scout, the verifier, and in astra-crew the worker agents.

## The spec

Every project with substantial work has a spec file: `SPEC.md` at the repo root, or wherever the repo's docs convention puts it. It is the durable record of expectations and the only input a fresh session needs. It must contain, findably: the outcome; decisions in the user's own words; done-conditions with a status, each checkable by the verifier's tools (git diff, reading files, running the repo's checks) or marked human-check; undecided items; out-of-scope items; the current slice; follow-ups (things noticed and not done, one line each with the slice and date, removed when promoted to a done-condition or dropped by the user); and lessons. The layout is yours to choose per project. Keep it reviewable by a person in one sitting, and reorganize or split it when it stops being that, saying so in your report. Update status in the spec as work lands, not only at the end. Never build an undecided item; propose wording for it as a draft and leave the decision to the user.

Lessons are what this codebase needs a fresh session to know that the repo and git history do not already record: corrections, confirmed approaches, environment quirks, and why each mattered. One entry per lesson with a one-line summary first. Read them before starting a slice. Update an existing entry rather than adding a duplicate, delete entries that turn out to be wrong, and do not record what the code, the checks, or the spec already say.

## Provider mode

The mode is a line in the project's spec, `Provider mode: <mode>`. Four values exist; two run here.

| Mode | Lead | Implementation | Runs in |
| --- | --- | --- | --- |
| `fable` | Claude Fable 5.1 | Fable 5.1 | Claude Code (the sibling plugin) |
| `fable-crew` | Claude Fable 5.1 | Sol / Luna by task class | Claude Code |
| `astra-crew` | GPT-6 Astra | Sol / Luna by task class as subagents | Codex |
| `astra` | GPT-6 Astra | GPT-6 Astra | Codex |

A spec with no line, or with `fable`, `fable-crew`, or the old value `codex`, belongs to Claude Code: `$bosun-brief` stops and says to open the project there. `$bosun-mode` sets the line and installs the agent files. In both astra modes you brief, keep the spec, commit, and verify through `$bosun-verify`. In `astra-crew` each slice's implementation is delegated to one worker agent chosen by task class:

| Task class | When | Agent | Model / effort |
| --- | --- | --- | --- |
| `small` | Fully specified change, one or two files, existing tests cover it | `bosun_worker_small` | `gpt-5.6-luna` / `max` |
| `routine` | Behavior specified, repo has tests for this kind of change, design settled | `bosun_worker_routine` | `gpt-5.6-sol` / `medium` |
| `feature` | Multi-file feature, refactor, or debugging with a clear goal | `bosun_worker_feature` | `gpt-5.6-sol` / `high` |
| `hard` | Migrations, hard bugs, slices expected to run over thirty minutes | `bosun_worker_hard` | `gpt-5.6-sol` / `xhigh` |

A slice overrides the table with a `Route: <agent>` line in the spec's current-slice section. Workers never commit and never edit the spec; you review the diff and commit. Verification always runs in a fresh read-only context (`bosun_verifier`, Astra at high), never in the session that wrote the code.

## Run policy

The run policy is a line in the spec next to the provider mode: `Run policy: one slice` or `Run policy: until blocked, max N slices`. No line means `one slice`; `until blocked` without a `max` means `max 3 slices`.

Under `one slice`, `$bosun-brief` runs one slice, verifies, reports, and stops. Under `until blocked`, after a slice verifies (PASS or PASS WITH FOLLOW-UPS), you record lessons, commit, push, open a PR for the slice's branch, report the slice, and then brief and run the next slice in the same turn. Every slice has its own branch and its own PR; you never merge. The run stops, with a report saying why, at the first of: no runnable done-condition remains; the next runnable done-condition depends on an undecided item; a verify produced two FAILs on the same finding; N slices have been started in this run, counting the first.

A done-condition is runnable when its status is `todo` or `in progress`, it is not `human-check`, and nothing it needs is on the undecided list. When no runnable done-condition remains, do not invent work: report that the roadmap is exhausted, list every open human-check condition and every undecided item as the question the spec records, propose candidate next slices drawn from the spec's follow-ups section as draft done-conditions marked as proposals, and end the turn asking what next. A proposal becomes a done-condition only when the user says so.

In astra-crew under `until blocked`, use the worker's run time to stage the next slice's brief when that slice does not depend on the running one, and re-validate the staged brief against what actually landed before running it. `$bosun-brief` holds the details.

## Starting substantial work

Anything beyond a few tool calls starts with `$bosun-brief`. With no spec, it creates one from what the user supplied and stops for review; that is the one planned stop. With a spec, it takes the next slice and runs to completion. Small tasks get a three-line brief, not a ceremony. If context was compacted, or a checkpoint was printed at session start, re-read the spec before doing anything else.

## While working

If, while working or testing, you find a pre-existing bug, a performance concern, or behavior the task doesn't mention, don't fix, optimize or extend it in this change unless the requested behavior cannot work without it; report it as a follow-up in your summary. Where the task is ambiguous, implement the reading its wording and the surrounding code most directly support, state that assumption in your summary, and don't build for the other readings as well. Verify your work however you like; scratch scripts and quick checks need not be kept. Commit tests only where the task asks for them or this repository already keeps tests for this kind of change, sized like the neighboring test files, roughly one focused test per stated behavior, and don't turn scratch checks into additional permanent test files. Implement every behavior the task asks for, completely.

Edit files surgically rather than rewriting them whole when the result is the same.

Delegate independent investigation to the `bosun_scout` agent (read-only, Luna at medium) with a self-contained prompt, and keep working while it runs. It has none of this conversation: give it the question, the paths, and the branch. Collect its result when you need it, not before, and read the lines it cites before acting on them.

## Finishing

Before reporting anything non-trivial as done, run `$bosun-verify` and act on its verdict. After two FAILs on the same finding, stop and report both positions to the user instead of looping. Report the outcome first, tie every claim to a tool result from this session, and list follow-ups separately from the delivered work. If stopping mid-slice, run `$bosun-checkpoint`.
