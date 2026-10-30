---
name: bosun-mode
description: "Set or report the harness's provider mode for this project. Three modes: `fable` (default; Fable 5.1 does everything), `fable-opus` (Fable leads, Opus 5.5 implements), `opus` (Opus 5.5 in every role). Use when the user says \"switch to opus\", \"use opus for implementation\", \"what mode are we in\", or \"back to fable mode\"."
argument-hint: "[fable|fable-opus|opus] [--verifier-effort low|medium|high|xhigh|max]"
---

# Bosun mode

The mode is a line in the project's spec, `Provider mode: <mode>`. It lives in the spec so a fresh session reads it with everything else. A spec with no such line is in `fable` mode. The values `codex`, `fable-crew`, `astra-crew` and `astra` were removed in 0.18.0 with the Codex plugin and the Codex worker.

| Mode | Lead | Implementation |
| --- | --- | --- |
| `fable` | Fable 5.1 | Fable 5.1 |
| `fable-opus` | Fable 5.1 | Opus 5.5 at high as a native subagent |
| `opus` | Opus 5.5 | Opus 5.5 (also scout and verifier) |

## Steps

1. Find the spec (`SPEC.md` at the repo root, then the repo's docs convention). If there is none, say so and stop; the mode has nowhere to live until `/bosun-brief` creates the spec.
2. With no arguments at all, only report the current mode (a removed value is reported as removed, with the three modes to choose from), top-level verifier effort (default `high`), and any current-slice override; do not configure agents or edit the spec. Otherwise parse the optional `--verifier-effort <level>` first. Only `low`, `medium`, `high`, `xhigh`, and `max` are valid; reject missing values, unknown flags, and invalid modes before writing anything. This option sets the project's top-level `Verifier effort:` line (beside `Provider mode:`), never a current-slice override. With no mode argument, keep the existing mode; if the stored mode is a removed value, stop as step 7 says before running setup. Resolve the top-level default as the option, existing top-level line, or `high`; conflicting top-level lines or invalid stored values are errors. Validate first, run the setup below, and update spec settings only after setup succeeds.

   For any target mode, run:

   ```bash
   python3 "<plugin root>/scripts/configure-claude-agents.py" --project "<project root>" --mode <target mode> --verifier-effort <default>
   ```

   The mode selects the verifier and scout models; `fable-opus` also installs the worker automatically. `<plugin root>` is the directory containing this plugin's `agents/` and `scripts/`, not the current project; resolve it from this skill's location. This writes project-local `.claude/agents/bosun-scout.md`, `bosun-verifier.md`, and `bosun-verifier-mobile.md`, plus `bosun-worker-opus.md` when requested. It preserves tool/MCP settings, refuses user-owned collisions and symlinks, and never edits installed plugin files. Stop on failure; do not select the new mode or claim effort was applied. Report files written and that current-slice effort overrides still take precedence at verification time. If this creates the project's first `.claude/agents/` directory, tell the user to restart Claude Code before delegating; confirm the local agents are available before running a slice. Do not silently invoke the plugin-scoped agents instead. Model override environment settings can supersede agent model selection on older Claude builds; surface a conflicting `CLAUDE_CODE_SUBAGENT_MODEL` instead of claiming the pinned model ran.

3. With `fable`: set the line to `Provider mode: fable` (add it under the spec's first heading if absent). Report.
4. With `fable-opus`: configure the project-local agents as above, then set `Provider mode: fable-opus`. Report Fable 5.1 as lead and verifier, `bosun-worker-opus` on `claude-opus-5-5` / `high` as implementer, and the verifier effort default. Opus account/model access is confirmed by the first worker spawn, not by writing an agent file. A failed spawn stops the slice; never fall back to Fable.
5. With `opus`: configure the local scout and both verifiers on Opus 5.5, then set `Provider mode: opus`. The lead implements directly and uses the local Opus scout and a fresh local Opus verifier. Before any briefing or implementation, confirm the session model is `claude-opus-5-5`; changing the spec does not change the running model. If it differs, use `/model claude-opus-5-5` or relaunch with `claude --model claude-opus-5-5`, then confirm before continuing. Never substitute a Fable lead. Returning to any Fable mode regenerates scout and verifier definitions on Fable 5.1 and requires a Fable lead session.
6. With only `--verifier-effort`: after setup succeeds, set the top-level `Verifier effort:` line and report it, without changing mode. With a mode and the option together, set both after setup succeeds.
7. Anything else, including the removed values `codex`, `fable-crew`, `astra-crew` and `astra`: list the three names and stop without changing anything.
