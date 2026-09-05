# Bosun spec

Repo: `mckissinger/bosun` (named `fable-harness` until 2026-09-04; evidence pointers and slice names before that date refer to the old paths, which map one to one onto the new ones), plugin version 0.1.2 at the time this spec was written (2026-09-02). The plugin is prompt-only (skills, agents, rules, one hook script); there is no runtime code or test suite. Checks are therefore file reads, `bash -n`, JSON validation, and a dry-run of any script this work adds.

## Outcome

A user can put the harness into a named provider mode. In `fable` mode (the default and today's behavior) Fable 5.1 briefs, implements, verifies, and keeps the spec. In `codex` mode Fable 5.1 still briefs, keeps the spec, and verifies, but the implementation step of each slice is handed to an OpenAI Codex model (`gpt-5.6-sol` or `gpt-5.6-luna`) through the user's own installed `codex exec` CLI, with model and reasoning effort chosen per task class from a routing table. Every codex-mode slice records what it cost and whether it verified first time, so the two modes can be compared after a handful of slices.

Second outcome (slice 3, 2026-09-03): the harness can keep working instead of idling. A `Run policy:` line lets `/bosun-brief` run slice after slice until something blocks it, use a codex worker's run time to stage the next brief, re-validate that staged brief against what actually landed, and, when the spec has no runnable work left, say so and ask what next with proposals drawn from accumulated follow-ups.

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
- "We should probably rename this harness in general so it's agnostic in terms of naming conventions and not confusing, right?" then "bosun, and yes rename the repo" (2026-09-04). The harness, its plugins, skills, agents, and working directories are named `bosun`; mode values and the two model-specific rules files keep their model names.
- "It seems like the better solution is probably just giving both access to these tools. We could always do this and then assess the sessions across projects to see how things are working." (2026-09-05; implementers and verifiers both get a browser.)
- "make sure that your updates are going to be in line with the initial intent of this harness. When we built this harness we reviewed all of the documentation around the new model Fable 5.1. I'm assuming the methodology would apply to Astro 6, given these are both the top frontier models, so make sure you're not straying from that initial intent." (2026-09-05)
- Agreed 2026-09-05 on the assistant's proposal, user said "proceed": leads get an instruction-only change; Sol/Luna workers and both verifiers get Playwright MCP; the browser is used only for done-conditions that name a route or screen; screenshots are evidence, not a required step; the verifier stays read-only in behavior; the README says plainly that this widens "built only from the Fable 5.1 docs" to Anthropic's guidance for Fable 5.1 in Claude Code.
- "ignore my old cc harness data entirely." (No routing or effort choice here is justified by cc-harness metrics.)
- From the research the user accepted without objection: Fable keeps briefing, spec upkeep, and verification; only implementation moves. Sol's `ultra` effort is never used because it auto-delegates, which fights the single-context slice design.
- Settled 2026-09-02 on the assistant's recommendations, user said "good": the scout stays a Fable agent; the worker never commits and Fable commits after review; the routing table is global with only the per-slice `Route:` override; the README recommends launching the Fable session at `medium` in codex mode but nothing enforces it.

## Facts this work relies on (verified 2026-09-02)

- `codex` is codex-cli 0.149.0 at `~/.local/bin/codex`, logged in via ChatGPT. `~/.codex/config.toml` defaults to `gpt-5.6-sol` at `high`.
- Codex model slugs: `gpt-5.6-sol` (efforts low, medium, high, xhigh, max, ultra) and `gpt-5.6-luna` (low, medium, high, xhigh, max).
- `codex exec` flags used: `-m <model>`, `-c model_reasoning_effort="<level>"`, `-C <dir>`, `--json` (JSONL events to stdout, including token usage), `-o <file>` (final agent message), `--skip-git-repo-check`, `--ephemeral`. `--approve-for-me` routes approval prompts through automatic review and itself selects the workspace-write sandbox; codex 0.149.0 rejects an explicit `-s` alongside it (found by the smoke run in this slice). `--dangerously-bypass-approvals-and-sandbox` exists and is not used by default.
- Claude Code's Bash tool caps a foreground command at 10 minutes. A background command re-invokes the session when it exits, so long codex runs go to the background and the session waits for that notification rather than polling.
- GPT-6 Astra (verified 2026-09-04): Codex slug `gpt-6-astra`; efforts low, medium, high, xhigh, max, ultra (ultra auto-delegates, as Sol's does); 1,050,000-token context, 128,000 max output. Needs codex-cli 0.153.1 or later. The npm CLI was updated to 0.153.4 on 2026-09-04 and a `codex exec -m gpt-6-astra` probe then succeeded; the ChatGPT desktop app on this machine still bundles codex-cli 0.152.0, so the app waits on its own updater. Astra modes run in the desktop app, not from Claude Code.
- Codex plugins (verified 2026-09-04 from the OpenAI docs): manifest at `.codex-plugin/plugin.json` (`name`, `version`, `description`, `skills`, `hooks`, `interface`), `skills/<name>/SKILL.md` with `name` and `description` frontmatter, `hooks/hooks.json` in the same shape as Claude Code's with a `SessionStart` event whose stdout JSON `{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"..."}}` injects context; `PLUGIN_ROOT` and `CLAUDE_PLUGIN_ROOT` are set for hook commands. A repo marketplace lives at `.agents/plugins/marketplace.json` (legacy `.claude-plugin/marketplace.json` also read) and installs with `codex plugin marketplace add <path or owner/repo>` then `codex plugin add`. Plugin-bundled hooks are skipped until the user reviews and trusts them once in the Codex UI. Hooks under `codex exec` are undocumented.
- Codex subagents (verified 2026-09-04): custom agents are one TOML file each under `~/.codex/agents/` or `<repo>/.codex/agents/` with `name`, `description`, `developer_instructions`, optional `model`, `model_reasoning_effort`, `sandbox_mode` (`read-only` allowed). Plugins do not bundle agents. The lead delegates by asking in the prompt; Codex spawns, waits, and closes threads itself. `[agents]` in config.toml sets `default_subagent_model`, `default_subagent_reasoning_effort`, and concurrency. Subagents start without the parent's conversation.
- Runtime verification sources (read 2026-09-05): Anthropic's Claude Code best practices ("Give Claude a check it can run: tests, a build, a screenshot to compare"; "Always provide verification (tests, scripts, screenshots). If you can't verify it, don't ship it"; verification by "a second opinion" subagent in a fresh context; show evidence, including screenshots, rather than asserting success) and the long-running-agents article (Claude "needed explicit prompting to use browser automation tools and do all testing as a human would"; giving it a browser "dramatically improved performance"). OpenAI's harness-engineering article (Chrome DevTools Protocol wired into the agent runtime for screenshots, DOM snapshots, and validating fixes) and the Codex subagent docs (a `browser_debugger` custom agent with an `mcp_servers` block, `workspace-write`). Codex's built-in browser is desktop-app only and not documented for subagents. The Fable 5.1 and GPT-6 model guides themselves say nothing about browsers; they say finish the task, keep tests to what the change warrants, and delegate when it saves time.
- Playwright MCP on this machine (verified 2026-09-05): Claude Code has it at user scope as `npx -y @playwright/mcp@latest --headless --isolated`; the package (0.0.80) and Chromium are cached. Codex probes with a local `python3 -m http.server` page: (A) a `read-only` custom agent with `[mcp_servers.playwright]` spawned but its browser call failed with "The requested module './index.js' does not provide an export named 'default'"; (B) the same agent as `workspace-write` returned the page title; (C) `codex exec` for a worker with `-c mcp_servers.playwright.command="npx"` and `-c mcp_servers.playwright.args=[...]` under `--approve-for-me` returned the page title. So the read-only sandbox breaks the MCP process (npx cannot write), and the verifier agent must be `workspace-write` with a never-edit rule. Follow-up probes of the finished `bosun_verifier` TOML from an Astra lead under `codex exec --approve-for-me`: with the agent on `gpt-5.6-luna` it opened the page and returned the title; with the agent on `gpt-6-astra` (the shipped setting) four runs failed, twice with the same module error as probe A and twice with "Automatic approval review blocked the agent's browser navigation", the CLI's `codex-auto-review` reviewer denying the MCP call. The desktop app uses interactive approvals instead, so whether the Astra verifier can browse there is done-condition 46's human-check; the agent file ships on Astra per the user's decision that verification runs on Astra.
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

1. `/bosun-brief` reads the spec, finds `Provider mode: fable-crew` (or its alias `codex`), and writes the brief as today plus two lines: `Task class:` and `Route: <model> / <effort>`.
2. Branch as today. The worker never commits; Fable commits after review.
3. Fable writes a worker prompt file into the checkpoint directory (`~/.claude/bosun/workers/<slug>/<slice>/prompt.md`) containing: the slice brief verbatim, the spec's decisions and out-of-scope lists, the scope, test, and targeted-edit rules from `rules/fable.md`, the exact check commands, and the instruction not to commit, not to touch the spec, and to finish with a short report of what changed and which checks it ran.
4. Fable runs `scripts/codex-worker.sh` in the background with the route, the worktree path, the prompt file, and an output directory. The script owns every `codex exec` flag, refuses `ultra`, refuses unknown models, and writes `events.jsonl`, `last-message.md`, and `usage.json` (input, cached input, output tokens, wall seconds, model, effort) into the output directory.
5. When the background command exits, Fable reads the worker's last message and the diff, updates done-condition statuses in the spec, and runs `/bosun-verify` exactly as in fable mode. FAIL handling is unchanged: fix findings by sending them back to the worker as a follow-up prompt (same script, same route, prompt = the findings plus the original brief), two FAILs on one finding stops the loop.
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

The Codex plugin is a sibling, not a shared-skills refactor: `codex/.codex-plugin/plugin.json`, `codex/rules/astra.md`, `codex/skills/<bosun-brief|bosun-verify|bosun-checkpoint|bosun-mode>/SKILL.md`, `codex/hooks/hooks.json`, `codex/scripts/session-start.sh`, `codex/agents/*.toml`; the repo-root `.agents/plugins/marketplace.json` points at `./codex`. Duplicated wording is the price of leaving the Claude plugin's fable-mode text untouched. The Codex skills are the Claude ones with: Astra in place of Fable; `$bosun-brief` style invocation; Codex subagents in place of the Agent tool and the worker script; and no `usage.json` (the app shows usage; the slice log records the route and the first-verify verdict only).

Agents shipped (installed into `~/.codex/agents/` by `$bosun-mode astra-crew` or `$bosun-mode astra`, since plugins cannot bundle agents): `bosun_scout` (gpt-5.6-luna, medium, read-only), `bosun_verifier` (gpt-6-astra, high, read-only, the verifier agent text), and one worker per routing row, `bosun_worker_small` (luna/max), `bosun_worker_routine` (sol/medium), `bosun_worker_feature` (sol/high), `bosun_worker_hard` (sol/xhigh), all workspace-write with the worker instructions (no commit, no spec edits, run the checks, report). In `astra-crew` the brief's Execute step asks Astra to delegate the slice to the worker agent named by the task class and wait for it; in `astra` Astra implements itself.

Effort for the Astra lead follows the same ladder and rules as Fable's (chosen at session start in the app's picker, held for the session, `ultra` never used). The SessionStart hook prints `codex/rules/astra.md` unless `~/.codex/AGENTS.md` already carries its heading, then the spec path with mode and run policy, then any checkpoint, as JSON `additionalContext`.

### Naming

The harness is `bosun`. Everything derived from the harness name is neutral: plugin and marketplace names (`bosun@bosun` on both sides), skill prefix (`/bosun-brief`, `$bosun-brief`), agent prefix (`bosun-scout`, `bosun-verifier` on Claude; `bosun_scout`, `bosun_verifier`, `bosun_worker_*` on Codex), working directories (`~/.claude/bosun/`, `~/.codex/bosun/`), hook messages, and the repo. Model names appear only where they mean the model: mode values (`fable`, `fable-crew`, `astra`, `astra-crew`), `rules/fable.md` and `codex/rules/astra.md` and their headings (which the hooks grep for in the user's global instruction files), and prose about what a model does.

### Runtime verification

A done-condition may name a route or screen ("`/settings` shows the new toggle", "the dashboard renders the chart") and count as checkable by the verifier's tools. The check is a browser: the implementer runs the app and looks, and the verifier re-checks.

Implementers. The Fable and Astra leads use whatever browser tool the session has (the Claude Code desktop browser pane or Playwright MCP; the Codex built-in browser) and need no new tooling. Sol and Luna workers get Playwright MCP: in fable-crew the brief adds `Worker browser: <yes | no>` (yes when any done-condition names a route or screen) and `scripts/codex-worker.sh --browser` passes the Playwright MCP config to `codex exec`; in astra-crew each worker TOML carries a `[mcp_servers.playwright]` block. For every route-or-screen done-condition the implementer records an evidence line: the route, what was checked, and a screenshot path if one was taken. Evidence goes in the report and in the verifier prompt. Screenshots are evidence when appearance matters, not a required step; the accessibility snapshot is the cheaper check for text and structure.

Verifiers. `bosun-verifier` (Claude) gets `mcp__playwright` in its tools and an inline `mcpServers` Playwright entry that starts with the agent and stops with it. `bosun_verifier` (Codex) gets a `[mcp_servers.playwright]` block and moves to `sandbox_mode = "workspace-write"` because the read-only sandbox breaks the MCP process; its instructions keep it read-only in behavior. Both use the browser only to re-check done-conditions that name a route or screen, following the implementer's evidence as the map, and report screenshot paths as evidence. They may start the app with the launch command the brief names and must stop it afterward. No exploratory walkthroughs.

Slice log. Each entry records how many route-or-screen done-conditions the slice had and how many the verifier confirmed in the browser, so runtime verification can be compared across modes and projects.

What this does not change: effort rules, scope and test rules, the worker never committing or editing the spec, the verifier's verdict format. This is the harness's first rule taken from Anthropic's Claude Code guidance rather than the Fable 5.1 model guide; the README says so.

### Run policy

The run policy is a line in the spec, `Run policy: one slice` or `Run policy: until blocked, max N slices`, under the first heading next to `Provider mode:`. A spec without the line is `one slice`. `until blocked` without a `max` means `max 3 slices`. It applies in both provider modes.

Under `one slice`, `/bosun-brief` behaves as before: one slice, verify, report, stop.

Under `until blocked`, after a slice verifies (PASS or PASS WITH FOLLOW-UPS), Fable records lessons, commits, pushes, opens a PR for the slice's branch, writes the slice's report, and then, in the same turn, briefs and runs the next slice. Each slice has its own branch (stacked on the previous slice's branch while that is unmerged, the existing rule) and its own PR; PRs are never merged by Fable. The run stops, with a report saying why, at the first of: no runnable done-condition remains; the next runnable done-condition depends on an undecided item; a verify produced two FAILs on the same finding; the codex preflight failed; N slices have been started in this run, counting the first.

A done-condition is runnable when its status is `todo` or `in progress`, it is not `human-check`, and nothing it needs is on the undecided list.

### Exhausted roadmap

When `/bosun-brief` finds no runnable done-condition, at the start or between slices under either policy, it does not invent work. It reports that the roadmap is exhausted, lists every open human-check condition and every undecided item as the question the spec records, and proposes candidate next slices drawn from the spec's follow-ups section, each as a draft done-condition marked as a proposal. It ends the turn asking what next. A proposal becomes a done-condition only when the user says so.

### Follow-ups section

The spec gains a "Follow-ups" section: things noticed and not done (verifier follow-ups, pre-existing bugs, deferred items), one line each naming the slice and date they came from. Step 9 of the brief appends to it, the exhausted-roadmap report draws from it, and a line is removed when it becomes a done-condition or the user drops it.

### Staging the next brief (fable-crew and astra-crew)

While the worker runs, under `until blocked` with the cap not reached, Fable identifies the next slice from the spec. If none of its done-conditions depend on what the running slice creates or changes (files it adds or rewrites, interfaces it defines, behavior that must land first), Fable scouts that slice's dependencies, reading only (the worktree may be read, never written, while the worker runs), and writes a staged brief in the brief template to `~/.claude/bosun/workers/<slug>/<next-slice>/brief.md` with a first line `Based on: <sha>` naming the worktree's HEAD at staging time. The staged brief does not enter the spec's current-slice section until it runs. If the next slice depends on the running one, the wait is used for scouting only and the notes go to `notes.md` in the same directory. Under `one slice`, nothing is staged. Only the brief is staged; the worker prompt is written from the final brief after re-validation, because it must contain that brief verbatim.

### Re-validating a staged brief

Before a staged brief runs, Fable compares its `Based on:` sha with the worktree's HEAD. If they differ, it re-reads the spec and `git diff <sha>..HEAD`, checks every file path, line reference, and assumption in the brief against what landed, and folds in any follow-ups from the previous slice's verify that fall inside this slice's done-conditions. Only then does the brief go into the spec's current-slice section and the worker prompt get written from it. If the previous slice's verify FAILed, the staged brief waits for the fix loop; if that loop stopped the run, the staged brief stays on disk and the report names its path.

## Done-conditions

Status values: `todo`, `in progress`, `done`, `verified <evidence>`, `human-check`.

1. `verified 2026-09-02 bosun-verifier, rules/fable.md:21-34` `rules/fable.md` has a "Provider mode" section stating the two modes, where the mode line lives in the spec, the routing table above, the `ultra` ban, and that verification always runs on Fable.
2. `verified 2026-09-02 bosun-verifier, skills/bosun-brief/SKILL.md:15-17,56-75` `skills/bosun-brief/SKILL.md` reads the mode from the spec and, in codex mode, adds `Task class:` and `Route:` lines to the brief template and replaces step 6 (Execute) with the worker flow above (prompt file, background script run, wait for exit, read diff and last message, update statuses). Fable mode behavior is unchanged word for word except where the mode branch is inserted.
3. `verified 2026-09-02 bosun-verifier, skills/bosun-mode/SKILL.md` A new skill `skills/bosun-mode/SKILL.md` (`/bosun-mode <fable|codex>`) sets or reports the mode line in the spec, prints the routing table, and in codex mode runs the preflight and reports the result. With no argument it reports the current mode.
4. `verified 2026-09-02 bosun-verifier, scripts/codex-worker.sh; real luna/low run exit 0 with all three files` `scripts/codex-worker.sh` exists, is executable, passes `bash -n`, and: takes `--model`, `--effort`, `--cwd`, `--prompt-file`, `--out-dir`, optional `--network`; rejects effort `ultra` and any model other than the two slugs with a non-zero exit and a message; supports `--dry-run` which prints the exact `codex exec` argv and exits 0 without spawning; on a real run writes `events.jsonl`, `last-message.md`, and `usage.json` into `--out-dir`.
5. `verified 2026-09-02 bosun-verifier, four dry-runs plus --network, no --dangerously flag` `scripts/codex-worker.sh --dry-run` for each of the four routing rows prints an argv containing the right `-m`, `model_reasoning_effort`, `--approve-for-me`, `--json`, `-o`, `--skip-git-repo-check`, `--ephemeral`, and no `--dangerously-*` flag.
6. `verified 2026-09-02 bosun-verifier, skills/bosun-verify/SKILL.md:19` `skills/bosun-verify/SKILL.md` gains one sentence: in codex mode the verifier prompt names the worker model and effort, and FAIL findings are returned to the worker through the same script rather than fixed by Fable.
7. `verified 2026-09-02 bosun-verifier, README.md:68-87` `README.md` documents the mode, the routing table, `/bosun-mode`, the worker script, the no-fallback preflight rule, and the sandbox default; the "What is in the plugin" table gains the new rows.
8. `verified 2026-09-02 bosun-verifier, scripts/session-start.sh:35-40, temp-spec run` `scripts/session-start.sh` prints the provider mode next to the spec path when the spec has a mode line.
9. `verified 2026-09-02 bosun-verifier, plugin.json:4, marketplace.json:22` `.claude-plugin/plugin.json` and the marketplace manifest bump to `0.2.0` and stay valid JSON.
10. `verified 2026-09-02 bosun-verifier, skills/bosun-brief/SKILL.md:22` The spec template guidance in `bosun-brief` ("No spec yet") includes an optional `Provider mode:` line so new specs can start in codex mode.
11. `human-check` One real slice on a throwaway project runs end to end in codex mode: brief, background worker, verify, report with usage numbers. The user judges output quality against a Fable-mode slice of similar size.

Slice 3, run policy (2026-09-03):

12. `verified 2026-09-03 bosun-verifier, rules/fable.md:36-44,17` `rules/fable.md` gains a "Run policy" section stating the line and its two values, the default and the default cap, what happens under `until blocked` (commit, push, PR per slice, next slice in the same turn, PRs never merged), the stop conditions, the runnable definition, the exhausted-roadmap behavior including that Fable never promotes a proposal, and the follow-ups section; the spec-contents list in "The spec" names the follow-ups section.
13. `verified 2026-09-03 bosun-verifier, skills/bosun-brief/SKILL.md:19-31,52-64,26` `skills/bosun-brief/SKILL.md` gains a "Find the run policy" section; step 1 of "Spec exists" checks for a runnable done-condition and, on none, follows the exhausted-roadmap behavior; step 9 appends follow-ups to the spec's follow-ups section and, under `until blocked`, continues with commit, push, PR, report, and the next slice subject to the stop conditions and the count; the "No spec yet" template names the follow-ups section and the optional `Run policy:` line. Existing single-slice wording is unchanged except where these branches are inserted.
14. `verified 2026-09-03 bosun-verifier, skills/bosun-brief/SKILL.md:91,72` `skills/bosun-brief/SKILL.md` "Codex mode" step 2 describes staging: the condition (until blocked, cap not reached, next slice independent of the running one), what is written where (`brief.md` with `Based on: <sha>`, or `notes.md` only when dependent), and that the worktree is never written while the worker runs.
15. `verified 2026-09-03 bosun-verifier, skills/bosun-brief/SKILL.md:74` `skills/bosun-brief/SKILL.md` describes re-validating a staged brief before it runs: sha comparison, diff read, references and assumptions checked, previous verify follow-ups folded in, brief then written into the spec and the worker prompt generated from it; waits on FAIL; stays on disk and is named in the report if the run stopped.
16. `verified 2026-09-03 bosun-verifier, skills/bosun-verify/SKILL.md:20` `skills/bosun-verify/SKILL.md` step 2 names staging the next brief (per `/bosun-brief`) as one thing to do while the verifier runs under `until blocked`.
17. `verified 2026-09-03 bosun-verifier, skills/bosun-checkpoint/SKILL.md:19` `skills/bosun-checkpoint/SKILL.md` "Next actions" names the path of any staged brief.
18. `verified 2026-09-03 bosun-verifier, scripts/session-start.sh:35-47, four temp-spec runs` `scripts/session-start.sh` prints the run policy next to the provider mode when the spec has a `Run policy:` line, passes `bash -n`, and a temp-spec run shows mode and policy together, mode alone, and policy alone.
19. `verified 2026-09-03 bosun-verifier, README.md:57,66,95-101` `README.md` documents the run policy line, the stop conditions, the exhausted-roadmap report, staging and re-validation, and the follow-ups section; "The spec" list gains follow-ups; "Daily use" mentions the line.
20. `verified 2026-09-03 bosun-verifier, plugin.json:4, marketplace.json:22` `.claude-plugin/plugin.json` and the marketplace manifest bump to `0.3.0` and stay valid JSON.
Slice 4, Codex port (2026-09-04):

22. `verified 2026-09-04 bosun-verifier, rules/fable.md:23-32, skills/bosun-brief/SKILL.md:17, skills/bosun-mode/SKILL.md:22-34, README.md:88-97` Mode names. `rules/fable.md`, `skills/bosun-brief/SKILL.md`, `skills/bosun-mode/SKILL.md`, `skills/bosun-verify/SKILL.md`, `README.md`, and this spec use `fable`, `fable-crew`, `astra-crew`, `astra`; `codex` is documented as an alias for `fable-crew` in the rules, the brief, and the mode skill; `/bosun-mode` accepts the four names (and `codex`), preflights codex for `fable-crew`, and for `astra*` sets the line and says the project now runs in Codex; `/bosun-brief` in an `astra*` mode stops and says so instead of running.
23. `verified 2026-09-04 bosun-verifier, codex/.codex-plugin/plugin.json, .agents/plugins/marketplace.json, codex plugin list under temp CODEX_HOME` `codex/.codex-plugin/plugin.json` (name `bosun`, version `0.4.0`, `skills`, `hooks`, `interface`) and repo-root `.agents/plugins/marketplace.json` (plugin `bosun`, local source `./codex`) are valid JSON; with `CODEX_HOME` pointed at a temp dir, `codex plugin marketplace add "$PWD"` then `codex plugin list` shows the plugin.
24. `verified 2026-09-04 bosun-verifier, codex/rules/astra.md:5-68, codex/hooks/hooks.json, six temp hook runs` `codex/rules/astra.md` carries the core rules for an Astra lead: effort ladder with the `ultra` ban, the spec contract including follow-ups, the four provider modes, the run policy, delegation to `bosun_scout`, finishing through `$bosun-verify`. `codex/hooks/hooks.json` declares a `SessionStart` command hook running `codex/scripts/session-start.sh`, which passes `bash -n`, emits `additionalContext` JSON, prints the rules unless `~/.codex/AGENTS.md` has the heading, the spec path with mode and run policy, and any checkpoint; a temp-spec run shows each.
25. `verified 2026-09-04 bosun-verifier, codex/skills/*/SKILL.md; bosun-brief:16-18,31,48,64-72,88; bosun-mode:23-35` `codex/skills/bosun-brief/SKILL.md`, `bosun-verify`, `bosun-checkpoint`, `bosun-mode` exist with `name` and `description` frontmatter and port the Claude skills: Astra wording; subagent delegation in place of the Agent tool; `astra-crew` Execute delegates to the worker agent for the task class and waits, `astra` implements directly; run policy, staged briefs, re-validation, and exhausted-roadmap behavior carried over; `bosun-mode` installs the agent files into `~/.codex/agents/` for the astra modes, sets a `fable*` line and says the project now runs in Claude Code (the mirror of the Claude side), and prints the routing table.
26. `verified 2026-09-04 bosun-verifier, codex/agents/*.toml, tomllib parse, fields and values` `codex/agents/` holds `bosun-scout.toml`, `bosun-verifier.toml`, `bosun-worker-small.toml`, `bosun-worker-routine.toml`, `bosun-worker-feature.toml`, `bosun-worker-hard.toml`; each parses with `tomllib`, has `name` (underscored: `bosun_scout`, `bosun_verifier`, `bosun_worker_small`, and so on, because Codex rejects hyphens in agent names), `description`, `developer_instructions`, `model`, `model_reasoning_effort`, `sandbox_mode`; scout and verifier are `read-only`; the four workers carry the routing table's model and effort and the worker instructions (no commit, no spec edits, run the checks, report files and checks).
27. `verified 2026-09-04 bosun-verifier, README.md:20-29,55-59,90-95,116` `README.md` has a four-mode table, a "Codex install" section (marketplace add, plugin add, trust the hook, `$bosun-mode astra-crew`), a description of how the astra modes run and what differs (native subagents, no usage file, desktop-app requirement of codex-cli 0.153.1+), and Codex rows in "What is in the plugin".
28. `verified 2026-09-04 bosun-verifier, plugin.json:4, marketplace.json:22` `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` bump to `0.4.0` and stay valid JSON.
29. `human-check` After updating the ChatGPT desktop app to a build with codex-cli 0.153.1 or later: install the Codex plugin, trust its hook, run `$bosun-mode astra-crew`, and run one slice on a throwaway project end to end (brief, worker subagent, verify on Astra, report). Then one slice in `astra` mode. Compare against the fable and fable-crew slices.
30. `human-check` The Codex session-start hook fires and prints the spec pointer in the desktop app (hooks under the app were not testable from Claude Code).

Slice 5, rename to bosun (2026-09-04):

31. `verified 2026-09-04 bosun-verifier, git ls-files, grep from the done-condition (five spec-only hits)` No harness-identity token remains: `grep -rniE 'fable-harness|fable harness|fable-(brief|verify|checkpoint|mode|scout|verifier|worker)\b|fable_(scout|verifier|worker)|/fable/'` over tracked `.md`, `.json`, `.sh`, `.toml` files finds nothing except prose about the `fable` mode, the pattern itself, and historical mentions of the old name in this spec. Directories and files are renamed: `skills/bosun-*`, `agents/bosun-*.md`, `codex/skills/bosun-*`, `codex/agents/bosun-*.toml`.
32. `verified 2026-09-04 bosun-verifier, four manifests, codex plugin list under temp CODEX_HOME` Manifests: `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` name the plugin and marketplace `bosun`; `codex/.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json` likewise; the three that carry a version at `0.5.0`, all four valid JSON; under a temp `CODEX_HOME`, `codex plugin marketplace add "$PWD"` then `codex plugin list` shows `bosun@bosun`.
33. `verified 2026-09-04 bosun-verifier, scripts/session-start.sh:27,33, codex/scripts/session-start.sh:29,48, temp runs` Both session-start scripts pass `bash -n`, print `Bosun spec for this project`, and look for checkpoints under `~/.claude/bosun/checkpoints/` and `~/.codex/bosun/checkpoints/`; temp-spec runs show the spec line and a checkpoint. The rules headings (`# Fable 5.1 agentic development`, `# Astra agentic development`) are unchanged so existing global instruction files keep silencing the hooks.
34. `verified 2026-09-04 bosun-verifier, name fields on both sides, tomllib, bosun_scout spawned from Astra (verifier run 3 and the implementer run)` Skill `name` fields are `bosun-brief`, `bosun-verify`, `bosun-checkpoint`, `bosun-mode` on both sides; Claude agents are `bosun-scout` and `bosun-verifier`; Codex agent `name` fields are `bosun_scout`, `bosun_verifier`, `bosun_worker_small`, `bosun_worker_routine`, `bosun_worker_feature`, `bosun_worker_hard`, all parsing with `tomllib`; one real spawn of `bosun_scout` from an Astra lead in a temp project succeeds.
35. `verified 2026-09-04 bosun-verifier, README.md:1,7-8,25-26, rules/fable.md:3, codex/rules/astra.md:3` `README.md` is titled Bosun, installs from `mckissinger/bosun` as `bosun@bosun` on both sides, and its plugin table, mode table, and "Why each piece exists" use the new names; `rules/fable.md` and `codex/rules/astra.md` refer to the Bosun README and the `bosun-*` skills and agents; mode values and model-specific wording are unchanged.
36. `verified 2026-09-04 bosun-verifier, gh repo view, git remote -v` The GitHub repo is renamed to `mckissinger/bosun`, the local `origin` remote points at it, and `gh repo view` reports the new name.
37. `human-check` Reinstall both plugins under the new names (`claude plugin marketplace add mckissinger/bosun`, `claude plugin install bosun@bosun`; `codex plugin marketplace add mckissinger/bosun`, `codex plugin add bosun@bosun`) and remove the old `fable-harness` installs and marketplaces.

Slice 6, runtime verification (2026-09-05):

38. `verified 2026-09-05 bosun-verifier, rules/fable.md:17,63,71, codex/rules/astra.md:18,64,70` `rules/fable.md` and `codex/rules/astra.md`: the spec contract says a done-condition may name a route or screen and is then checked in a browser; "While working" says the implementer runs the app and checks such done-conditions, recording route, what was checked, and screenshot path; "Finishing" says the verifier re-checks them. Effort, scope, and test rules unchanged.
39. `verified 2026-09-05 bosun-verifier, agents/bosun-verifier.md:4-10,16,18` `agents/bosun-verifier.md`: `tools` gains `mcp__playwright`; an `mcpServers` inline Playwright entry (`npx -y @playwright/mcp@latest --headless --isolated`); rules gain the browser-only-for-route-or-screen rule, following the implementer's evidence, screenshot paths as evidence, may start and must stop the app; still never edits.
40. `verified 2026-09-05 bosun-verifier, codex/agents/bosun-verifier.toml:5,10,12,32-34, worker TOMLs:16,19,22-24, tomllib` `codex/agents/bosun-verifier.toml`: `sandbox_mode = "workspace-write"`, a `[mcp_servers.playwright]` block, and the same rules including an explicit never-edit sentence; parses with `tomllib`. `codex/agents/bosun-worker-*.toml`: each gains the same `[mcp_servers.playwright]` block and the implementer's runtime-check instruction with the evidence line.
41. `verified 2026-09-05 bosun-verifier, scripts/codex-worker.sh:28,58-61, dry-runs, implementer real run` `scripts/codex-worker.sh` gains `--browser`, which adds `-c mcp_servers.playwright.command="npx"` and `-c 'mcp_servers.playwright.args=[...]'` to the argv; `--dry-run --browser` shows them and without the flag they are absent; `bash -n` passes; one real no-op run with `--browser` (Luna, low, "reply OK") exits 0 with the three output files.
42. `verified 2026-09-05 bosun-verifier, skills/bosun-brief/SKILL.md:49,52,86,91,95,98,102, codex/skills/bosun-brief/SKILL.md:48,51,87,92` `skills/bosun-brief/SKILL.md` and `codex/skills/bosun-brief/SKILL.md`: step 6 tells the lead to run the app and check route-or-screen done-conditions with the session's browser tool, recording evidence; the report (step 9) carries an `Evidence:` list; the worker prompt carries the same instruction; the fable-crew template gains `Worker browser: <yes | no>` and step 2 passes `--browser` when yes; the slice log line records route-or-screen done-condition counts.
43. `verified 2026-09-05 bosun-verifier, skills/bosun-verify/SKILL.md:19,25, codex/skills/bosun-verify/SKILL.md:18,24` `skills/bosun-verify/SKILL.md` and `codex/skills/bosun-verify/SKILL.md`: the verifier prompt includes the implementer's evidence list and the app launch command when a done-condition names a route or screen; the relay step says screenshot paths are reported as evidence.
44. `verified 2026-09-05 bosun-verifier, README.md:3,53,58,118-126,160` `README.md`: a "Runtime verification" section describing the above for both harnesses, the `Worker browser` line, and the `--browser` flag; "Why each piece exists" gains a paragraph that cites the sources in this spec's facts and states that this rule comes from Anthropic's Claude Code guidance and OpenAI's harness guidance rather than the model guides; the intro sentence "Built only from Anthropic's Fable 5.1 documentation" is amended accordingly; the plugin table rows for the verifiers mention the browser.
45. `verified 2026-09-05 bosun-verifier, three manifests at 0.6.0` `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `codex/.codex-plugin/plugin.json` bump to `0.6.0`, valid JSON.
46. `human-check` On a throwaway web project with one done-condition naming a route: a fable-mode slice where Fable checks the route in a browser and the verifier re-checks it with Playwright, reporting screenshot paths; then the same in fable-crew with `Worker browser: yes`; then in astra-crew in the desktop app.

21. `human-check` On a throwaway project with `Run policy: until blocked, max 2 slices` and three runnable done-conditions, one `/bosun-brief` runs two slices, opens two PRs, and stops citing the cap. On a spec whose done-conditions are all verified or human-check, `/bosun-brief` reports the exhausted roadmap with proposals and asks what next.

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
- Renaming the local working directory or the user's global instruction files; those are the user's (slice 5).
- Chrome DevTools MCP, the Claude-in-Chrome connector, or Codex Computer Use as harness-provided tools; leads may use what their session has (slice 6).
- Exploratory browser walkthroughs by the verifier; it re-checks named done-conditions only (slice 6).
- Bundling the Playwright package or browsers; the harness assumes `npx` can fetch or has cached them (slice 6).

## Current slice

Status: verified PASS WITH FOLLOW-UPS 2026-09-05; the README contradiction the verifier found was fixed before the PR, the rest are follow-ups below. Next: done-condition 46 (human-check) on a throwaway web project, first in fable mode.

Outcome: done-conditions that name a route or screen are checked in a browser by the implementer and re-checked by the verifier, on both harnesses, with evidence in the report.
Done-conditions: 38 through 45 above (46 is human-check).
Out of scope: see the section above; in particular no other browser tools, no exploratory walkthroughs, no bundled browsers, no change to effort, scope, or test rules.
Assumptions: Playwright MCP is invoked as `npx -y @playwright/mcp@latest --headless --isolated` on both sides, matching the user's existing Claude Code configuration; the Codex verifier runs `workspace-write` because probe A showed the read-only sandbox breaks the MCP process, with read-only behavior enforced by instruction; the fable-crew worker gets the browser only when the brief says `Worker browser: yes`, to avoid the npx startup on backend slices, while the astra-crew worker TOMLs carry it always because agent files are static; the verifier may start the app with the brief's launch command, since running the app changes no files.
Effort assumed: high (session default; not chosen at launch).
Checks: `bash -n scripts/*.sh codex/scripts/*.sh`; JSON validation of the three versioned manifests; `/opt/homebrew/opt/python@3.12/bin/python3.12` `tomllib` parse of `codex/agents/*.toml`; `scripts/codex-worker.sh --dry-run` with and without `--browser`; one real `--browser` no-op run; a probe that spawns the updated `bosun_verifier` TOML from Astra against a local page and gets the title.
Branch: `runtime-verify`

## Follow-ups

(noticed and not done; one line each with the slice and date; removed when promoted to a done-condition or dropped by the user)

- provider-modes, 2026-09-02: `scripts/codex-worker.sh` help text prints one line too many (now `2,17p`, should be `2,16p`; the range was bumped with the header in slice 6 and kept the off-by-one).
- provider-modes, 2026-09-02: a value flag given last to `scripts/codex-worker.sh` (`--model` with no value) dies with bash's unbound-variable error instead of the script's own message; still non-zero.
- provider-modes, 2026-09-02: `skills/bosun-brief/SKILL.md` "Find the provider mode" line understates which steps change (the "two lines" wording was fixed by the codex-port rename).
- provider-modes, 2026-09-02: this spec's assumption text says `usage.json` comes from the "last token_count-style event"; the script sums every `turn.completed` usage event, which matches what codex emits.
- provider-modes, 2026-09-02: a relative `--out-dir` could split outputs between codex's `-C` cwd and the shell cwd; the documented flow passes absolute paths.
- provider-modes, 2026-09-02: `marketplace.json` `tags` array was reflowed one-per-line by the JSON rewrite; cosmetic.
- run-policy, 2026-09-03: `skills/bosun-brief/SKILL.md` step 9 reports before "Until blocked" commits and opens the PR, while the rules, README, and design say commit, push, PR, then report; the per-slice report cannot name its PR. Pick one order.
- run-policy, 2026-09-03: `skills/bosun-verify/SKILL.md:20` invites staging under `until blocked` without saying codex mode only, while the brief skill and design scope staging to codex mode. Say which applies.
- run-policy, 2026-09-03: `README.md` "Version" line says 0.2.0; manifests are at 0.3.0 (already stale on main at 0.2.1).
- run-policy, 2026-09-03: the stop condition "next runnable done-condition depends on an undecided item" can never fire, since the runnable definition already excludes those. Drop it or reword.
- codex-port, 2026-09-04: `Route:` override is not portable across harnesses: Claude side is `Route: <model> / <effort>`, Codex side is `Route: <agent>`. A spec moved between them with a Route line set would confuse the other brief. Add a one-line rule on each side to map or reject the foreign form.
- codex-port, 2026-09-04: `README.md` "Why each piece exists" tail still says "The codex provider mode has not yet run a real slice" and "Version 0.2.0"; manifests are 0.4.0 and the mode is now `fable-crew`.
- codex-port, 2026-09-04: `rules/fable.md` run-policy section and this spec's design still say "applies in both provider modes"; there are four.
- codex-port, 2026-09-04: `README.md` documents appending `rules/fable.md` to `~/.claude/CLAUDE.md` but not the Codex equivalent (append `codex/rules/astra.md` to `~/.codex/AGENTS.md`, which the Codex hook checks for). The checkpoints line under the plugin table names only the Claude path.
- runtime-verify, 2026-09-05: `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` descriptions still say "Built from Anthropic's Fable 5.1 docs" while the README intro now also credits Claude Code guidance.
- runtime-verify, 2026-09-05: `codex/rules/astra.md`, `codex/skills/bosun-mode/SKILL.md`, `codex/skills/bosun-verify/SKILL.md`, and the verifier TOML description call `bosun_verifier` read-only without saying its sandbox is `workspace-write` with read-only behavior; only the README and the TOML's own rule explain it.
- runtime-verify, 2026-09-05: whether Claude Code honors the `mcpServers` list-of-maps frontmatter in `agents/bosun-verifier.md` has not been probed; done-condition 46's fable-mode run shows it.

## Slice log

(each codex-mode slice appends: date, slice name, task class, route, first-verify verdict, usage)

- 2026-09-05, runtime-verify, fable mode (implemented by Fable), first verify PASS WITH FOLLOW-UPS; route-or-screen done-conditions: 0 of 0.
- 2026-09-04, bosun-rename, fable mode (implemented by Fable), first verify PASS WITH FOLLOW-UPS.
- 2026-09-04, codex-port, fable mode (implemented by Fable), first verify PASS WITH FOLLOW-UPS.
- 2026-09-03, run-policy, fable mode (implemented by Fable), first verify PASS WITH FOLLOW-UPS.
- 2026-09-02, provider-modes, fable mode (this slice was implemented by Fable), first verify PASS WITH FOLLOW-UPS. Smoke run of the worker script only: gpt-5.6-luna / low, 4 s, 16,824 input (8,960 cached), 5 output tokens.

## Lessons

- Under `codex exec`, a Codex subagent's browser (Playwright MCP) call can be denied by the automatic approval reviewer (`codex-auto-review`) that `--approve-for-me` installs; observed twice with a `gpt-6-astra` agent and never with `gpt-5.6-luna` (2026-09-05, codex-cli 0.153.4). A second failure shape, "The requested module './index.js' does not provide an export named 'default'", appeared on Astra agents and on a read-only agent, and was never reproduced on Luna at workspace-write. CLI probes therefore prove an agent file's shape, not that the Astra-model agent will be allowed to browse; that is settled in the desktop app, where approvals are interactive.
- Codex subagent spawns fail intermittently with "collab spawn failed: no thread with id: <the lead's own thread id>"; the lead then reports NOTSPAWNED. Seen 2026-09-04 on codex-cli 0.153.4 in five `codex exec --ephemeral` runs from Astra: three succeeded (all in git repos) and two failed (one bare temp dir, one git repo with a commit), while a run without `--ephemeral` succeeded. Neither the git repo nor `--ephemeral` is a proven cause. Treat one failure as inconclusive and retry once before concluding an agent file is broken; a parse check never proves usability.
- Codex custom agent names accept only lowercase letters, digits, and underscores; a hyphen makes every spawn fail with "agent_name must use only lowercase letters, digits, and underscores", surfaced only in the lead's output, while the TOML still parses fine. File names may keep hyphens (`bosun-scout.toml` holds `name = "bosun_scout"`). Found 2026-09-04 by spawning from Astra in a temp project; a parse check of the agent files is not proof they are usable, so any new agent needs one real spawn.

- `codex exec` rejects `-s <sandbox>` together with `--approve-for-me`; the latter already selects the workspace-write sandbox. Found by a real smoke run of `scripts/codex-worker.sh` (2026-09-02, codex-cli 0.149.0) after the dry-run looked fine, so a dry-run of the argv is not proof the argv is accepted. Any flag change to the script needs one real no-op run (Luna, low, "reply OK") before it ships.
