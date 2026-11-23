---
name: bosun-mode
description: "Set up or report Bosun's agents for this project and its verifier effort. Bosun runs on Opus 5.5 in every role, so there is one mode, `opus`. Use when the local scout and verifier agents are missing or stale, when the user says \"set the verifier effort\", \"what mode are we in\", or \"set up the agents\", or when a spec still names a removed mode."
argument-hint: "[opus] [--verifier-effort low|medium|high|xhigh|max]"
---

# Bosun mode

Bosun runs on Opus 5.5 (`claude-opus-5-5`) in every role (core rules, "Model"). This skill writes the project-local scout and verifier agents, sets the project's verifier effort, and reports both. A spec may carry `Provider mode: opus` under its first heading; a spec without the line is the same. `fable` and `fable-opus` were removed in 0.24.0, and `codex`, `fable-crew`, `astra-crew` and `astra` in 0.18.0.

## Steps

1. Find the spec (`SPEC.md` at the repo root, then the repo's docs convention). If there is none, say so and stop; the settings have nowhere to live until `/bosun-brief` creates the spec.
2. With no arguments, only report: the mode (`opus`, or the removed value the spec names, with what to do about it), the top-level verifier effort (default `high`), and any override in the current slice's brief. Do not configure agents or edit the spec.
3. Otherwise validate before writing anything. The only mode argument accepted is `opus`. The only option is `--verifier-effort <level>`, with `low`, `medium`, `high`, `xhigh` or `max`; reject a missing value, an unknown flag, or another mode. The option sets the project's top-level `Verifier effort:` line, never a slice's override. Resolve the top-level default as the option, the existing top-level line, or `high`; conflicting top-level lines or an invalid stored value are errors.
4. Run:

   ```bash
   python3 "<plugin root>/scripts/configure-claude-agents.py" --project "<project root>" --verifier-effort <default>
   ```

   `<plugin root>` is the directory holding this plugin's `agents/` and `scripts/`, not the current project; resolve it from this skill's location. This writes project-local `.claude/agents/bosun-scout.md`, `bosun-verifier.md` and `bosun-verifier-mobile.md` on `claude-opus-5-5`. It preserves tool and MCP settings, refuses user-owned collisions and symlinks, and never edits installed plugin files. Stop on failure, without changing the spec or claiming the effort was applied. If this creates the project's first `.claude/agents/` directory, tell the user to restart Claude Code before delegating. Surface a conflicting `CLAUDE_CODE_SUBAGENT_MODEL` setting instead of claiming the pinned model ran.
5. After setup succeeds: when the spec names a removed mode, change that line to `Provider mode: opus`; when `--verifier-effort` was given, set the top-level `Verifier effort:` line, adding it near the top of the spec when it is missing. Report the files written, the verifier effort, and that an override in the current slice's brief still takes precedence at verification time.
6. Remind the user that the session itself must run on `claude-opus-5-5`: a spec line cannot change it (`/model claude-opus-5-5`, or relaunch with `claude --model claude-opus-5-5`).
