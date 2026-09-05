# Fable Harness spec

Repo: `mckissinger/fable-harness`, plugin version 0.1.2 at the time this spec was written (2026-09-02). The plugin is prompt-only (skills, agents, rules, one hook script); there is no runtime code or test suite. Checks are therefore file reads, `bash -n`, JSON validation, and a dry-run of any script this work adds.

## Outcome

A user can put the harness into a named provider mode. In `fable` mode (the default and today's behavior) Fable 5.1 briefs, implements, verifies, and keeps the spec. In `codex` mode Fable 5.1 still briefs, keeps the spec, and verifies, but the implementation step of each slice is handed to an OpenAI Codex model (`gpt-5.6-sol` or `gpt-5.6-luna`) through the user's own installed `codex exec` CLI, with model and reasoning effort chosen per task class from a routing table. Every codex-mode slice records what it cost and whether it verified first time, so the two modes can be compared after a handful of slices.

Second outcome (slice 3, 2026-09-03): the harness can keep working instead of idling. A `Run policy:` line lets `/fable-brief` run slice after slice until something blocks it, use a codex worker's run time to stage the next brief, re-validate that staged brief against what actually landed, and, when the spec has no runnable work left, say so and ask what next with proposals drawn from accumulated follow-ups.

Third outcome (slice 4, 2026-09-04): the harness runs on either Claude Code or Codex. Four named provider modes replace the two: `fable` (Fable 5.1 does everything, Claude Code), `fable-crew` (Fable leads, Sol and Luna implement by task class, Claude Code; today's `codex`), `astra-crew` (GPT-6 Astra leads, Sol and Luna implement by task class, Codex), and `astra` (Astra does everything, Codex). The repo ships a second plugin for Codex under `codex/` with the same spec contract, so a project can move between the two harnesses by changing one line.

## Decisions, in the user's words

- "so far the slices I have been implementing are pretty reasonably chunked, not long horizon at all. I think sol and potentially Luna could do it."
- "with different model and effort routing depending on the task."
- "might be worth setting up a mode selection for it and then we can test it out."
- "no Luna should be on max. it is so cheap so I dont care" (2026-09-03; the `small` row moved from Luna/high to Luna/max.)
- "I notice sometimes I just sit around in a session waiting when fable could be working on something else or at least getting something else started. Basically it is nor proactive." (2026-09-03)
- "making sure there is actually more work on the road map of the spec, if there is not, fable should ask us what next." (2026-09-03)
- "if something materially changes on the previous slice that we are waiting to complete it may need to edit the brief it wrote." (2026-09-03)
- Agreed 2026-09-03 on the assistant's recommendation, user said "sounds good" then "lets implement": a slice cap like max 3 is the right first setting; proposals for new work are never promoted into done-conditions by Fable; a staged brief is only pre-written when the next slice does not depend on the unfinished one.
- "I would like to update the plugin to be able to use either Codex or Claude Code with multiple configurations. The existing configurations we have now, but a full Codex version where, instead of Fable 5, it's using Astra 6, the new model that just came out, and then it's using Soul and Luna, just like it is for work." (2026-09-04; "Soul" is Sol, "for work" is the worker.)
- "We wouldn't run it in Claude if it was fully Codex." "Verification will run on Astra in mode 3." "Ultimately, when we're using Astra, we'll solely be in Codex via the desktop app." (2026-09-04)
- "I agree with your mode names." (2026-09-04: `fable`, `fable-crew`, `astra-crew`, `astra`; `codex` stays accepted as an alias for `fable-crew`.)
- "ignore my old cc harness data entirely." (No routing or effort choice here is justified by cc-harness metrics.)
- From the research the user accepted without objection: Fable keeps briefing, spec upkeep, and verification; only implementation moves. Sol's `ultra` effort is never used because it auto-delegates, which fights the single-context slice design.
- Settled 2026-09-02 on the assistant's recommendations, user said "good": the scout stays a Fable agent; the worker never commits and Fable commits after review; the routing table is global with only the per-slice `Route:` override; the README recommends launching the Fable session at `medium` in codex mode but nothing enforces it.

## Facts this work relies on (verified 2026-09-02)

- `codex` is codex-cli 0.149.0 at `~/.local/bin/codex`, logged in via ChatGPT. `~/.codex/config.toml` defaults to `gpt-5.6-sol` at `high`.
- Codex model slugs: `gpt-5.6-sol` (efforts low, medium, high, xhigh, max, ultra) and `gpt-5.6-luna` (low, medium, high, xhigh, max).
- `codex exec` flags used: `-m <model>`, `-c model_reasoning_effort="<level>"`, `-C <dir>`, `--json` (JSONL events to stdout, including token usage), `-o <file>` (final agent message), `--skip-git-repo-check`, `--ephemeral`. `--approve-for-me` routes approval prompts through automatic review and itself selects the workspace-write sandbox; codex 0.149.0 rejects an explicit `-s` alongside it (found by the smoke run in this slice). `--dangerously-bypass-approvals-and-sandbox` exists and is not used by default.
- Claude Code's Bash tool caps a foreground command at 10 minutes. A background command re-invokes the session when it exits, so long codex runs go to the background and the session waits for that notification rather than polling.
- GPT-6 Astra (verified 2026-09-04): Codex slug `gpt-6-astra`; efforts low, medium, high, xhigh, max, ultra (ultra auto-delegates, as Sol's does); 1,050,000-token context, 128,000 max output. Needs codex-cli 0.153.1 or later. The user's login reaches it (a probe from codex-cli 0.149.0 failed only with "requires a newer version of Codex"); the npm CLI is 0.149.0 and the ChatGPT desktop app on this machine bundles codex-cli 0.152.0, so both are behind at the time of writing. Astra modes run in the desktop app, not from Claude Code.
- Codex plugins (verified 2026-09-04 from the OpenAI docs): manifest at `.codex-plugin/plugin.json` (`name`, `version`, `description`, `skills`, `hooks`, `interface`), `skills/<name>/SKILL.md` with `name` and `description` frontmatter, `hooks/hooks.json` in the same shape as Claude Code's with a `SessionStart` event whose stdout JSON `{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"..."}}` injects context; `PLUGIN_ROOT` and `CLAUDE_PLUGIN_ROOT` are set for hook commands. A repo marketplace lives at `.agents/plugins/marketplace.json` (legacy `.claude-plugin/marketplace.json` also read) and installs with `codex plugin marketplace add <path or owner/repo>` then `codex plugin add`. Plugin-bundled hooks are skipped until the user reviews and trusts them once in the Codex UI. Hooks under `codex exec` are undocumented.
- Codex subagents (verified 2026-09-04): custom agents are one TOML file each under `~/.codex/agents/` or `<repo>/.codex/agents/` with `name`, `description`, `developer_instructions`, optional `model`, `model_reasoning_effort`, `sandbox_mode` (`read-only` allowed). Plugins do not bundle agents. The lead delegates by asking in the prompt; Codex spawns, waits, and closes threads itself. `[agents]` in config.toml sets `default_subagent_model`, `default_subagent_reasoning_effort`, and concurrency. Subagents start without the parent's conversation.
- Public benchmark shape (for routing only): Luna is close to Sol on short agentic coding but far behind on long-context recall, so Luna is for small, fully specified slices; Sol for everything else.

## Design

### Where the mode lives

The mode is a line in the project's spec, `Provider mode: <mode>` (four values, see "Provider modes (four)" below; `codex` is read as `fable-crew`), under a heading the brief skill can find. The spec is already the one input a fresh session needs, so the mode travels with it. There is no global default file; a spec without the line is in `fable` mode.

### Routing table (fable-crew and astra-crew)

Task class is chosen by the brief, using the same criteria the effort policy in `rules/fable.md` already uses. The brief names the class and the resulting route in the slice brief so it is reviewable before the run.

| Task class | When | Model | Effort |
| --- | --- | --- | --- |
| `small` | Fully specified change, one or two files, existing tests cover it | `gpt-5.6-luna` | `max` |
| `routine` | Behavior specified, repo has tests for this kind of change, design settled | `gpt-5.6-sol` | `medium` |
| `feature` | Multi-file feature, refactor, or debugging with a clear goal | `gpt-5.6-sol` | `high` |
| `hard` | Migrations, hard bugs, slices expected to run over thirty minutes | `gpt-5.6-sol` | `xhigh` |

`ultra` is never passed. Luna runs at `max` because its cost is low enough that the user does not care to save on it; Sol never routes to `max` by default. The user can override per slice by writing `Route: <model> / <effort>` in the current-slice section before saying go.

### Slice flow in fable-crew mode

1. `/fable-brief` reads the spec, finds `Provider mode: fable-crew` (or its alias `codex`), and writes the brief as today plus two lines: `Task class:` and `Route: <model> / <effort>`.
2. Branch as today. The worker never commits; Fable commits after review.
3. Fable writes a worker prompt file into the checkpoint directory (`~/.claude/fable/workers/<slug>/<slice>/prompt.md`) containing: the slice brief verbatim, the spec's decisions and out-of-scope lists, the scope, test, and targeted-edit rules from `rules/fable.md`, the exact check commands, and the instruction not to commit, not to touch the spec, and to finish with a short report of what changed and which checks it ran.
4. Fable runs `scripts/codex-worker.sh` in the background with the route, the worktree path, the prompt file, and an output directory. The script owns every `codex exec` flag, refuses `ultra`, refuses unknown models, and writes `events.jsonl`, `last-message.md`, and `usage.json` (input, cached input, output tokens, wall seconds, model, effort) into the output directory.
5. When the background command exits, Fable reads the worker's last message and the diff, updates done-condition statuses in the spec, and runs `/fable-verify` exactly as in fable mode. FAIL handling is unchanged: fix findings by sending them back to the worker as a follow-up prompt (same script, same route, prompt = the findings plus the original brief), two FAILs on one finding stops the loop.
6. The report and the spec's slice log both carry the route and the usage numbers.

### Preflight

Before spawning, the script checks `codex --version` and `codex login status`. On failure it exits non-zero with the reason and Fable stops and reports; it never silently falls back to implementing the slice itself.

### Sandbox and approvals

Default is `--approve-for-me` (which selects the workspace-write sandbox), cwd set to the worktree, plus `--skip-git-repo-check` and `--ephemeral`. Network access inside the sandbox is off by default; a slice that needs `npm install` or similar sets `Worker network: yes` in its brief and the script passes `-c sandbox_workspace_write.network_access=true`. This is the assumption most likely to change after the first real run; see lessons.

### Provider modes (four)

| Mode | Lead | Implementation | Harness |
| --- | --- | --- | --- |
| `fable` | Fable 5.1 | Fable 5.1 | Claude Code plugin (repo root) |
| `fable-crew` | Fable 5.1 | Sol / Luna by task class via `scripts/codex-worker.sh` | Claude Code plugin |
| `astra-crew` | GPT-6 Astra | Sol / Luna by task class as Codex subagents | Codex plugin (`codex/`) |
| `astra` | GPT-6 Astra | GPT-6 Astra | Codex plugin |

`Provider mode: codex` is read as `fable-crew`. A spec without the line is `fable`. The Claude Code plugin refuses to run a slice in an `astra*` mode and says to open the project in Codex; the Codex plugin refuses `fable*` modes symmetrically. The spec, its sections, the run policy, and the routing table are identical across harnesses, so switching is one line.

### Codex plugin layout

The Codex plugin is a sibling, not a shared-skills refactor: `codex/.codex-plugin/plugin.json`, `codex/rules/astra.md`, `codex/skills/<fable-brief|fable-verify|fable-checkpoint|fable-mode>/SKILL.md`, `codex/hooks/hooks.json`, `codex/scripts/session-start.sh`, `codex/agents/*.toml`; the repo-root `.agents/plugins/marketplace.json` points at `./codex`. Duplicated wording is the price of leaving the Claude plugin's fable-mode text untouched. The Codex skills are the Claude ones with: Astra in place of Fable; `$fable-brief` style invocation; Codex subagents in place of the Agent tool and the worker script; and no `usage.json` (the app shows usage; the slice log records the route and the first-verify verdict only).

Agents shipped (installed into `~/.codex/agents/` by `$fable-mode astra-crew` or `$fable-mode astra`, since plugins cannot bundle agents): `fable-scout` (gpt-5.6-luna, medium, read-only), `fable-verifier` (gpt-6-astra, high, read-only, the verifier agent text), and one worker per routing row, `fable-worker-small` (luna/max), `fable-worker-routine` (sol/medium), `fable-worker-feature` (sol/high), `fable-worker-hard` (sol/xhigh), all workspace-write with the worker instructions (no commit, no spec edits, run the checks, report). In `astra-crew` the brief's Execute step asks Astra to delegate the slice to the worker agent named by the task class and wait for it; in `astra` Astra implements itself.

Effort for the Astra lead follows the same ladder and rules as Fable's (chosen at session start in the app's picker, held for the session, `ultra` never used). The SessionStart hook prints `codex/rules/astra.md` unless `~/.codex/AGENTS.md` already carries its heading, then the spec path with mode and run policy, then any checkpoint, as JSON `additionalContext`.

### Run policy

The run policy is a line in the spec, `Run policy: one slice` or `Run policy: until blocked, max N slices`, under the first heading next to `Provider mode:`. A spec without the line is `one slice`. `until blocked` without a `max` means `max 3 slices`. It applies in both provider modes.

Under `one slice`, `/fable-brief` behaves as before: one slice, verify, report, stop.

Under `until blocked`, after a slice verifies (PASS or PASS WITH FOLLOW-UPS), Fable records lessons, commits, pushes, opens a PR for the slice's branch, writes the slice's report, and then, in the same turn, briefs and runs the next slice. Each slice has its own branch (stacked on the previous slice's branch while that is unmerged, the existing rule) and its own PR; PRs are never merged by Fable. The run stops, with a report saying why, at the first of: no runnable done-condition remains; the next runnable done-condition depends on an undecided item; a verify produced two FAILs on the same finding; the codex preflight failed; N slices have been started in this run, counting the first.

A done-condition is runnable when its status is `todo` or `in progress`, it is not `human-check`, and nothing it needs is on the undecided list.

### Exhausted roadmap

When `/fable-brief` finds no runnable done-condition, at the start or between slices under either policy, it does not invent work. It reports that the roadmap is exhausted, lists every open human-check condition and every undecided item as the question the spec records, and proposes candidate next slices drawn from the spec's follow-ups section, each as a draft done-condition marked as a proposal. It ends the turn asking what next. A proposal becomes a done-condition only when the user says so.

### Follow-ups section

The spec gains a "Follow-ups" section: things noticed and not done (verifier follow-ups, pre-existing bugs, deferred items), one line each naming the slice and date they came from. Step 9 of the brief appends to it, the exhausted-roadmap report draws from it, and a line is removed when it becomes a done-condition or the user drops it.

### Staging the next brief (fable-crew and astra-crew)

While the worker runs, under `until blocked` with the cap not reached, Fable identifies the next slice from the spec. If none of its done-conditions depend on what the running slice creates or changes (files it adds or rewrites, interfaces it defines, behavior that must land first), Fable scouts that slice's dependencies, reading only (the worktree may be read, never written, while the worker runs), and writes a staged brief in the brief template to `~/.claude/fable/workers/<slug>/<next-slice>/brief.md` with a first line `Based on: <sha>` naming the worktree's HEAD at staging time. The staged brief does not enter the spec's current-slice section until it runs. If the next slice depends on the running one, the wait is used for scouting only and the notes go to `notes.md` in the same directory. Under `one slice`, nothing is staged. Only the brief is staged; the worker prompt is written from the final brief after re-validation, because it must contain that brief verbatim.

### Re-validating a staged brief

Before a staged brief runs, Fable compares its `Based on:` sha with the worktree's HEAD. If they differ, it re-reads the spec and `git diff <sha>..HEAD`, checks every file path, line reference, and assumption in the brief against what landed, and folds in any follow-ups from the previous slice's verify that fall inside this slice's done-conditions. Only then does the brief go into the spec's current-slice section and the worker prompt get written from it. If the previous slice's verify FAILed, the staged brief waits for the fix loop; if that loop stopped the run, the staged brief stays on disk and the report names its path.

## Done-conditions

Status values: `todo`, `in progress`, `done`, `verified <evidence>`, `human-check`.

1. `verified 2026-09-02 fable-verifier, rules/fable.md:21-34` `rules/fable.md` has a "Provider mode" section stating the two modes, where the mode line lives in the spec, the routing table above, the `ultra` ban, and that verification always runs on Fable.
2. `verified 2026-09-02 fable-verifier, skills/fable-brief/SKILL.md:15-17,56-75` `skills/fable-brief/SKILL.md` reads the mode from the spec and, in codex mode, adds `Task class:` and `Route:` lines to the brief template and replaces step 6 (Execute) with the worker flow above (prompt file, background script run, wait for exit, read diff and last message, update statuses). Fable mode behavior is unchanged word for word except where the mode branch is inserted.
3. `verified 2026-09-02 fable-verifier, skills/fable-mode/SKILL.md` A new skill `skills/fable-mode/SKILL.md` (`/fable-mode <fable|codex>`) sets or reports the mode line in the spec, prints the routing table, and in codex mode runs the preflight and reports the result. With no argument it reports the current mode.
4. `verified 2026-09-02 fable-verifier, scripts/codex-worker.sh; real luna/low run exit 0 with all three files` `scripts/codex-worker.sh` exists, is executable, passes `bash -n`, and: takes `--model`, `--effort`, `--cwd`, `--prompt-file`, `--out-dir`, optional `--network`; rejects effort `ultra` and any model other than the two slugs with a non-zero exit and a message; supports `--dry-run` which prints the exact `codex exec` argv and exits 0 without spawning; on a real run writes `events.jsonl`, `last-message.md`, and `usage.json` into `--out-dir`.
5. `verified 2026-09-02 fable-verifier, four dry-runs plus --network, no --dangerously flag` `scripts/codex-worker.sh --dry-run` for each of the four routing rows prints an argv containing the right `-m`, `model_reasoning_effort`, `--approve-for-me`, `--json`, `-o`, `--skip-git-repo-check`, `--ephemeral`, and no `--dangerously-*` flag.
6. `verified 2026-09-02 fable-verifier, skills/fable-verify/SKILL.md:19` `skills/fable-verify/SKILL.md` gains one sentence: in codex mode the verifier prompt names the worker model and effort, and FAIL findings are returned to the worker through the same script rather than fixed by Fable.
7. `verified 2026-09-02 fable-verifier, README.md:68-87` `README.md` documents the mode, the routing table, `/fable-mode`, the worker script, the no-fallback preflight rule, and the sandbox default; the "What is in the plugin" table gains the new rows.
8. `verified 2026-09-02 fable-verifier, scripts/session-start.sh:35-40, temp-spec run` `scripts/session-start.sh` prints the provider mode next to the spec path when the spec has a mode line.
9. `verified 2026-09-02 fable-verifier, plugin.json:4, marketplace.json:22` `.claude-plugin/plugin.json` and the marketplace manifest bump to `0.2.0` and stay valid JSON.
10. `verified 2026-09-02 fable-verifier, skills/fable-brief/SKILL.md:22` The spec template guidance in `fable-brief` ("No spec yet") includes an optional `Provider mode:` line so new specs can start in codex mode.
11. `human-check` One real slice on a throwaway project runs end to end in codex mode: brief, background worker, verify, report with usage numbers. The user judges output quality against a Fable-mode slice of similar size.

Slice 3, run policy (2026-09-03):

12. `verified 2026-09-03 fable-verifier, rules/fable.md:36-44,17` `rules/fable.md` gains a "Run policy" section stating the line and its two values, the default and the default cap, what happens under `until blocked` (commit, push, PR per slice, next slice in the same turn, PRs never merged), the stop conditions, the runnable definition, the exhausted-roadmap behavior including that Fable never promotes a proposal, and the follow-ups section; the spec-contents list in "The spec" names the follow-ups section.
13. `verified 2026-09-03 fable-verifier, skills/fable-brief/SKILL.md:19-31,52-64,26` `skills/fable-brief/SKILL.md` gains a "Find the run policy" section; step 1 of "Spec exists" checks for a runnable done-condition and, on none, follows the exhausted-roadmap behavior; step 9 appends follow-ups to the spec's follow-ups section and, under `until blocked`, continues with commit, push, PR, report, and the next slice subject to the stop conditions and the count; the "No spec yet" template names the follow-ups section and the optional `Run policy:` line. Existing single-slice wording is unchanged except where these branches are inserted.
14. `verified 2026-09-03 fable-verifier, skills/fable-brief/SKILL.md:91,72` `skills/fable-brief/SKILL.md` "Codex mode" step 2 describes staging: the condition (until blocked, cap not reached, next slice independent of the running one), what is written where (`brief.md` with `Based on: <sha>`, or `notes.md` only when dependent), and that the worktree is never written while the worker runs.
15. `verified 2026-09-03 fable-verifier, skills/fable-brief/SKILL.md:74` `skills/fable-brief/SKILL.md` describes re-validating a staged brief before it runs: sha comparison, diff read, references and assumptions checked, previous verify follow-ups folded in, brief then written into the spec and the worker prompt generated from it; waits on FAIL; stays on disk and is named in the report if the run stopped.
16. `verified 2026-09-03 fable-verifier, skills/fable-verify/SKILL.md:20` `skills/fable-verify/SKILL.md` step 2 names staging the next brief (per `/fable-brief`) as one thing to do while the verifier runs under `until blocked`.
17. `verified 2026-09-03 fable-verifier, skills/fable-checkpoint/SKILL.md:19` `skills/fable-checkpoint/SKILL.md` "Next actions" names the path of any staged brief.
18. `verified 2026-09-03 fable-verifier, scripts/session-start.sh:35-47, four temp-spec runs` `scripts/session-start.sh` prints the run policy next to the provider mode when the spec has a `Run policy:` line, passes `bash -n`, and a temp-spec run shows mode and policy together, mode alone, and policy alone.
19. `verified 2026-09-03 fable-verifier, README.md:57,66,95-101` `README.md` documents the run policy line, the stop conditions, the exhausted-roadmap report, staging and re-validation, and the follow-ups section; "The spec" list gains follow-ups; "Daily use" mentions the line.
20. `verified 2026-09-03 fable-verifier, plugin.json:4, marketplace.json:22` `.claude-plugin/plugin.json` and the marketplace manifest bump to `0.3.0` and stay valid JSON.
Slice 4, Codex port (2026-09-04):

22. `done` Mode names. `rules/fable.md`, `skills/fable-brief/SKILL.md`, `skills/fable-mode/SKILL.md`, `skills/fable-verify/SKILL.md`, `README.md`, and this spec use `fable`, `fable-crew`, `astra-crew`, `astra`; `codex` is documented as an alias for `fable-crew` in the rules, the brief, and the mode skill; `/fable-mode` accepts the four names (and `codex`), preflights codex for `fable-crew`, and for `astra*` sets the line and says the project now runs in Codex; `/fable-brief` in an `astra*` mode stops and says so instead of running.
23. `done` `codex/.codex-plugin/plugin.json` (name `fable-harness`, version `0.4.0`, `skills`, `hooks`, `interface`) and repo-root `.agents/plugins/marketplace.json` (plugin `fable-harness`, local source `./codex`) are valid JSON; with `CODEX_HOME` pointed at a temp dir, `codex plugin marketplace add "$PWD"` then `codex plugin list` shows the plugin.
24. `done` `codex/rules/astra.md` carries the core rules for an Astra lead: effort ladder with the `ultra` ban, the spec contract including follow-ups, the four provider modes, the run policy, delegation to `fable-scout`, finishing through `$fable-verify`. `codex/hooks/hooks.json` declares a `SessionStart` command hook running `codex/scripts/session-start.sh`, which passes `bash -n`, emits `additionalContext` JSON, prints the rules unless `~/.codex/AGENTS.md` has the heading, the spec path with mode and run policy, and any checkpoint; a temp-spec run shows each.
25. `done` `codex/skills/fable-brief/SKILL.md`, `fable-verify`, `fable-checkpoint`, `fable-mode` exist with `name` and `description` frontmatter and port the Claude skills: Astra wording; subagent delegation in place of the Agent tool; `astra-crew` Execute delegates to the worker agent for the task class and waits, `astra` implements directly; run policy, staged briefs, re-validation, and exhausted-roadmap behavior carried over; `fable-mode` installs the agent files into `~/.codex/agents/` for the astra modes, refuses `fable*` modes, and prints the routing table.
26. `done` `codex/agents/` holds `fable-scout.toml`, `fable-verifier.toml`, `fable-worker-small.toml`, `fable-worker-routine.toml`, `fable-worker-feature.toml`, `fable-worker-hard.toml`; each parses with `tomllib`, has `name`, `description`, `developer_instructions`, `model`, `model_reasoning_effort`, `sandbox_mode`; scout and verifier are `read-only`; the four workers carry the routing table's model and effort and the worker instructions (no commit, no spec edits, run the checks, report files and checks).
27. `done` `README.md` has a four-mode table, a "Codex install" section (marketplace add, plugin add, trust the hook, `$fable-mode astra-crew`), a description of how the astra modes run and what differs (native subagents, no usage file, desktop-app requirement of codex-cli 0.153.1+), and Codex rows in "What is in the plugin".
28. `done` `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` bump to `0.4.0` and stay valid JSON.
29. `human-check` After updating the ChatGPT desktop app to a build with codex-cli 0.153.1 or later: install the Codex plugin, trust its hook, run `$fable-mode astra-crew`, and run one slice on a throwaway project end to end (brief, worker subagent, verify on Astra, report). Then one slice in `astra` mode. Compare against the fable and fable-crew slices.
30. `human-check` The Codex session-start hook fires and prints the spec pointer in the desktop app (hooks under the app were not testable from Claude Code).

21. `human-check` On a throwaway project with `Run policy: until blocked, max 2 slices` and three runnable done-conditions, one `/fable-brief` runs two slices, opens two PRs, and stops citing the cap. On a spec whose done-conditions are all verified or human-check, `/fable-brief` reports the exhausted roadmap with proposals and asks what next.

## Undecided

(none)

## Out of scope

- Any change to fable-mode behavior beyond inserting the mode branch.
- A cost ledger, dashboard, or budget cap. Usage numbers go in the spec's slice log and the report only.
- Porting the verifier or the brief to Codex. Both stay on Fable.
- Codex hooks, guard scripts, or hook-trust flags. The worker is bounded by the sandbox and the prompt only.
- `gpt-5.6-terra` or any model not in the table.
- Parallel workers.
- Parallel slices in separate worktrees (slice 3).
- A skill to set the run policy; the line is edited by hand or by asking Fable (slice 3).
- Staging while Fable itself implements in fable mode; there is nothing to wait on (slice 3).
- Machine-checkable dependency syntax between done-conditions; Fable judges dependence from the text (slice 3).
- Sharing one skills directory between the two plugins; the Codex plugin duplicates wording instead (slice 4).
- Running Astra modes from Claude Code, or fable modes from Codex (slice 4).
- A `usage.json` equivalent for Codex subagents; the app's own usage view is the record (slice 4).
- Upgrading the user's codex CLI or desktop app from this harness (slice 4).
- `gpt-5.6-terra` or `gpt-reserve` in any role (slice 4).

## Current slice

Status: in progress 2026-09-04.

Outcome: the harness gains four named provider modes and a sibling Codex plugin under `codex/` so the same spec runs on Claude Code (`fable`, `fable-crew`) or Codex with GPT-6 Astra (`astra-crew`, `astra`).
Done-conditions: 22 through 28 above (29 and 30 are human-check).
Out of scope: see the section above; in particular no shared skills directory, no CLI or app upgrade, no usage file for Codex subagents, no change to `scripts/codex-worker.sh`.
Assumptions: the Astra effort ladder and rules mirror Fable's, with `ultra` banned, because Astra's ultra is documented as auto-delegating like Sol's; workers in `astra-crew` are native Codex subagents (one agent file per routing row) rather than a nested `codex exec`, because a nested CLI inside the sandbox needs network and loses nothing the app does not already show; the scout in astra modes is Luna at medium read-only, the Codex analog of the cheaper-model scout discussed for Claude; agent files are copied into `~/.codex/agents/` by `$fable-mode` because plugins cannot bundle agents; Codex skills are invoked as `$fable-brief` etc., per the plugin docs' `$plugin-creator` example; hook output uses the documented `additionalContext` JSON; `codex plugin` checks run under a temporary `CODEX_HOME` so the user's config is untouched.
Effort assumed: high (session default; not chosen at launch).
Checks: `bash -n scripts/*.sh codex/scripts/*.sh`; JSON validation of the four manifests; `/opt/homebrew/opt/python@3.12/bin/python3.12 -c 'import tomllib,glob;[tomllib.load(open(f,"rb")) for f in glob.glob("codex/agents/*.toml")]'` (the system python3 is 3.9 and lacks tomllib); temp-spec runs of both session-start scripts; `CODEX_HOME=<tmp> codex plugin marketplace add "$PWD" && CODEX_HOME=<tmp> codex plugin list`.
Branch: `codex-port`

## Follow-ups

(noticed and not done; one line each with the slice and date; removed when promoted to a done-condition or dropped by the user)

- provider-modes, 2026-09-02: `scripts/codex-worker.sh:28` help text prints one line too many (`2,16p` should be `2,15p`).
- provider-modes, 2026-09-02: a value flag given last to `scripts/codex-worker.sh` (`--model` with no value) dies with bash's unbound-variable error instead of the script's own message; still non-zero.
- provider-modes, 2026-09-02: `skills/fable-brief/SKILL.md` says the codex block adds "two lines" but it adds three; the "Find the provider mode" line understates which steps change.
- provider-modes, 2026-09-02: this spec's assumption text says `usage.json` comes from the "last token_count-style event"; the script sums every `turn.completed` usage event, which matches what codex emits.
- provider-modes, 2026-09-02: a relative `--out-dir` could split outputs between codex's `-C` cwd and the shell cwd; the documented flow passes absolute paths.
- provider-modes, 2026-09-02: `marketplace.json` `tags` array was reflowed one-per-line by the JSON rewrite; cosmetic.
- run-policy, 2026-09-03: `skills/fable-brief/SKILL.md` step 9 reports before "Until blocked" commits and opens the PR, while the rules, README, and design say commit, push, PR, then report; the per-slice report cannot name its PR. Pick one order.
- run-policy, 2026-09-03: `skills/fable-verify/SKILL.md:20` invites staging under `until blocked` without saying codex mode only, while the brief skill and design scope staging to codex mode. Say which applies.
- run-policy, 2026-09-03: `README.md` "Version" line says 0.2.0; manifests are at 0.3.0 (already stale on main at 0.2.1).
- run-policy, 2026-09-03: the stop condition "next runnable done-condition depends on an undecided item" can never fire, since the runnable definition already excludes those. Drop it or reword.

## Slice log

(each codex-mode slice appends: date, slice name, task class, route, first-verify verdict, usage)

- 2026-09-03, run-policy, fable mode (implemented by Fable), first verify PASS WITH FOLLOW-UPS.
- 2026-09-02, provider-modes, fable mode (this slice was implemented by Fable), first verify PASS WITH FOLLOW-UPS. Smoke run of the worker script only: gpt-5.6-luna / low, 4 s, 16,824 input (8,960 cached), 5 output tokens.

## Lessons

- `codex exec` rejects `-s <sandbox>` together with `--approve-for-me`; the latter already selects the workspace-write sandbox. Found by a real smoke run of `scripts/codex-worker.sh` (2026-09-02, codex-cli 0.149.0) after the dry-run looked fine, so a dry-run of the argv is not proof the argv is accepted. Any flag change to the script needs one real no-op run (Luna, low, "reply OK") before it ships.
