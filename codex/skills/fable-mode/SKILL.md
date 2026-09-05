---
name: fable-mode
description: Set or report the harness's provider mode for this project from Codex. `astra` has GPT-6 Astra implement each slice itself; `astra-crew` has Astra lead while gpt-5.6-sol or gpt-5.6-luna subagents implement, routed by task class. Setting either also installs the harness's agent files. The `fable` and `fable-crew` modes belong to the Claude Code plugin. Use when the user says "switch to astra-crew", "use sol/luna for implementation", "what mode are we in", or "move this to Claude".
---

# Fable mode (Codex)

The mode is a line in the project's spec, `Provider mode: <mode>`. It lives in the spec so a fresh session reads it with everything else. No line means `fable`; the old value `codex` means `fable-crew`. Both of those run in Claude Code, not here.

| Mode | Lead | Implementation | Runs in |
| --- | --- | --- | --- |
| `fable` | Claude Fable 5.1 | Fable 5.1 | Claude Code |
| `fable-crew` | Claude Fable 5.1 | Sol / Luna by task class | Claude Code |
| `astra-crew` | GPT-6 Astra | Sol / Luna by task class as subagents | Codex |
| `astra` | GPT-6 Astra | GPT-6 Astra | Codex |

## Steps

1. Find the spec (`SPEC.md` at the repo root, then the repo's docs convention). If there is none, say so and stop; the mode has nowhere to live until `$fable-brief` creates the spec.
2. With no argument: report the current mode (`fable` if no line, `fable-crew` if the line says `codex`) and, in `astra-crew`, print the routing table below. Stop.
3. With `astra` or `astra-crew`:
   - Set the line to `Provider mode: <mode>` (add it under the spec's first heading if absent).
   - Install the agent files: create `~/.codex/agents/` if needed and copy every `<plugin root>/agents/*.toml` into it, overwriting files of the same name. `<plugin root>` is the base directory this skill was loaded from, two levels up from this file. List what was written.
   - Print the routing table (astra-crew) and remind the user that a slice can override it with `Route: <agent>` in the spec's current-slice section, that `ultra` is never used, and that the session's effort comes from the app's picker.
4. With `fable`, `fable-crew`, or `codex`: set the line to that value (`codex` becomes `fable-crew`), then say the project now runs in Claude Code with the harness's Claude plugin, and that `$fable-brief` will refuse slices here while the spec names a fable mode. Stop.
5. Anything else: list the four names and stop.

## Routing table (astra-crew)

| Task class | When | Agent | Model / effort |
| --- | --- | --- | --- |
| `small` | Fully specified change, one or two files, existing tests cover it | `fable_worker_small` | `gpt-5.6-luna` / `max` |
| `routine` | Behavior specified, repo has tests for this kind of change, design settled | `fable_worker_routine` | `gpt-5.6-sol` / `medium` |
| `feature` | Multi-file feature, refactor, or debugging with a clear goal | `fable_worker_feature` | `gpt-5.6-sol` / `high` |
| `hard` | Migrations, hard bugs, slices expected to run over thirty minutes | `fable_worker_hard` | `gpt-5.6-sol` / `xhigh` |

Verification always runs on Astra through `$fable-verify`, in the read-only `fable_verifier` agent.
