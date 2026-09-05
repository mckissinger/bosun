# Bosun

A harness for autonomous coding runs: one durable spec per project, effort chosen at launch, fresh-context verification, and a checkpoint for stopping mid-slice. Built from Anthropic's Fable 5.1 documentation and Anthropic's guidance for running it in Claude Code, with the source of each rule in "Why each piece exists". It ships as two plugins that share the spec contract. The Claude Code plugin (repo root) runs on Claude Fable 5.1, alone (`fable`) or leading gpt-5.6-sol and gpt-5.6-luna workers through your own `codex` CLI (`fable-crew`). The Codex plugin (`codex/`) runs the same workflow in the ChatGPT desktop app on GPT-6 Astra, alone (`astra`) or leading Sol and Luna as Codex subagents (`astra-crew`). See "Provider modes" and "Codex install".

## Install

```bash
claude plugin marketplace add mckissinger/bosun
claude plugin install bosun@bosun
```

The plugin's core rules load automatically at session start through a hook. To make them part of your global instructions instead (one less thing printed each session), append `rules/fable.md` to `~/.claude/CLAUDE.md`; the hook detects the section heading and stops printing them.

Optional, per the effort doc's "set effort explicitly": add to `~/.claude/settings.json`

```json
{ "modelSettings": { "claude-fable-5-1": { "effortLevel": "high" } } }
```

## Codex install

The Codex plugin lives in `codex/` and installs from this repo's marketplace file:

```bash
codex plugin marketplace add mckissinger/bosun
codex plugin add bosun@bosun
```

Then, in the ChatGPT desktop app: trust the plugin's SessionStart hook when Codex asks (plugin hooks are skipped until reviewed once), open a project, and run `$bosun-mode astra-crew` or `$bosun-mode astra`. That sets the spec line and copies the harness's agent files (`codex/agents/*.toml`) into `~/.codex/agents/`, since Codex plugins cannot bundle agents. GPT-6 Astra needs a Codex build with codex-cli 0.153.1 or later; the app updates itself.

## The shape

```
launch session at the right effort
  -> /bosun-brief   (no spec: write it, stop for review | spec: brief next slice, run)
  -> work, updating spec status as done-conditions land
  -> /bosun-verify  (fresh read-only verifier; marks verified in spec)
  -> report; /bosun-checkpoint only if stopping mid-slice
  -> under "Run policy: until blocked": commit, push, PR, next slice, until something stops it
```

## What is in the plugin

| Piece | Path | Job |
| --- | --- | --- |
| Core rules | `rules/fable.md` | Effort policy, spec contract, scope and test limits, targeted edits, delegation, refusal recovery, finishing |
| `/bosun-brief` | `skills/bosun-brief/SKILL.md` | Creates the spec on first run and stops for review; afterwards briefs a slice and runs it to completion |
| `/bosun-verify` | `skills/bosun-verify/SKILL.md` | Fresh-context verification against the spec, records verified status |
| `/bosun-checkpoint` | `skills/bosun-checkpoint/SKILL.md` | Transient mid-slice state the spec does not hold |
| `/bosun-mode` | `skills/bosun-mode/SKILL.md` | Sets or reports the provider mode line in the spec; preflights codex |
| Codex worker | `scripts/codex-worker.sh` | Runs one slice on gpt-5.6-sol or gpt-5.6-luna via `codex exec`; owns every flag, refuses `ultra`, writes usage |
| `bosun-scout` agent | `agents/bosun-scout.md` | Read-only background investigator, medium effort |
| `bosun-verifier` agent | `agents/bosun-verifier.md` | Read-only verifier, high effort, with Playwright for done-conditions that name a route or screen |
| SessionStart hook | `scripts/session-start.sh` | Loads the rules if needed, points at the spec with its provider mode and run policy, prints any checkpoint; on compaction, tells the model to re-read the spec |
| Codex plugin manifest | `codex/.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json` | The sibling plugin for the ChatGPT desktop app |
| Codex core rules | `codex/rules/astra.md` | The same contract for an Astra lead: effort ladder, spec, modes, run policy, finishing |
| Codex skills | `codex/skills/*/SKILL.md` | `$bosun-brief`, `$bosun-verify`, `$bosun-checkpoint`, `$bosun-mode`, ported for Astra and Codex subagents |
| Codex agents | `codex/agents/*.toml` | `bosun_scout`, `bosun_verifier`, and one worker per routing row, the verifier and workers with Playwright; installed by `$bosun-mode` |
| Codex hook | `codex/hooks/hooks.json`, `codex/scripts/session-start.sh` | Rules, spec pointer, and checkpoint as session context |

Checkpoints are written to `~/.claude/bosun/checkpoints/<project-slug>.md`.

## The spec

`SPEC.md` at the repo root, or wherever the repo's docs convention puts it. It is the only input a fresh session needs. The harness fixes what it must contain, not how it is laid out:

- the outcome
- decisions, in the user's own words
- done-conditions with a status, each checkable by the verifier's tools (git diff, file reads, the repo's checks) or marked human-check
- undecided items, as questions
- out-of-scope items
- the current slice
- follow-ups: things noticed and not done, one line each with the slice and date; the exhausted-roadmap report draws its proposals from here
- lessons: what a fresh session needs to know about this codebase that the repo does not already record

The model chooses the layout per project, keeps it reviewable by a person in one sitting, and reorganizes or splits it when it stops being that. Status is updated as work lands, so a crash mid-run loses little. The test of the spec: with the checkpoint deleted, can a fresh session continue from spec, branch, and git log? If not, the spec is incomplete.

## Daily use

1. Launch at the effort the work needs: `claude --effort high` for most slices, `xhigh` for long runs, migrations, hard bugs. Effort is held for the session; the model cannot change it.
2. New project: `/bosun-brief <task>` with your structures pasted or pointed at. Review the spec it writes, fill in what you can, say go. That is the one planned stop.
3. Existing spec: `/bosun-brief` (optionally naming the slice). It runs to completion, verifies, and reports. With `Run policy: until blocked, max N slices` in the spec it keeps going, one branch and one PR per slice, until something stops it; see "Run policy".
4. Read the report: done-conditions with evidence, follow-ups, anything left out. Human-check conditions are yours.
5. Stopping mid-slice: `/bosun-checkpoint`. The next session in that directory loads it.

## Provider modes

The mode is a line in the project's spec, `Provider mode: <mode>`. No line means `fable`; the old value `codex` means `fable-crew`. `/bosun-mode <mode>` sets it (preflighting `codex --version` and `codex login status` for `fable-crew`); `/bosun-mode` alone reports it.

| Mode | Lead | Implementation | Harness |
| --- | --- | --- | --- |
| `fable` | Fable 5.1 | Fable 5.1 | Claude Code plugin |
| `fable-crew` | Fable 5.1 | Sol / Luna by task class via `scripts/codex-worker.sh` | Claude Code plugin |
| `astra-crew` | GPT-6 Astra | Sol / Luna by task class as Codex subagents | Codex plugin (`codex/` in this repo) |
| `astra` | GPT-6 Astra | GPT-6 Astra | Codex plugin |

The spec, its sections, the run policy, and the routing table are the same in every mode, so moving a project between harnesses is one line. Each plugin refuses the other's modes: `/bosun-brief` in Claude Code stops if the spec names an `astra*` mode, and `$bosun-brief` in Codex stops on a `fable*` mode.

In `fable-crew` mode Fable 5.1 still writes the brief, keeps the spec, commits, and runs `/bosun-verify`. The implementation step of each slice goes to a Codex model through `scripts/codex-worker.sh`, routed by the task class the brief assigns:

| Task class | When | Model | Effort |
| --- | --- | --- | --- |
| `small` | Fully specified change, one or two files, existing tests cover it | `gpt-5.6-luna` | `max` |
| `routine` | Behavior specified, repo has tests for this kind of change, design settled | `gpt-5.6-sol` | `medium` |
| `feature` | Multi-file feature, refactor, or debugging with a clear goal | `gpt-5.6-sol` | `high` |
| `hard` | Migrations, hard bugs, slices expected to run over thirty minutes | `gpt-5.6-sol` | `xhigh` |

A slice overrides the table with `Route: <model> / <effort>` in the spec's current-slice section. `ultra` is never used (it auto-delegates); the script refuses it.

How a fable-crew slice runs: the brief gains `Task class:`, `Route:`, and `Worker network:` lines; Fable writes a self-contained prompt file under `~/.claude/bosun/workers/<slug>/<slice>/`; the worker script runs in the background (Claude Code's foreground Bash caps at ten minutes) and the session continues when it exits; Fable reads the diff and the worker's last message, updates the spec, verifies on Fable, sends FAIL findings back to the worker, and commits once verified. The report and the spec's slice log record the route and the token usage from `usage.json`, so the two modes can be compared after a few slices.

Rules that do not bend: the worker never commits; verification never moves off Fable; if the codex preflight fails the slice stops and says so rather than falling back to Fable. The sandbox default is `--approve-for-me` (which selects the workspace-write sandbox) and no network; a brief that says `Worker network: yes` adds `sandbox_workspace_write.network_access=true` for installs. Recommended: launch the Fable session at `medium` effort in fable-crew mode, since Fable's own work per slice is briefing and review.

Requires the `codex` CLI (tested with codex-cli 0.149.0) logged in with your own account. The harness spawns your unmodified binary; it never handles provider credentials.

**The astra modes.** `astra-crew` and `astra` run in the ChatGPT desktop app through the Codex plugin, with GPT-6 Astra as the lead. Astra briefs, keeps the spec, commits, and verifies through `$bosun-verify`, which spawns the read-only `bosun_verifier` agent (Astra at high). In `astra-crew`, the Execute step asks Astra to delegate the slice to the worker agent named by the task class (`bosun_worker_small` is Luna at max, `bosun_worker_routine` Sol at medium, `bosun_worker_feature` Sol at high, `bosun_worker_hard` Sol at xhigh) and wait for it; in `astra`, Astra implements the slice itself. Three things differ from fable-crew: workers are native Codex subagents rather than a `codex exec` process, so there is no `usage.json` and the slice log records the route and first-verify verdict only (the app's usage view is the cost record); the scout is `bosun_scout`, Luna at medium, read-only; and checkpoints go to `~/.codex/bosun/checkpoints/`. The same rules that do not bend apply: workers never commit, verification is a fresh read-only context, `ultra` is never used.

## Runtime verification

A done-condition may name a route or screen ("`/settings` shows the new toggle") and still count as checkable, because both the implementer and the verifier have a browser.

The implementer runs the app and looks before marking such a done-condition done, and records one evidence line per done-condition: the route, what was checked, and a screenshot path if one was taken. The Fable lead uses the desktop browser pane or Playwright MCP; the Astra lead uses the built-in browser. Sol and Luna workers get Playwright MCP: in fable-crew the brief says `Worker browser: yes` and the worker script passes `--browser`, which binds the server for that run only; in astra-crew the worker agent files carry it always. Screenshots are evidence when appearance matters; the accessibility snapshot is the cheaper check for text and structure. Nobody walks the whole app.

The verifier gets Playwright too (an inline `mcpServers` entry on `bosun-verifier`; an `mcp_servers` block on `bosun_verifier`, which therefore runs `workspace-write` with a never-edit rule, because Codex's read-only sandbox breaks the MCP process). It uses the browser only to re-check the route-or-screen done-conditions, following the implementer's evidence lines, may start the app with the launch command the brief names, stops it afterward, and reports screenshot paths as evidence. Each slice-log line records how many done-conditions named a route or screen and how many the verifier confirmed, so runtime verification can be compared across modes and projects.

Requires `npx` able to fetch or find `@playwright/mcp` and a Chromium; the first run downloads them.

## Run policy

A Claude Code session is turn-based: when the model ends its turn, nothing happens until something wakes it. The default harness ends the turn after every slice, so the user waits between slices, and in fable-crew mode the session idles while the worker runs. The run policy removes most of that idle time without changing what gets built.

The policy is a line in the spec next to the provider mode: `Run policy: one slice` (the default; no line means the same) or `Run policy: until blocked, max N slices` (`until blocked` alone means `max 3 slices`). Under `until blocked`, after a slice verifies, Fable commits, pushes, opens a PR for that slice's branch, reports, and briefs the next slice in the same turn. Every slice keeps its own branch and PR; Fable never merges. The run stops, and the report says why, at the first of: no runnable done-condition left; the next one depends on an undecided item; two FAILs on one verify finding; a failed codex preflight; the slice cap. A done-condition is runnable when it is `todo` or `in progress`, not `human-check`, and needs nothing on the undecided list.

**Exhausted roadmap.** When no runnable done-condition remains, under either policy, Fable does not invent work. It reports that the roadmap is exhausted, lists the open human-checks and the undecided questions, proposes next slices drawn from the spec's follow-ups section as clearly marked drafts, and asks what next. A proposal becomes a done-condition only when you say so.

**Staging (fable-crew mode).** While the worker runs, under `until blocked` with the cap not reached, Fable scouts the next slice and, if it does not depend on the running one, writes a staged brief to `~/.claude/bosun/workers/<slug>/<next-slice>/brief.md` with a `Based on: <sha>` line. It never writes to the worktree while the worker owns it. If the next slice does depend on the running one, it scouts only.

**Re-validation.** Before a staged brief runs, Fable compares its `Based on:` sha with HEAD. If the previous slice moved it, Fable re-reads the spec and the landed diff, checks every file reference and assumption in the brief, folds in the previous verify's follow-ups that belong to this slice, and only then writes the brief into the spec and generates the worker prompt from it. A staged brief waits on a FAIL, and stays on disk (named in the report) if the run stopped.

## Why each piece exists

Sources: [Overview](https://platform.claude.com/docs/en/models/fable-5-1/overview), [What's new](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1), [Migration guide](https://platform.claude.com/docs/en/models/fable-5-1/migration-guide), [Prompting Claude Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1), [Effort](https://platform.claude.com/docs/en/build-with-claude/effort), [Refusals and fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback), [Claude Code effort controls](https://code.claude.com/docs/en/model-config).

**Effort is the primary control.** Adaptive thinking is always on and cannot be turned off. Default is `high`. The prompting guide says start at `high`, step down to `medium` or `low` where quality holds, step up to `xhigh` or `max` only where measured. At `low` the model answers from memory instead of searching. At `xhigh` and `max` it may draft a long deliverable in thinking and again in the reply. Claude cannot change effort inside a session, and the effort doc says to hold it constant within a conversation, so effort is chosen at launch and the brief states the level it assumes.

**Sizing.** The guide says Fable 5.1 "can execute very long tasks without much guidance on methodology, especially when the goal is clear," and pairs `xhigh` with runs over thirty minutes. The harness sizes work as outcomes with done-conditions, not step lists, and drains ambiguity once, in the spec, at the one planned stop.

**Finish the whole task.** The guide's autonomous-operation and "Delivering work" blocks are already injected by Claude Code on Fable 5.1, along with the progress-update line and the per-turn batching nudge, so the harness does not repeat them.

**Scope and tests.** The guide's block on keeping changes and tests to what the task asks for is in the core rules verbatim; the guide reports it cuts unrequested additions with no measurable change in task success.

**Targeted edits.** Fable 5.1 rewrites whole files more than Fable 5 did. The guide's one-sentence fix is in the core rules verbatim.

**Delegation.** The guide says letting the lead keep working while subagents run lowers time to completion at similar quality and cost. `bosun-scout` runs in the background; the core rules tell the lead to keep working.

**Safeguard false positives.** The guide names three triggers: compile-check phrasing, lesser-known languages without context, base64 in tool output. The core rules carry the phrasing and a recovery step: rephrase once, then record the blocked step in the spec and move on.

**Verification.** `/bosun-verify` runs a fresh-context, read-only verifier at `high`, the documented starting point, so the judgment is independent of the session that did the work. Two FAILs on the same finding stop the loop and go to the user.

**Runtime verification.** This is the one rule that does not come from the Fable 5.1 model guide, which says nothing about browsers. It comes from Anthropic's guidance for running Fable in Claude Code and from OpenAI's equivalent for Codex: the [Claude Code best practices](https://code.claude.com/docs/en/best-practices) ("Give Claude a check it can run: tests, a build, a screenshot to compare"; "Always provide verification (tests, scripts, screenshots). If you can't verify it, don't ship it"; verification by a second-opinion subagent; show evidence, including screenshots, rather than asserting success), Anthropic's [long-running agents article](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (the coding agent "needed explicit prompting to use browser automation tools and do all testing as a human would", and a browser "dramatically improved performance"), OpenAI's [harness engineering](https://openai.com/index/harness-engineering/) (the Chrome DevTools Protocol wired into the agent runtime so Codex could screenshot, snapshot the DOM, and validate fixes) and the [Codex subagent docs](https://learn.chatgpt.com/docs/agent-configuration/subagents) (a browser-debugging custom agent bound to an MCP server). The model guides on both sides say finish the task and keep tests to what the change warrants; the product guidance says a check for visible behavior is a browser. Both roles get one because the implementer's check is the loop that makes the work correct and the verifier's is the independent gate; self-review measurably favors its own output, so the overlap is the point, and it stays cheap because the verifier re-checks named done-conditions only.

**Lessons.** The prompting guide says Fable 5.1 performs notably better when it can write learnings somewhere for future reference, even a plain markdown file, and gives the format: one lesson per entry with a one-line summary, corrections and confirmed approaches alike with why they mattered, update rather than duplicate, delete what turns out wrong, and skip what the repo or history already records. The harness keeps them as a section of the spec, because every point where the harness already forces a spec read (session start, compaction, the brief) then covers them for free. The section splits into its own file only when it stops being readable in one sitting, by the same rule as the rest of the spec.

**Continuity.** The guide's compaction instruction lists six things a summary must preserve. Claude Code does not expose custom compaction instructions, so the harness keeps expectations in the spec, fires a "re-read the spec" reminder from the SessionStart hook when compaction happens, and uses the checkpoint only for transient mid-slice state.

## Not covered on purpose

- Parallel builder agents. The docs credit the model's gains to long single-context runs; splitting work buys wall-clock at the cost of context and merge work, and there is no evidence yet that wall-clock is the constraint.
- Browser or UI tools for the verifier. UI-only done-conditions are marked human-check instead.
- API-side migration concerns (beta headers, append-only message arrays, `tool_choice`, `input_transformations`, fallback middleware). Claude Code manages the conversation prefix itself. If you call the Messages API directly, read the migration guide's "Preserved thinking" section first.

## Status

Version 0.2.0. Designed from the docs and walked through scenarios on paper; not yet exercised on a real multi-session project. The codex provider mode has not yet run a real slice; its sandbox and network defaults are the part most likely to change after the first one. Expect the first real runs to change it.
