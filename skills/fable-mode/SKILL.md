---
name: fable-mode
description: Set or report the harness's provider mode for this project. `fable` (default) has Fable 5.1 implement each slice itself; `codex` hands implementation to an OpenAI Codex model (gpt-5.6-sol or gpt-5.6-luna) through the user's installed `codex exec`, routed by task class, while Fable briefs, keeps the spec, and verifies. Use when the user says "switch to codex mode", "use sol/luna for implementation", "what mode are we in", or "back to fable mode".
argument-hint: "[fable|codex]"
---

# Fable mode

The mode is a line in the project's spec, `Provider mode: fable` or `Provider mode: codex`. It lives in the spec so a fresh session reads it with everything else. A spec with no such line is in `fable` mode.

## Steps

1. Find the spec (`SPEC.md` at the repo root, then the repo's docs convention). If there is none, say so and stop; the mode has nowhere to live until `/fable-brief` creates the spec.
2. With no argument: report the current mode and, in codex mode, print the routing table below. Stop.
3. With `fable`: set the line to `Provider mode: fable` (add it under the spec's first heading if absent). Report.
4. With `codex`:
   - Run the preflight and report its output verbatim:

     ```bash
     codex --version && codex login status
     ```

     If either fails, do not set the mode. Report the failure and stop; there is no fallback.
   - Set the line to `Provider mode: codex`.
   - Print the routing table and remind the user that a slice can override it with a `Route: <model> / <effort>` line in the spec's current-slice section, and that launching the Fable session at `medium` effort is recommended in this mode.

## Routing table (codex mode)

| Task class | When | Model | Effort |
| --- | --- | --- | --- |
| `small` | Fully specified change, one or two files, existing tests cover it | `gpt-5.6-luna` | `max` |
| `routine` | Behavior specified, repo has tests for this kind of change, design settled | `gpt-5.6-sol` | `medium` |
| `feature` | Multi-file feature, refactor, or debugging with a clear goal | `gpt-5.6-sol` | `high` |
| `hard` | Migrations, hard bugs, slices expected to run over thirty minutes | `gpt-5.6-sol` | `xhigh` |

`ultra` is never passed; the worker script refuses it. Verification always runs on Fable through `/fable-verify`.
