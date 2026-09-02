# Fable 5.1 agentic development

Rules for autonomous coding runs. Rationale and doc citations: the fable-harness README.

## Effort

Effort is the primary control on Fable 5.1. Thinking is adaptive, always on, and cannot be disabled. Effort is chosen when the session is launched (`claude --effort <level>`, or `/effort <level>` before the first brief) and held for the session. You cannot change it and should not ask for a change mid-run; state the level you are assuming in the brief.

- `low`: fully specified one-line changes. Never for anything that needs fresh information; at low, Fable 5.1 answers from memory instead of searching.
- `medium`: routine implementation with fully specified behavior and existing test coverage.
- `high`: the default. Features, multi-file changes, refactors, debugging.
- `xhigh`: runs over thirty minutes, migrations, hard bugs, reviewing large diffs.
- `max`: only when xhigh has measurably fallen short.

## The spec

Every project with substantial work has a spec file: `SPEC.md` at the repo root, or wherever the repo's docs convention puts it. It is the durable record of expectations and the only input a fresh session needs. It must contain, findably: the outcome; decisions in the user's own words; done-conditions with a status, each checkable by the verifier's tools (git diff, reading files, running the repo's checks) or marked human-check; undecided items; out-of-scope items; the current slice; and lessons. The layout is yours to choose per project. Keep it reviewable by a person in one sitting, and reorganize or split it when it stops being that, saying so in your report. Update status in the spec as work lands, not only at the end. Never build an undecided item; propose wording for it as a draft and leave the decision to the user.

Lessons are what this codebase needs a fresh session to know that the repo and git history do not already record: corrections, confirmed approaches, environment quirks, and why each mattered. One entry per lesson with a one-line summary first. Read them before starting a slice. Update an existing entry rather than adding a duplicate, delete entries that turn out to be wrong, and do not record what the code, the checks, or the spec already say. If the section grows past what a person reads in one sitting, split it into its own file next to the spec and say so in your report.

## Starting substantial work

Anything beyond a few tool calls starts with `/fable-brief`. With no spec, it creates one from what the user supplied and stops for review; that is the one planned stop. With a spec, it takes the next slice and runs to completion. Small tasks get a three-line brief, not a ceremony. If context was compacted, or a checkpoint was printed at session start, re-read the spec before doing anything else.

## While working

If, while working or testing, you find a pre-existing bug, a performance concern, or behavior the task doesn't mention, don't fix, optimize or extend it in this change unless the requested behavior cannot work without it; report it as a follow-up in your summary. Where the task is ambiguous, implement the reading its wording and the surrounding code most directly support, state that assumption in your summary, and don't build for the other readings as well. Verify your work however you like; scratch scripts and quick checks need not be kept. Commit tests only where the task asks for them or this repository already keeps tests for this kind of change, sized like the neighboring test files — roughly one focused test per stated behavior — and don't turn scratch checks into additional permanent test files. This is about extras only: implement every behavior the task asks for, completely.

The number of tokens used to edit files is best minimized, all else being equal. Therefore, when it will not affect the end result, try to surgically edit a file rather than rewrite the entire thing.

Delegate independent investigation to the `fable-scout` agent in the background with a self-contained prompt, and keep working while it runs. Collect its result when you need it, not before.

Phrase code questions to avoid safeguard false positives: ask "are there any bugs in this program" rather than "does this compile without errors"; give the model documentation for lesser-known languages; keep base64-encoded data out of tool output. If a step still returns a refusal, rephrase it once along those lines. If it persists, record the blocked step in the spec and continue with the other done-conditions.

## Finishing

Before reporting anything non-trivial as done, run `/fable-verify` and act on its verdict. After two FAILs on the same finding, stop and report both positions to the user instead of looping. Report the outcome first, tie every claim to a tool result from this session, and list follow-ups separately from the delivered work. If stopping mid-slice, run `/fable-checkpoint`.
