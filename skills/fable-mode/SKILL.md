---
name: fable-mode
description: Set or report the harness's provider mode for this project. Four modes: `fable` (default; Fable 5.1 does everything), `fable-crew` (Fable leads, gpt-5.6-sol or gpt-5.6-luna implement through the user's `codex exec`, routed by task class), `astra-crew` and `astra` (GPT-6 Astra leads in Codex; set here, run there). Use when the user says "switch to fable-crew", "use sol/luna for implementation", "move this project to codex/astra", "what mode are we in", or "back to fable mode".
argument-hint: "[fable|fable-crew|astra-crew|astra]"
---

# Fable mode

The mode is a line in the project's spec, `Provider mode: <mode>`. It lives in the spec so a fresh session reads it with everything else. A spec with no such line is in `fable` mode; the old value `codex` means `fable-crew`.

| Mode | Lead | Implementation | Runs in |
| --- | --- | --- | --- |
| `fable` | Fable 5.1 | Fable 5.1 | Claude Code |
| `fable-crew` | Fable 5.1 | Sol / Luna by task class | Claude Code |
| `astra-crew` | GPT-6 Astra | Sol / Luna by task class | Codex (desktop app) |
| `astra` | GPT-6 Astra | GPT-6 Astra | Codex (desktop app) |

## Steps

1. Find the spec (`SPEC.md` at the repo root, then the repo's docs convention). If there is none, say so and stop; the mode has nowhere to live until `/fable-brief` creates the spec.
2. With no argument: report the current mode (say `fable-crew` if the line says `codex`) and, in fable-crew mode, print the routing table below. Stop.
3. With `fable`: set the line to `Provider mode: fable` (add it under the spec's first heading if absent). Report.
4. With `fable-crew` (or `codex`):
   - Run the preflight and report its output verbatim:

     ```bash
     codex --version && codex login status
     ```

     If either fails, do not set the mode. Report the failure and stop; there is no fallback.
   - Set the line to `Provider mode: fable-crew`.
   - Print the routing table and remind the user that a slice can override it with a `Route: <model> / <effort>` line in the spec's current-slice section, and that launching the Fable session at `medium` effort is recommended in this mode.
5. With `astra-crew` or `astra`: set the line to that value. Then say that the project now runs in Codex: open it in the ChatGPT desktop app with the harness's Codex plugin installed (README, "Codex install") and run `$fable-mode <mode>` there to install the agent files. Nothing else happens in this session; `/fable-brief` will refuse to run slices while the spec names an Astra mode.
6. Anything else: list the four names and stop.

## Routing table (fable-crew and astra-crew)

| Task class | When | Model | Effort |
| --- | --- | --- | --- |
| `small` | Fully specified change, one or two files, existing tests cover it | `gpt-5.6-luna` | `max` |
| `routine` | Behavior specified, repo has tests for this kind of change, design settled | `gpt-5.6-sol` | `medium` |
| `feature` | Multi-file feature, refactor, or debugging with a clear goal | `gpt-5.6-sol` | `high` |
| `hard` | Migrations, hard bugs, slices expected to run over thirty minutes | `gpt-5.6-sol` | `xhigh` |

`ultra` is never passed; the worker script refuses it. In fable-crew mode verification always runs on Fable through `/fable-verify`; in astra-crew it runs on Astra.
