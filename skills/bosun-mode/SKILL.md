---
name: bosun-mode
description: "Set or report the harness's provider mode for this project. Six modes: `fable` (default; Fable 5.1 does everything), `fable-opus` (Fable leads, Opus 5.5 implements), `opus` (Opus 5.5 in every role), `fable-crew` (Fable leads, gpt-5.6-sol or gpt-5.6-luna implement through the user's `codex exec`, routed by task class), `astra-crew` and `astra` (GPT-6 Astra leads in Codex; set here, run there). Use when the user says \"switch to fable-crew\", \"use sol/luna for implementation\", \"move this project to codex/astra\", \"what mode are we in\", or \"back to fable mode\"."
argument-hint: "[fable|fable-crew|fable-opus|opus|astra-crew|astra] [--verifier-effort low|medium|high|xhigh|max]"
---

# Bosun mode

The mode is a line in the project's spec, `Provider mode: <mode>`. It lives in the spec so a fresh session reads it with everything else. A spec with no such line is in `fable` mode; the old value `codex` means `fable-crew`.

| Mode | Lead | Implementation | Runs in |
| --- | --- | --- | --- |
| `fable` | Fable 5.1 | Fable 5.1 | Claude Code |
| `fable-crew` | Fable 5.1 | Sol / Luna by task class | Claude Code |
| `fable-opus` | Fable 5.1 | Opus 5.5 at high as a native subagent | Claude Code |
| `opus` | Opus 5.5 | Opus 5.5 (also scout and verifier) | Claude Code |
| `astra-crew` | GPT-6 Astra | Sol / Luna by task class | Codex (desktop app) |
| `astra` | GPT-6 Astra | GPT-6 Astra | Codex (desktop app) |

## Steps

1. Find the spec (`SPEC.md` at the repo root, then the repo's docs convention). If there is none, say so and stop; the mode has nowhere to live until `/bosun-brief` creates the spec.
2. With no arguments at all, only report the current mode (`codex` is reported as `fable-crew`), top-level verifier effort (default `high`), any current-slice override, and the fable-crew routing table when applicable; do not configure agents or edit the spec. Otherwise parse the optional `--verifier-effort <level>` first. Only `low`, `medium`, `high`, `xhigh`, and `max` are valid; reject missing values, unknown flags, and invalid modes before writing anything. This option sets the project's top-level `Verifier effort:` line (beside `Provider mode:`), never a current-slice override. With no mode argument, keep the existing mode. Resolve the top-level default as the option, existing top-level line, or `high`; conflicting top-level lines or invalid stored values are errors. Effort setup is supported only in Claude modes; for an Astra target, report that this option is Claude-only without changing anything. Validate first, run the setup below, and update spec settings only after setup succeeds.

   For a Claude target (`fable`, `fable-crew`, `fable-opus`, `opus`), after any required Codex preflight, run:

   ```bash
   python3 "<plugin root>/scripts/configure-claude-agents.py" --project "<project root>" --mode <target mode> --verifier-effort <default>
   ```

   The mode selects the verifier and scout models; `fable-opus` also installs the worker automatically. `<plugin root>` is the directory containing this plugin's `agents/` and `scripts/`, not the current project; resolve it from this skill's location. This writes project-local `.claude/agents/bosun-scout.md`, `bosun-verifier.md`, and `bosun-verifier-mobile.md`, plus `bosun-worker-opus.md` when requested. It preserves tool/MCP settings, refuses user-owned collisions and symlinks, and never edits installed plugin files. Stop on failure; do not select the new mode or claim effort was applied. Report files written and that current-slice effort overrides still take precedence at verification time. If this creates the project's first `.claude/agents/` directory, tell the user to restart Claude Code before delegating; confirm the local agents are available before running a slice. Do not silently invoke the plugin-scoped agents instead. Model override environment settings can supersede agent model selection on older Claude builds; surface a conflicting `CLAUDE_CODE_SUBAGENT_MODEL` instead of claiming the pinned model ran.

3. With `fable`: set the line to `Provider mode: fable` (add it under the spec's first heading if absent). Report.
4. With `fable-crew` (or `codex`):
   - Run the preflight and report its output verbatim:

     ```bash
     codex --version && codex login status
     ```

     If either fails, do not set the mode. Report the failure and stop; there is no fallback.
   - Set the line to `Provider mode: fable-crew`.
   - Print the routing table and remind the user that a slice can override it with a `Route: <model> / <effort>` line in the spec's current-slice section, and that launching the Fable session at `medium` effort is recommended in this mode.
5. With `astra-crew` or `astra`: set the line to that value. Then say that the project now runs in Codex: open it in the ChatGPT desktop app with the harness's Codex plugin installed (README, "Codex install") and run `$bosun-mode <mode>` there to install the agent files. Nothing else happens in this session; `/bosun-brief` will refuse to run slices while the spec names an Astra mode.
6. With `fable-opus`: configure the project-local agents as above, then set `Provider mode: fable-opus`. Report Fable 5.1 as lead and verifier, `bosun-worker-opus` on `claude-opus-5-5` / `high` as implementer, and the verifier effort default. No Codex login is required. Opus account/model access is confirmed by the first worker spawn, not by writing an agent file. A failed spawn stops the slice; never fall back to Fable, Sol or Luna.
7. With `opus`: configure the local scout and both verifiers on Opus 5.5, then set `Provider mode: opus`. The lead implements directly and uses the local Opus scout and a fresh local Opus verifier. Before any briefing or implementation, confirm the session model is `claude-opus-5-5`; changing the spec does not change the running model. If it differs, use `/model claude-opus-5-5` or relaunch with `claude --model claude-opus-5-5`, then confirm before continuing. Never substitute a Fable lead. Returning to any Fable mode regenerates scout and verifier definitions on Fable 5.1 and requires a Fable lead session.
8. With only `--verifier-effort`: after setup succeeds, set the top-level `Verifier effort:` line and report it, without changing mode. With a mode and the option together, set both after setup succeeds.
9. Anything else: list the six names and stop.

## Routing table (fable-crew and astra-crew)

| Task class | When | Model | Effort |
| --- | --- | --- | --- |
| `small` | Fully specified change, one or two files, existing tests cover it | `gpt-5.6-luna` | `max` |
| `routine` | Behavior specified, repo has tests for this kind of change, design settled | `gpt-5.6-sol` | `medium` |
| `feature` | Multi-file feature, refactor, or debugging with a clear goal | `gpt-5.6-sol` | `high` |
| `hard` | Migrations, hard bugs, slices expected to run over thirty minutes | `gpt-5.6-sol` | `xhigh` |

`ultra` is never passed; the worker script refuses it. In fable-crew mode verification always runs on Fable through `/bosun-verify`; in astra-crew it runs on Astra.
