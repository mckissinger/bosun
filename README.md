# Fable Harness

A Claude Code plugin for autonomous coding runs on Claude Fable 5.1. One durable spec per project, effort chosen at launch, fresh-context verification, and a checkpoint for stopping mid-slice. Built only from Anthropic's Fable 5.1 documentation.

## Install

```bash
claude plugin marketplace add mckissinger/fable-harness
claude plugin install fable-harness@fable-harness
```

The plugin's core rules load automatically at session start through a hook. To make them part of your global instructions instead (one less thing printed each session), append `rules/fable.md` to `~/.claude/CLAUDE.md`; the hook detects the section heading and stops printing them.

Optional, per the effort doc's "set effort explicitly": add to `~/.claude/settings.json`

```json
{ "modelSettings": { "claude-fable-5-1": { "effortLevel": "high" } } }
```

## The shape

```
launch session at the right effort
  -> /fable-brief   (no spec: write it, stop for review | spec: brief next slice, run)
  -> work, updating spec status as done-conditions land
  -> /fable-verify  (fresh read-only verifier; marks verified in spec)
  -> report; /fable-checkpoint only if stopping mid-slice
```

## What is in the plugin

| Piece | Path | Job |
| --- | --- | --- |
| Core rules | `rules/fable.md` | Effort policy, spec contract, scope and test limits, targeted edits, delegation, refusal recovery, finishing |
| `/fable-brief` | `skills/fable-brief/SKILL.md` | Creates the spec on first run and stops for review; afterwards briefs a slice and runs it to completion |
| `/fable-verify` | `skills/fable-verify/SKILL.md` | Fresh-context verification against the spec, records verified status |
| `/fable-checkpoint` | `skills/fable-checkpoint/SKILL.md` | Transient mid-slice state the spec does not hold |
| `fable-scout` agent | `agents/fable-scout.md` | Read-only background investigator, medium effort |
| `fable-verifier` agent | `agents/fable-verifier.md` | Read-only verifier, high effort |
| SessionStart hook | `scripts/session-start.sh` | Loads the rules if needed, points at the spec, prints any checkpoint; on compaction, tells the model to re-read the spec |

Checkpoints are written to `~/.claude/fable/checkpoints/<project-slug>.md`.

## The spec

`SPEC.md` at the repo root, or wherever the repo's docs convention puts it. It is the only input a fresh session needs. The harness fixes what it must contain, not how it is laid out:

- the outcome
- decisions, in the user's own words
- done-conditions with a status, each checkable by the verifier's tools (git diff, file reads, the repo's checks) or marked human-check
- undecided items, as questions
- out-of-scope items
- the current slice

The model chooses the layout per project, keeps it reviewable by a person in one sitting, and reorganizes or splits it when it stops being that. Status is updated as work lands, so a crash mid-run loses little. The test of the spec: with the checkpoint deleted, can a fresh session continue from spec, branch, and git log? If not, the spec is incomplete.

## Daily use

1. Launch at the effort the work needs: `claude --effort high` for most slices, `xhigh` for long runs, migrations, hard bugs. Effort is held for the session; the model cannot change it.
2. New project: `/fable-brief <task>` with your structures pasted or pointed at. Review the spec it writes, fill in what you can, say go. That is the one planned stop.
3. Existing spec: `/fable-brief` (optionally naming the slice). It runs to completion, verifies, and reports.
4. Read the report: done-conditions with evidence, follow-ups, anything left out. Human-check conditions are yours.
5. Stopping mid-slice: `/fable-checkpoint`. The next session in that directory loads it.

## Why each piece exists

Sources: [Overview](https://platform.claude.com/docs/en/models/fable-5-1/overview), [What's new](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1), [Migration guide](https://platform.claude.com/docs/en/models/fable-5-1/migration-guide), [Prompting Claude Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1), [Effort](https://platform.claude.com/docs/en/build-with-claude/effort), [Refusals and fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback), [Claude Code effort controls](https://code.claude.com/docs/en/model-config).

**Effort is the primary control.** Adaptive thinking is always on and cannot be turned off. Default is `high`. The prompting guide says start at `high`, step down to `medium` or `low` where quality holds, step up to `xhigh` or `max` only where measured. At `low` the model answers from memory instead of searching. At `xhigh` and `max` it may draft a long deliverable in thinking and again in the reply. Claude cannot change effort inside a session, and the effort doc says to hold it constant within a conversation, so effort is chosen at launch and the brief states the level it assumes.

**Sizing.** The guide says Fable 5.1 "can execute very long tasks without much guidance on methodology, especially when the goal is clear," and pairs `xhigh` with runs over thirty minutes. The harness sizes work as outcomes with done-conditions, not step lists, and drains ambiguity once, in the spec, at the one planned stop.

**Finish the whole task.** The guide's autonomous-operation and "Delivering work" blocks are already injected by Claude Code on Fable 5.1, along with the progress-update line and the per-turn batching nudge, so the harness does not repeat them.

**Scope and tests.** The guide's block on keeping changes and tests to what the task asks for is in the core rules verbatim; the guide reports it cuts unrequested additions with no measurable change in task success.

**Targeted edits.** Fable 5.1 rewrites whole files more than Fable 5 did. The guide's one-sentence fix is in the core rules verbatim.

**Delegation.** The guide says letting the lead keep working while subagents run lowers time to completion at similar quality and cost. `fable-scout` runs in the background; the core rules tell the lead to keep working.

**Safeguard false positives.** The guide names three triggers: compile-check phrasing, lesser-known languages without context, base64 in tool output. The core rules carry the phrasing and a recovery step: rephrase once, then record the blocked step in the spec and move on.

**Verification.** `/fable-verify` runs a fresh-context, read-only verifier at `high`, the documented starting point, so the judgment is independent of the session that did the work. Two FAILs on the same finding stop the loop and go to the user.

**Continuity.** The guide's compaction instruction lists six things a summary must preserve. Claude Code does not expose custom compaction instructions, so the harness keeps expectations in the spec, fires a "re-read the spec" reminder from the SessionStart hook when compaction happens, and uses the checkpoint only for transient mid-slice state.

## Not covered on purpose

- Parallel builder agents. The docs credit the model's gains to long single-context runs; splitting work buys wall-clock at the cost of context and merge work, and there is no evidence yet that wall-clock is the constraint.
- Browser or UI tools for the verifier. UI-only done-conditions are marked human-check instead.
- API-side migration concerns (beta headers, append-only message arrays, `tool_choice`, `input_transformations`, fallback middleware). Claude Code manages the conversation prefix itself. If you call the Messages API directly, read the migration guide's "Preserved thinking" section first.

## Status

Version 0.1.0. Designed from the docs and walked through scenarios on paper; not yet exercised on a real multi-session project. Expect the first real runs to change it.
