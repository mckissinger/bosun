# Fable Harness spec: provider modes

Repo: `mckissinger/fable-harness`, plugin version 0.1.2 at the time this spec was written (2026-09-02). The plugin is prompt-only (skills, agents, rules, one hook script); there is no runtime code or test suite. Checks are therefore file reads, `bash -n`, JSON validation, and a dry-run of any script this work adds.

## Outcome

A user can put the harness into a named provider mode. In `fable` mode (the default and today's behavior) Fable 5.1 briefs, implements, verifies, and keeps the spec. In `codex` mode Fable 5.1 still briefs, keeps the spec, and verifies, but the implementation step of each slice is handed to an OpenAI Codex model (`gpt-5.6-sol` or `gpt-5.6-luna`) through the user's own installed `codex exec` CLI, with model and reasoning effort chosen per task class from a routing table. Every codex-mode slice records what it cost and whether it verified first time, so the two modes can be compared after a handful of slices.

## Decisions, in the user's words

- "so far the slices I have been implementing are pretty reasonably chunked, not long horizon at all. I think sol and potentially Luna could do it."
- "with different model and effort routing depending on the task."
- "might be worth setting up a mode selection for it and then we can test it out."
- "ignore my old cc harness data entirely." (No routing or effort choice here is justified by cc-harness metrics.)
- From the research the user accepted without objection: Fable keeps briefing, spec upkeep, and verification; only implementation moves. Sol's `ultra` effort is never used because it auto-delegates, which fights the single-context slice design.
- Settled 2026-09-02 on the assistant's recommendations, user said "good": the scout stays a Fable agent; the worker never commits and Fable commits after review; the routing table is global with only the per-slice `Route:` override; the README recommends launching the Fable session at `medium` in codex mode but nothing enforces it.

## Facts this work relies on (verified 2026-09-02)

- `codex` is codex-cli 0.149.0 at `~/.local/bin/codex`, logged in via ChatGPT. `~/.codex/config.toml` defaults to `gpt-5.6-sol` at `high`.
- Codex model slugs: `gpt-5.6-sol` (efforts low, medium, high, xhigh, max, ultra) and `gpt-5.6-luna` (low, medium, high, xhigh, max).
- `codex exec` flags used: `-m <model>`, `-c model_reasoning_effort="<level>"`, `-C <dir>`, `-s workspace-write`, `--json` (JSONL events to stdout, including token usage), `-o <file>` (final agent message), `--skip-git-repo-check`, `--ephemeral`. `--approve-for-me` exists for approval prompts under workspace-write. `--dangerously-bypass-approvals-and-sandbox` exists and is not used by default.
- Claude Code's Bash tool caps a foreground command at 10 minutes. A background command re-invokes the session when it exits, so long codex runs go to the background and the session waits for that notification rather than polling.
- Public benchmark shape (for routing only): Luna is close to Sol on short agentic coding but far behind on long-context recall, so Luna is for small, fully specified slices; Sol for everything else.

## Design

### Where the mode lives

The mode is a line in the project's spec, `Provider mode: fable` or `Provider mode: codex`, under a heading the brief skill can find. The spec is already the one input a fresh session needs, so the mode travels with it. There is no global default file; a spec without the line is in `fable` mode.

### Routing table (codex mode)

Task class is chosen by the brief, using the same criteria the effort policy in `rules/fable.md` already uses. The brief names the class and the resulting route in the slice brief so it is reviewable before the run.

| Task class | When | Model | Effort |
| --- | --- | --- | --- |
| `small` | Fully specified change, one or two files, existing tests cover it | `gpt-5.6-luna` | `high` |
| `routine` | Behavior specified, repo has tests for this kind of change, design settled | `gpt-5.6-sol` | `medium` |
| `feature` | Multi-file feature, refactor, or debugging with a clear goal | `gpt-5.6-sol` | `high` |
| `hard` | Migrations, hard bugs, slices expected to run over thirty minutes | `gpt-5.6-sol` | `xhigh` |

`ultra` is never passed. `max` is not in the table; the user can override per slice by writing `Route: <model> / <effort>` in the current-slice section before saying go.

### Slice flow in codex mode

1. `/fable-brief` reads the spec, finds `Provider mode: codex`, and writes the brief as today plus two lines: `Task class:` and `Route: <model> / <effort>`.
2. Branch as today. The worker never commits; Fable commits after review.
3. Fable writes a worker prompt file into the checkpoint directory (`~/.claude/fable/workers/<slug>/<slice>/prompt.md`) containing: the slice brief verbatim, the spec's decisions and out-of-scope lists, the scope, test, and targeted-edit rules from `rules/fable.md`, the exact check commands, and the instruction not to commit, not to touch the spec, and to finish with a short report of what changed and which checks it ran.
4. Fable runs `scripts/codex-worker.sh` in the background with the route, the worktree path, the prompt file, and an output directory. The script owns every `codex exec` flag, refuses `ultra`, refuses unknown models, and writes `events.jsonl`, `last-message.md`, and `usage.json` (input, cached input, output tokens, wall seconds, model, effort) into the output directory.
5. When the background command exits, Fable reads the worker's last message and the diff, updates done-condition statuses in the spec, and runs `/fable-verify` exactly as in fable mode. FAIL handling is unchanged: fix findings by sending them back to the worker as a follow-up prompt (same script, same route, prompt = the findings plus the original brief), two FAILs on one finding stops the loop.
6. The report and the spec's slice log both carry the route and the usage numbers.

### Preflight

Before spawning, the script checks `codex --version` and `codex login status`. On failure it exits non-zero with the reason and Fable stops and reports; it never silently falls back to implementing the slice itself.

### Sandbox and approvals

Default is `-s workspace-write` with `--approve-for-me`, cwd set to the worktree, plus `--skip-git-repo-check` and `--ephemeral`. Network access inside the sandbox is off by default; a slice that needs `npm install` or similar sets `Worker network: yes` in its brief and the script passes `-c sandbox_workspace_write.network_access=true`. This is the assumption most likely to change after the first real run; see lessons.

## Done-conditions

Status values: `todo`, `in progress`, `done`, `verified <evidence>`, `human-check`.

1. `todo` `rules/fable.md` has a "Provider mode" section stating the two modes, where the mode line lives in the spec, the routing table above, the `ultra` ban, and that verification always runs on Fable.
2. `todo` `skills/fable-brief/SKILL.md` reads the mode from the spec and, in codex mode, adds `Task class:` and `Route:` lines to the brief template and replaces step 6 (Execute) with the worker flow above (prompt file, background script run, wait for exit, read diff and last message, update statuses). Fable mode behavior is unchanged word for word except where the mode branch is inserted.
3. `todo` A new skill `skills/fable-mode/SKILL.md` (`/fable-mode <fable|codex>`) sets or reports the mode line in the spec, prints the routing table, and in codex mode runs the preflight and reports the result. With no argument it reports the current mode.
4. `todo` `scripts/codex-worker.sh` exists, is executable, passes `bash -n`, and: takes `--model`, `--effort`, `--cwd`, `--prompt-file`, `--out-dir`, optional `--network`; rejects effort `ultra` and any model other than the two slugs with a non-zero exit and a message; supports `--dry-run` which prints the exact `codex exec` argv and exits 0 without spawning; on a real run writes `events.jsonl`, `last-message.md`, and `usage.json` into `--out-dir`.
5. `todo` `scripts/codex-worker.sh --dry-run` for each of the four routing rows prints an argv containing the right `-m`, `model_reasoning_effort`, `-s workspace-write`, `--approve-for-me`, `--json`, `-o`, `--skip-git-repo-check`, `--ephemeral`, and no `--dangerously-*` flag.
6. `todo` `skills/fable-verify/SKILL.md` gains one sentence: in codex mode the verifier prompt names the worker model and effort, and FAIL findings are returned to the worker through the same script rather than fixed by Fable.
7. `todo` `README.md` documents the mode, the routing table, `/fable-mode`, the worker script, the no-fallback preflight rule, and the sandbox default; the "What is in the plugin" table gains the new rows.
8. `todo` `scripts/session-start.sh` prints the provider mode next to the spec path when the spec has a mode line.
9. `todo` `.claude-plugin/plugin.json` and the marketplace manifest bump to `0.2.0` and stay valid JSON.
10. `todo` The spec template guidance in `fable-brief` ("No spec yet") includes an optional `Provider mode:` line so new specs can start in codex mode.
11. `human-check` One real slice on a throwaway project runs end to end in codex mode: brief, background worker, verify, report with usage numbers. The user judges output quality against a Fable-mode slice of similar size.

## Undecided

(none)

## Out of scope

- Any change to fable-mode behavior beyond inserting the mode branch.
- A cost ledger, dashboard, or budget cap. Usage numbers go in the spec's slice log and the report only.
- Porting the verifier or the brief to Codex. Both stay on Fable.
- Codex hooks, guard scripts, or hook-trust flags. The worker is bounded by the sandbox and the prompt only.
- `gpt-5.6-terra` or any model not in the table.
- Parallel workers.

## Current slice

Outcome: the plugin gains a `codex` provider mode that routes a slice's implementation to Sol or Luna through `scripts/codex-worker.sh`, with Fable briefing and verifying.
Done-conditions: 1 through 10 above (11 is human-check and follows on a throwaway project).
Out of scope: see the section above; in particular no change to fable-mode wording beyond the inserted branch, no hooks, no scout routing.
Assumptions: the mode line is matched as a line starting with `Provider mode:` anywhere in the spec; `usage.json` is built from the last `token_count`-style usage event in the codex JSONL and, if none is present, records nulls rather than failing; the network toggle uses `sandbox_workspace_write.network_access` as documented for codex config.
Effort assumed: high (session default; not chosen at launch).
Checks: `bash -n scripts/*.sh`; `python3 -c 'import json;json.load(open(".claude-plugin/plugin.json"));json.load(open(".claude-plugin/marketplace.json"))'`; `scripts/codex-worker.sh --dry-run` for each routing row and for the `ultra` and unknown-model rejections.
Branch: `provider-modes`

## Slice log

(empty; each codex-mode slice appends: date, slice name, task class, route, first-verify verdict, usage)

## Lessons

(empty)
