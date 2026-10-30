# Bosun spec

Provider mode: opus

Repo: `mckissinger/bosun` (named `fable-harness` until 2026-09-04; evidence pointers and slice names before that date refer to the old paths, which map one to one onto the new ones), plugin version 0.1.2 at the time this spec was written (2026-09-02). The plugin is prompt-only (skills, agents, rules, one hook script); there is no runtime code or test suite. Checks are therefore file reads, `bash -n`, JSON validation, and a dry-run of any script this work adds.

## Outcome

A user can put the harness into a named provider mode. In `fable` mode (the default and today's behavior) Fable 5.1 briefs, implements, verifies, and keeps the spec. In `codex` mode Fable 5.1 still briefs, keeps the spec, and verifies, but the implementation step of each slice is handed to an OpenAI Codex model (`gpt-5.6-sol` or `gpt-5.6-luna`) through the user's own installed `codex exec` CLI, with model and reasoning effort chosen per task class from a routing table. Every codex-mode slice records what it cost and whether it verified first time, so the two modes can be compared after a handful of slices.

Second outcome (slice 3, 2026-09-03): the harness can keep working instead of idling. A `Run policy:` line lets `/bosun-brief` run slice after slice until something blocks it, use a codex worker's run time to stage the next brief, re-validate that staged brief against what actually landed, and, when the spec has no runnable work left, say so and ask what next with proposals drawn from accumulated follow-ups.

Third outcome (slice 4, 2026-09-04): the harness runs on either Claude Code or Codex. Four named provider modes replace the two: `fable` (Fable 5.1 does everything, Claude Code), `fable-crew` (Fable leads, Sol and Luna implement by task class, Claude Code; today's `codex`), `astra-crew` (GPT-6 Astra leads, Sol and Luna implement by task class, Codex), and `astra` (Astra does everything, Codex). The repo ships a second plugin for Codex under `codex/` with the same spec contract, so a project can move between the two harnesses by changing one line.

## Decisions, in the user's words

- (2026-10-30) Planning hub. Michael: "What are your thoughts on using the hub lane or the hub session as basically the one where we can continue to make decisions, plan out work, etc.? The other lanes that come off of that are the actual working lanes." Asked "What do you recommend?", the lead recommended a hub that never builds once lanes start, with the shape chosen per run (hub plus one lane, hub plus two, or one session for short or unattended runs) and approved once per run. On a third lane, the lead listed its hesitations (three independent areas at once, Michael's review time, red default branch from parallel merges, CI and machine load, spec conflicts). Michael: "Let's keep the hub plus two, and we'll defer the third area after we've continued to use this and explored it." Then "Yes" to briefing it.
- (2026-10-30) Lanes. After reviewing the cre-list hub session and its two Lane B runs (10 slices merged while the hub built Build), Michael: "I would like to see how we can implement this in Bosun." On standard versus mode and sessions versus subagents, the lead recommended a standard rule gated by conditions, with the hub proposing and Michael approving once per run, lanes as sessions the hub starts, and subagents staying inside a slice. Michael: "I agree with the lanes running as sessions, which is now a Claude Code feature where the hub can initiate these other sessions. We don't even have to set it up for Codex." Then "Brief lanes". Supersedes the 2026-10-26 removal of parallel lanes; the old lane files and per-brief overlap check stay removed.
- (2026-10-30) Remove the Codex side. After reviewing the cre-list hub-and-lane sessions, the lead recommended lanes as Claude Code sessions the hub starts, and noted that the matching Codex copy made the design awkward. Michael: "We don't even have to set it up for Codex. I'm not even really using Codex now, so I'm just using Claude." On keeping the plugin: "Yeah, let's just keep the plugin and maybe remove the Codex piece." On `fable-crew`: "I don't use Fable Crew. Right now, I'm just using Opus mode. That's my standard." Then "yes" to starting this slice. Supersedes the 2026-09-04 decision that the harness runs on both Claude Code and Codex, and the provider-modes, codex-port and astra decisions below for everything they say about `fable-crew`, `astra-crew`, `astra` and the Codex plugin. Lanes are the next, separate slice.
- (2026-10-26) Merge flow. From the cre-list (Crelaunch) session: under `Run policy: until blocked`, with up-to-date branches required, no merge queue and 20–25 minute CI, five PRs piled up behind each other and one waited an hour. That session relayed what Michael agreed to there: build ahead only on independent slices, use a merge queue, and fix a red PR by pausing and fixing it in its own worktree. Asked here, Michael: "Yes, I would like to build it ... It'll be default for all my projects, really." The lead found GitHub's merge queue unavailable on all of his repos (amdg-org is on the Team plan with private repos; project-hearth is a private personal repo) and recommended turning off the up-to-date requirement, with CI on pushes to the default branch, over paying for GitHub Enterprise Cloud, revisiting a queue once an app has customers and main deploys to production. Michael: "proceed". The rule still names the queue as the recommended setup where GitHub offers one.

- (2026-10-26) After the lead found no project uses lanes (no `Stack isolation:` or `Lane:` line and no `lanes/` directory in any spec) and that cre-list had 16 linked worktrees, 7 of them merged and clean. Michael: "Let's remove the parallel lanes. Maybe add the cleanup of git state to the hygiene slice if you think that'd be helpful. Let's defer the milestone gaps for now until we've started to use this and see if it affects our process at all as is, without those additional items you're mentioning. Make sure you take note of those." On the launch and operate plan the lead proposed (thin launch skill, docs, marketing plan, monitoring, agent-run support and debugging): "I agree with your recommendations." On the public page: "it doesn't have to be a landing page per se. It could be a full marketing page. I want you to keep that super vague, though. No specific design instructions or anything like that." After the lead offered to brief removal, cleanup, the deferrals and the plan: "proceed". The lead put cleanup in `bosun-triage`, which already runs first at each milestone end, rather than in the hygiene slice itself, because cleanup changes no file and a hygiene slice is a code slice with its own PR.

- (2026-10-25) On the build-mode merge fallback (`gh pr merge <n> --merge` when GitHub refuses auto-merge because every required check is already green), the lead recommended keeping it and rewording the global CLAUDE.md line to "Never merge past a red or missing required check, and never bypass branch protection. If GitHub refuses auto-merge because every required check is already green, merge with `gh pr merge <n> --merge`." Michael: "Proceed with the recommendation."

- (2026-10-25) After a review of the Quillery, RV Rez and CRE Launch sessions. Michael: "95% of the time … we always proceed with Bosun's recommendations. We like to make sure that we take care of follow-ups, especially when Bosun recommends they be taken care of." On design: "I want that to be a staple too." The review found he took the recommendation about 60% of the time at first ask, and about 75–85% after asking "what do you recommend?". His overrides fell on product scope, pricing and fees, spend and design taste, not on process. He called stops between slices, merge prompts and the 3-slice cap unnecessary. After nearly every slice he asked whether to resolve follow-ups and almost always said yes. Design approval differs by project: CRE Launch and RV Rez get his approval of a prototype; Quillery runs an unattended critique loop against approved boards. The lead proposed one setting (a `Decisions:` line, with build mode as `take recommendations`) plus a `Design approval:` line. Michael asked whether these were several build modes or one setting; the lead answered "one setting." Michael: "ok lets brief it."

- (2026-10-20) After a review of the hub-and-lane sessions in cre-list and rv-rez (lanes sharing one local Supabase stack, every cre-list e2e run wiping it, an unapproved migration applied to the shared stack, SPEC.md conflicts between parallel slices, the hub handing out stack instances and migration numbers by message), the lead proposed one Bosun slice: a parallel-lanes section in the core rules, per-lane spec files, an overlap check in `/bosun-brief`, and a `Stack isolation:` spec line, with stack scripts and migration numbering left to each project and no lease tooling yet. Michael: "so should we change bosun then?" then "proceed". This supersedes the slice 3 out-of-scope line on parallel slices in separate worktrees.

- (2026-09-25) "If Fable is not the lead, then why would you name it Fable.md? I want it to be clean." Supersedes the 2026-09-04 rule that the two rules files keep model names: they are `rules/core.md` and `codex/rules/core.md`, and shared prose says "the lead". Entries in this spec dated before 2026-09-25 that cite `rules/fable.md` or `codex/rules/astra.md` refer to those files under their old names.

- (2026-09-22) "I mean opus 5.5. The model was just released a few hours ago". Confirmed directly from Anthropic's live release page: https://www.anthropic.com/claude-opus-5-5 names `claude-opus-5-5` in Availability. Search results and the installed CLI's embedded model list had lagged the release.

- (2026-09-22) "I would like to 2 more modes to bosun, fable crew with opus 5.5 as the implemented and then another mode with just opus 5.5 for everything". Extend the unfinished fable-opus work to Opus 5.5 and add opus for all roles.

- (2026-09-18) "Can we add another mode to bosun where opus 5 is the implementer?" "Fable as the lead and I would like to be able to toggle effort on the verifier as well." Approved switching this repository to astra for implementation in Codex.

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
- (2026-09-16) "Does the current bosun setup allow us to properly verify and test mobile apps?" It did not: the verifier had Playwright only, so a native iOS screen could only be screenshotted through `xcrun simctl` and never tapped or inspected. Michael: "lets proceed" on one slice that adds a mobile verifier, not two.
- (2026-09-16) The mobile verifier gets its simulator tooling the same way the web verifier gets Playwright: an npx-launched MCP server declared in the agent file, so it behaves the same in every environment. The desktop app's own iOS Simulator tool is not used by the harness.

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

(2026-10-30, remove-codex) Everything below about `fable-crew`, `astra-crew`, `astra`, the routing table, `scripts/codex-worker.sh` and the Codex plugin is superseded: those were removed in 0.18.0. The parts about the spec, the run policy and staging still hold, with staging now for `fable-opus` only.

### Where the mode lives

Historical four-mode design below is superseded by the current six-mode slice: fable, fable-crew, fable-opus, opus, astra-crew, astra. See Current slice and README for current routing.

The mode is a line in the project's spec, `Provider mode: <mode>` (four values, see "Provider modes (four)" below; `codex` is read as `fable-crew`), under a heading the brief skill can find. The spec is already the one input a fresh session needs, so the mode travels with it. There is no global default file; a spec without the line is in `fable` mode.

### Routing table (fable-crew and astra-crew)

Task class is chosen by the brief, using the same criteria the effort policy in `rules/core.md` already uses. The brief names the class and the resulting route in the slice brief so it is reviewable before the run.

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
3. Fable writes a worker prompt file into the checkpoint directory (`~/.claude/bosun/workers/<slug>/<slice>/prompt.md`) containing: the slice brief verbatim, the spec's decisions and out-of-scope lists, the scope, test, and targeted-edit rules from `rules/core.md`, the exact check commands, and the instruction not to commit, not to touch the spec, and to finish with a short report of what changed and which checks it ran.
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

The Codex plugin is a sibling, not a shared-skills refactor: `codex/.codex-plugin/plugin.json`, `codex/rules/core.md`, `codex/skills/<bosun-brief|bosun-verify|bosun-checkpoint|bosun-mode>/SKILL.md`, `codex/hooks/hooks.json`, `codex/scripts/session-start.sh`, `codex/agents/*.toml`; the repo-root `.agents/plugins/marketplace.json` points at `./codex`. Duplicated wording is the price of leaving the Claude plugin's fable-mode text untouched. The Codex skills are the Claude ones with: Astra in place of Fable; `$bosun-brief` style invocation; Codex subagents in place of the Agent tool and the worker script; and no `usage.json` (the app shows usage; the slice log records the route and the first-verify verdict only).

Agents shipped (installed into `~/.codex/agents/` by `$bosun-mode astra-crew` or `$bosun-mode astra`, since plugins cannot bundle agents): `bosun_scout` (gpt-5.6-luna, medium, read-only), `bosun_verifier` (gpt-6-astra, high, read-only, the verifier agent text), and one worker per routing row, `bosun_worker_small` (luna/max), `bosun_worker_routine` (sol/medium), `bosun_worker_feature` (sol/high), `bosun_worker_hard` (sol/xhigh), all workspace-write with the worker instructions (no commit, no spec edits, run the checks, report). In `astra-crew` the brief's Execute step asks Astra to delegate the slice to the worker agent named by the task class and wait for it; in `astra` Astra implements itself.

Effort for the Astra lead follows the same ladder and rules as Fable's (chosen at session start in the app's picker, held for the session, `ultra` never used). The SessionStart hook prints `codex/rules/core.md` unless `~/.codex/AGENTS.md` already carries its heading, then the spec path with mode and run policy, then any checkpoint, as JSON `additionalContext`.

### Naming

The harness is `bosun`. Everything derived from the harness name is neutral: plugin and marketplace names (`bosun@bosun` on both sides), skill prefix (`/bosun-brief`, `$bosun-brief`), agent prefix (`bosun-scout`, `bosun-verifier` on Claude; `bosun_scout`, `bosun_verifier`, `bosun_worker_*` on Codex), working directories (`~/.claude/bosun/`, `~/.codex/bosun/`), hook messages, and the repo. Model names appear only where they mean the model: mode values (`fable`, `fable-crew`, `fable-opus`, `opus`, `astra`, `astra-crew`), model-specific agents (`bosun-worker-opus`), mode-specific sections, and prose about what a model does. Shared files are named for their role: `rules/core.md` and `codex/rules/core.md`, headed `# Bosun core rules (Claude Code)` and `# Bosun core rules (Codex)`, which the hooks grep for in the user's global instruction files (2026-09-25; before that the files were `rules/fable.md` and `codex/rules/astra.md`).

### Runtime verification

A done-condition may name a route or screen ("`/settings` shows the new toggle", "the dashboard renders the chart") and count as checkable by the verifier's tools. The check is a browser: the implementer runs the app and looks, and the verifier re-checks.

Implementers. The Fable and Astra leads use whatever browser tool the session has (the Claude Code desktop browser pane or Playwright MCP; the Codex built-in browser) and need no new tooling. Sol and Luna workers get Playwright MCP: in fable-crew the brief adds `Worker browser: <yes | no>` (yes when any done-condition names a route or screen) and `scripts/codex-worker.sh --browser` passes the Playwright MCP config to `codex exec`; in astra-crew each worker TOML carries a `[mcp_servers.playwright]` block. For every route-or-screen done-condition the implementer records an evidence line: the route, what was checked, and a screenshot path if one was taken. Evidence goes in the report and in the verifier prompt. Screenshots are evidence when appearance matters, not a required step; the accessibility snapshot is the cheaper check for text and structure.

Verifiers. `bosun-verifier` (Claude) gets `mcp__playwright` in its tools and an inline `mcpServers` Playwright entry that starts with the agent and stops with it. `bosun_verifier` (Codex) gets a `[mcp_servers.playwright]` block and moves to `sandbox_mode = "workspace-write"` because the read-only sandbox breaks the MCP process; its instructions keep it read-only in behavior. Both use the browser only to re-check done-conditions that name a route or screen, following the implementer's evidence as the map, and report screenshot paths as evidence. They may start the app with the launch command the brief names and must stop it afterward. No exploratory walkthroughs.

Slice log. Each entry records how many route-or-screen done-conditions the slice had and how many the verifier confirmed in the browser, so runtime verification can be compared across modes and projects.

What this does not change: effort rules, scope and test rules, the worker never committing or editing the spec, the verifier's verdict format. This is the harness's first rule taken from Anthropic's Claude Code guidance rather than the Fable 5.1 model guide; the README says so.

### Run policy

The run policy is a line in the spec, `Run policy: one slice` or `Run policy: until blocked, max N slices`, under the first heading next to `Provider mode:`. A spec without the line is `one slice`. `until blocked` without a `max` means `max 3 slices`. It applies in both provider modes.

Under `one slice`, `/bosun-brief` behaves as before: one slice, verify, report, stop.

Under `until blocked`, after a slice verifies (PASS or PASS WITH FOLLOW-UPS), Fable records lessons, commits, pushes, opens a PR for the slice's branch, writes the slice's report, and then, in the same turn, briefs and runs the next slice. Each slice has its own branch (stacked on the previous slice's branch while that is unmerged, the rule until 2026-10-26; since then the core rules' "Merge flow" builds ahead only on independent slices and never stacks) and its own PR; PRs are never merged by Fable. The run stops, with a report saying why, at the first of: no runnable done-condition remains; the next runnable done-condition depends on an undecided item; a verify produced two FAILs on the same finding; the codex preflight failed; N slices have been started in this run, counting the first.

A done-condition is runnable when its status is `todo` or `in progress`, it is not `human-check`, and nothing it needs is on the undecided list.

### Exhausted roadmap

When `/bosun-brief` finds no runnable done-condition, at the start or between slices under either policy, it does not invent work. It reports that the roadmap is exhausted, lists every open human-check condition and every undecided item as the question the spec records, and proposes candidate next slices drawn from the spec's follow-ups section, each as a draft done-condition marked as a proposal. It ends the turn asking what next. A proposal becomes a done-condition only when the user says so.

### Follow-ups section

The spec gains a "Follow-ups" section: things noticed and not done (verifier follow-ups, pre-existing bugs, deferred items), one line each naming the slice, the date, and a tag (`bug`, `drift`, `nit`, `deferral`; added 2026-10-11). Step 9 of the brief appends to it, the exhausted-roadmap report draws from it, and a line is removed when it becomes a done-condition, the user drops it, or `bosun-triage` shows it resolved in a batch the user approves.

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

Slice 7, CI optimization skill (2026-09-15; user accepted the proposed bosun-ci design with "ok sounds good"):

47. `verified 2026-09-15 bosun_verifier PASS; skill reads, normalized parity, quick_validate.py, JSON/version checks, diff --check` Both plugins ship a discoverable `bosun-ci` skill for GitHub Actions with matching audit and improvement behavior, using the local Bosun skill invocation conventions.
48. `verified 2026-09-15 bosun_verifier PASS; skill reads, normalized parity, quick_validate.py, JSON/version checks, diff --check` Audits stay read-only; improvement requests use Bosun briefing/verification. Instructions measure elapsed time, runner minutes, and reliability, preserve required-check coverage and failure propagation, and distinguish measured savings from estimates or missing evidence.
49. `verified 2026-09-15 bosun_verifier PASS; skill reads, normalized parity, quick_validate.py, JSON/version checks, diff --check` README documents both entry points and measurement limits; all three versioned manifests are 0.7.0 and parse as JSON; both new skills pass skill validation.
50. `human-check` Exercise an audit and an optimization on a real GitHub Actions project with authenticated run history and comparable before/after hosted runs. No hosted speedup is claimed by this skill-authoring slice.

51. `verified 2026-09-16 bosun-verifier PASS WITH FOLLOW-UPS; agents/bosun-verifier.md:18, codex/agents/bosun-verifier.toml:12, rules/fable.md:63, codex/rules/astra.md:64, both bosun-brief Execute steps` **Web viewport rule.** `agents/bosun-verifier.md`, `codex/agents/bosun-verifier.toml`, `rules/fable.md`, `codex/rules/astra.md`, and both `bosun-brief` skills say that a route-or-screen done-condition may name a viewport width, that the implementer's evidence line then carries the viewport, and that the verifier re-checks it in Playwright at that viewport. No new capability.
52. `verified 2026-09-16 bosun-verifier PASS WITH FOLLOW-UPS; agents/bosun-verifier-mobile.md:4-12 frontmatter (YAML parse), :20 simulator rule, diff vs web verifier limited to frontmatter, rule, step 3b` **Mobile verifier agent, Claude side.** `agents/bosun-verifier-mobile.md` exists with frontmatter `tools: Read, Grep, Glob, Bash, mcp__mobile`, `effort: high`, and an inline `mcpServers` entry `mobile` that runs `npx -y @mobilenext/mobile-mcp@latest` over stdio with env `MOBILEMCP_DISABLE_TELEMETRY=1`. Its body is the `bosun-verifier` body with the browser rule replaced by a simulator rule: the simulator is for done-conditions that name a native screen and nothing else; follow the implementer's evidence lines (screen, device, what was checked, screenshot path); the app is built and installed with the commands the prompt names; the verifier may boot the named simulator with `xcrun simctl boot` and must shut down anything it booted with `xcrun simctl shutdown` before finishing; use the on-screen element list for text and structure and save a screenshot only when appearance is what the done-condition asserts; no exploratory walkthroughs. Everything else (read-only, evidence citations, judge as written, human-check handling, bug hunt, report format) is identical to `bosun-verifier`.
53. `verified 2026-09-16 bosun-verifier PASS WITH FOLLOW-UPS; codex/agents/bosun-verifier-mobile.toml:1-5, :32-35 (tomllib parse via python3.12)` **Mobile verifier agent, Codex side.** `codex/agents/bosun-verifier-mobile.toml` exists with `name = "bosun_verifier_mobile"` (underscores only, per the lessons), the same model, effort, and `sandbox_mode = "workspace-write"` as `bosun-verifier.toml`, the same developer instructions as 52 adapted to Codex wording, and a `[mcp_servers.mobile]` block with `command = "npx"`, `args = ["-y", "@mobilenext/mobile-mcp@latest"]`, and `env = { MOBILEMCP_DISABLE_TELEMETRY = "1" }`. `codex/skills/bosun-mode/SKILL.md` needs no change because it copies every `agents/*.toml`.
54. `verified 2026-09-16 bosun-verifier PASS WITH FOLLOW-UPS; skills/bosun-brief/SKILL.md:38,50,88,93,101; codex/skills/bosun-brief/SKILL.md:37,49,90` **Brief marks the surface.** Both `bosun-brief` skills: the brief template gains an optional line `Surface: ios` present only when a done-condition names a native screen; the evidence line for such a done-condition is `screen, device, what was checked, screenshot path`; the Execute step says the Fable or Astra lead checks a native screen with the simulator tool its session has, or `xcrun simctl` from the shell when it has none, before marking it done. In fable-crew mode the template gains `Worker simulator: <yes | no>` (yes when `Surface: ios`), and the worker prompt rules name the simulator check when it is yes.
55. `verified 2026-09-16 bosun-verifier PASS WITH FOLLOW-UPS; skills/bosun-verify/SKILL.md:9,20,22; codex/skills/bosun-verify/SKILL.md:8,19,21; web verifier 'not verifiable here' at agents/bosun-verifier.md:18 and the TOML :12` **Verify picks the verifier.** Both `bosun-verify` skills: when the brief says `Surface: ios`, launch `bosun-verifier-mobile` (`bosun_verifier_mobile` in Codex) instead of the web verifier and include in its prompt the device name, the build and install commands, the bundle id, and the evidence lines; otherwise launch the web verifier as today. The web verifier's rule text says a native-screen done-condition is "not verifiable here" and names the mobile verifier.
56. `verified 2026-09-16 bosun-verifier PASS WITH FOLLOW-UPS; scripts/codex-worker.sh:8,32,67-71; dry-run with --simulator prints three mcp_servers.mobile flags, without prints none; real no-op run Luna/low exit 0, 5 s` **Worker script binds the simulator.** `scripts/codex-worker.sh` accepts `--simulator`, which adds `-c 'mcp_servers.mobile.command="npx"'`, `-c 'mcp_servers.mobile.args=["-y","@mobilenext/mobile-mcp@latest"]'`, and `-c 'mcp_servers.mobile.env={MOBILEMCP_DISABLE_TELEMETRY="1"}'` to the argv, documented in the header comment next to `--browser`; `bash -n` passes; `--dry-run` prints the three `-c` flags when `--simulator` is given and none of them otherwise.
57. `verified 2026-09-16 bosun-verifier PASS WITH FOLLOW-UPS; README.md:17,69,74,150,199; three manifests parse and say 0.7.1` **Docs and version.** README: the agent table gains a `bosun-verifier-mobile` row and the Codex agents row names `bosun_verifier_mobile`; the "Runtime verification" section gets one paragraph on native screens (surface line, simulator MCP on both verifiers and on fable-crew workers via `--simulator`, `xcrun simctl` boot and shutdown, macOS with Xcode required, evidence line shape); the prerequisites line at README.md:17 mentions macOS with Xcode and a simulator for native-screen checks; the "Version" line says 0.7.1. All three manifests (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `codex/.codex-plugin/plugin.json`) say 0.7.1 and parse as JSON.
58. `verified 2026-09-16 bosun-verifier PASS WITH FOLLOW-UPS; verifier re-ran the stdio handshake: mobile-mcp 1.0.4, 32 tools incl. the four named` **Simulator MCP answers on this machine.** `npx -y @mobilenext/mobile-mcp@latest` started over stdio with `MOBILEMCP_DISABLE_TELEMETRY=1` answers an MCP `initialize` followed by `tools/list` with a tool list that includes `mobile_install_app`, `mobile_launch_app`, `mobile_save_screenshot`, and `mobile_list_elements_on_screen`. Run by the lead as a check, not by the worker.
59. `human-check` A real native iOS slice on a real project: the fable-crew worker checks a screen with `Worker simulator: yes`, and `bosun-verifier-mobile` confirms it in its own simulator, with the slice log recording the counts. Also the first real spawn of `bosun_verifier_mobile` from Codex, per the lesson that a parse check never proves an agent is usable.

### Opus modes slice (2026-09-22, verified)

Status: verified 2026-09-22, bosun_verifier PASS; completes the uncommitted September 18 slice. Live Claude agent execution remains untested.
Outcome: Add fable-opus (Fable leads/verifies, native Opus 5.5 worker implements) and opus (Opus 5.5 leads, implements, scouts, and verifies), preserving independent Claude verifier effort controls.
Done-conditions: O1–O6 below.
Out of scope: changing Sol/Luna routing; selectable Astra verifier effort; paid benchmarks; publishing/installing globally; unrelated follow-ups.
Assumptions: retain the unfinished fable-opus name, add opus; both run in Claude Code. Opus worker stays at high. Verifier effort precedence remains invocation, current slice, project default, high. Existing user-owned definitions are not overwritten. Session model must actually match the selected mode; spec edits do not change the running model.
Effort assumed: inherited session setting (not exposed); no picker change.
Checks: python3 scripts/configure-claude-agents.py --help; temporary-project generation across modes/efforts, transitions, invalid inputs and collision/symlink refusal; JSON/TOML/frontmatter parsing; bash -n scripts/*.sh codex/scripts/*.sh; claude plugin validate .; git diff --check; independent bosun_verifier review. Live Opus execution is separate from static configuration validation.
Branch: codex/fable-opus-verifier-effort, existing uncommitted work based on main (98d6025); preserve and complete that work.

O1. `verified 2026-09-22 bosun_verifier PASS` Six-mode tables, selection and host gates recognize fable-opus and opus. Default/legacy modes retain their meaning; Codex redirects both new modes to Claude Code.
O2. `verified 2026-09-22 bosun_verifier PASS` fable-opus pins the worker to Opus 5.5/high, with Fable lead/verifier, no nested delegation, spec edits, or commits by the worker; same-worker retries and evidence rules remain intact.
O3. `verified 2026-09-22 bosun_verifier PASS` opus uses Opus 5.5 for lead, direct implementation, scout, and both verifier variants; verifies in a fresh context; gates execution on the actual lead model and restores Fable agents when switching back.
O4. `verified 2026-09-22 bosun_verifier PASS` Claude verifier effort remains independently configurable; generator validates before writing, preserves tools/MCP, handles spaces, is idempotent, refuses symlinks/unrelated files, and does not change worker effort when verifier effort changes.
O5. `verified 2026-09-22 bosun_verifier PASS` Docs explain usage, host/model/reload requirements and validation limits; README and manifests consistently use 0.8.0 for the completed unpublished slice.
O6. `verified 2026-09-22 bosun_verifier PASS; live spawns untested` Static checks and independent review pass; live model verification limits are explicitly recorded without equating generated configuration to a successful spawn.

### Core rules rename slice (2026-09-25, verified)

Name: core-rules-rename (2026-09-25). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS 2026-09-25.
Outcome: Shared files are named for their role, not a model: the two core rules files become `rules/core.md` and `codex/rules/core.md`, and shared prose says "the lead" wherever it means whichever model is leading.
Done-conditions:
R1. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS` `rules/fable.md` is renamed (git mv) to `rules/core.md` with first heading `# Bosun core rules (Claude Code)`, and `codex/rules/astra.md` to `codex/rules/core.md` with `# Bosun core rules (Codex)`. The old paths no longer exist.
R2. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS` `scripts/session-start.sh` prints `rules/core.md` unless `~/.claude/CLAUDE.md` has a line `# Bosun core rules (Claude Code)`; `codex/scripts/session-start.sh` prints `codex/rules/core.md` unless `~/.codex/AGENTS.md` has `# Bosun core rules (Codex)`. Checked by running each hook with a temporary HOME, with and without the heading.
R3. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS` Outside SPEC.md history, no file names `rules/fable.md`, `codex/rules/astra.md`, `rules/astra.md`, `# Fable 5.1 agentic development`, or `# Astra agentic development` (grep), except the README sentence telling users who appended the old file how to migrate.
R4. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS` In both core rules files, the shared (not mode-specific) parts of `bosun-brief`, `bosun-verify`, and `bosun-mode` in both plugins, and README, "Fable" or "Astra" that means whichever model is leading reads "the lead". Model names remain only for mode names, model-specific agents (`bosun-worker-opus`), mode-specific sections, and facts about a specific model. The line "References to Fable in the shared rules below mean the selected Claude lead" is removed.
R5. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS` The spec records the user's decision superseding the 2026-09-04 naming rule, the Naming design paragraph matches, and a note says older entries refer to the old rules paths.
R6. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS` Version 0.9.0 in all three manifests and the README version line; manifests parse.
R7. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS` Checks pass: `bash -n scripts/*.sh codex/scripts/*.sh`; JSON parse of the three manifests and `hooks/hooks.json`, `codex/hooks/hooks.json`; `claude plugin validate .`; `git diff --check`.
Out of scope: the Tests and CI rules and `bosun-ci` changes (next slice); renaming mode values, agents, or the working directories; rewriting historical spec entries; fixing unrelated follow-ups.
Assumptions: "Fable"/"Astra" in the fable-crew, fable-opus, and Astra-mode sections stays where it names the model that holds that role in that mode. The minor version bump is because users who appended the old rules heading to their global file must re-append under the new heading. The user's global CLAUDE.md stale copy was removed by the user's approval on 2026-09-25 before this slice, so nothing on this machine still carries the old heading.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in R7, plus the R2 hook runs and the R3 grep.
Branch: rename-core-rules, from main (574003a); carries the uncommitted mode-line change astra -> opus.

### Tests and CI standard slice (2026-09-25, verified)

Name: tests-ci-standard (2026-09-25). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS WITH FOLLOW-UPS 2026-09-25. Stacked on rename-core-rules (PR #13, unmerged).
Outcome: Every Bosun role follows the same test and CI rules, and `bosun-ci` treats Blacksmith as the runner standard and carries the lessons from Linear's CI rework.
Done-conditions:
T1. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS on second verify` Both core rules files have a "Tests and CI" paragraph in "While working" stating: run the tests for what you touched before handoff or push, the full suite only for shared code, configuration, dependencies, or test setup, and never push to find out whether tests pass; never weaken, skip, or delete a test to make a change pass, and say so when a specified behavior change requires a test change; new tests make no real network calls, use no real sleeps or wall-clock time, and do not depend on order or leak global state; follow the repo's written test and CI conventions; a failure that passes on rerun with no change and unrelated to the change is a flake candidate, reported with name and message, never fixed with retries or longer sleeps, quarantined only with the user's approval; a workflow change states whether it adds or removes CI time and does not undo existing optimizations. Because every crew-mode worker prompt already includes the core rules' "While working" rules (`skills/bosun-brief` fable-crew and fable-opus step 1, `codex/skills/bosun-brief` astra-crew step 1), those prompts carry it with no template change.
T2. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS on second verify` `agents/bosun-worker-opus.md` and the four `codex/agents/bosun-worker-*.toml` carry the same rules as one compact bullet.
T3. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS on second verify` `agents/bosun-verifier.md`, `agents/bosun-verifier-mobile.md`, `codex/agents/bosun-verifier.toml`, and `codex/agents/bosun-verifier-mobile.toml` treat as findings: an existing test weakened, skipped, or deleted without a done-condition that changes that behavior and a report that says so; a new test with real network calls, real sleeps, or wall-clock or order dependence; a CI workflow change whose report does not state its CI-time effect.
T4. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS on second verify` Both `bosun-ci` skills: a "Runner standard" section makes Blacksmith the standard (GitHub-hosted runners are a finding; per-job sizing; org and Default runner group requirement, personal repos excluded; check current Blacksmith docs for labels and cache actions; after a migration, measure checkout time and look for hung or retried checkouts). The line keeping provider migrations and paid runner upgrades out of scope is replaced: migration is recommended, and implemented only when the user asked for it.
T5. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS on second verify` Both `bosun-ci` skills' "Choose a change": critical-path gate jobs rank first; candidates for gate-job fetch and checkout trimming, repeated setup (base image, filtered installs, schema snapshot, cache vs fresh install), batching small checks with per-task output, native typecheck and type-free lint rules, sharding only after setup is short with the setup-times-shards arithmetic and file splitting, per-file isolation opt-in with teardown and an isolated project for risky files, and affected-only tests with a full-run fallback.
T6. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS on second verify` Both `bosun-ci` skills' implementation done-conditions add: an optimization that constrains how code or tests are written is recorded where the project's agents read it (its CLAUDE.md or AGENTS.md, or the spec's lessons). References gain Linear's article and Blacksmith's docs.
T7. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS on second verify` `skills/bosun-brief/SKILL.md` step 6 says to follow the scope and edit rules in the core rules, not "the global CLAUDE.md" (follow-up from core-rules-rename, folded in because this slice edits those rules).
T8. `verified 2026-09-25 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS on second verify` Version 0.10.0 in all three manifests and the README version line; checks pass: `bash -n scripts/*.sh codex/scripts/*.sh`; JSON parses; TOML parses (python3.12 tomllib) for every `codex/agents/*.toml`; `claude plugin validate .` and `codex`; `git diff --check`; `python3 scripts/configure-claude-agents.py` into a temp project regenerates verifiers containing the new rule.
Out of scope: Blacksmith Testbox (follow-up); migrating any project's CI; changes to fable-crew routing, verifier effort, or mode behavior; README beyond the version line, the core-rules row contents, and the bosun-ci scope sentence T4 contradicts.
Assumptions: the rules are Bosun-wide defaults; a project's own written conventions win where they differ, which is what "follow the repo's written conventions" means. The verifier runs before the PR exists and, in lead-implements modes, before any report, so both `bosun-verify` skills now pass it the implementer's test and CI statements (added after the first verify FAILed and found the gap). Blacksmith label examples are illustrative and the skill says to confirm against current docs.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in T8.
Branch: tests-ci-standard, stacked on rename-core-rules.

### CI research guidance slice (2026-10-07, verified)

Name: ci-research-guidance (2026-10-07). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS 2026-10-07 (first verify PASS WITH FOLLOW-UPS; its three wording follow-ups fixed in-slice at the user's request, then re-verified PASS).
Outcome: `bosun-ci` and the verifiers carry what the 2026-10-07 CI research changed: selection must not let misses land under auto-merge, identical-input skipping is a coverage-preserving candidate, and agent-written test bloat is a verifier finding.
Done-conditions:
C1. `verified 2026-10-07 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS, PASS on re-verify after wording fixes; skills/bosun-ci/SKILL.md:57, codex/skills/bosun-ci/SKILL.md:57` Both `bosun-ci` skills' change-based selection candidate says that when PRs merge automatically on green, a scheduled or post-merge full run finds a selection miss only after it lands, so anything the PR run skips still runs in a required check before merge (for example the full suite in a merge queue), and that on the PR run end-to-end tests stay full or path-gated because the import graph cannot select them.
C2. `verified 2026-10-07 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS, PASS on re-verify after wording fixes; skills/bosun-ci/SKILL.md:48, codex/skills/bosun-ci/SKILL.md:48` Both `bosun-ci` skills' "Choose a change" list has an identical-input candidate: skip a task whose inputs match a run that already passed, through a task or remote cache keyed on those inputs, with a caution that the key must cover every input the task reads, and that tasks reaching live services, reading the clock, or showing flakes stay uncached.
C3. `verified 2026-10-07 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS, PASS on re-verify after wording fixes; agents/bosun-verifier.md:23, agents/bosun-verifier-mobile.md:25, codex/agents/bosun-verifier.toml:16, codex/agents/bosun-verifier-mobile.toml:16` `agents/bosun-verifier.md`, `agents/bosun-verifier-mobile.md`, `codex/agents/bosun-verifier.toml`, and `codex/agents/bosun-verifier-mobile.toml` treat as a Tests and CI finding a new test that asserts the code's internal structure instead of a stated behavior (a boundary call is fine when it is the stated behavior), or checks a behavior an existing test already checks.
C4. `verified 2026-10-07 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS, PASS on re-verify after wording fixes; SPEC.md Follow-ups, two ci-research lines` The two ci-research deferrals (two-tier CI, scheduled `bosun-ci` runs) are in Follow-ups.
C5. `verified 2026-10-07 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS, PASS on re-verify after wording fixes; manifests and README:221 at 0.10.1; all C5 checks exit 0; regenerated verifiers carry the finding` Version 0.10.1 in all three manifests and the README version line; checks pass: `bash -n scripts/*.sh codex/scripts/*.sh`; JSON parses; TOML parses (python3.12 tomllib) for every `codex/agents/*.toml`; `claude plugin validate .`; `git diff --check`; the two `bosun-ci` skills' "Choose a change" sections are identical; `python3 scripts/configure-claude-agents.py` into a temp project regenerates verifiers containing the new finding.
Out of scope: the core rules' Tests and CI paragraph (user: the July-August targeted-test lessons are not a reason to change it); two-tier CI implementation and scheduled audits (deferred, C4); worker definitions; README beyond the version line; other follow-ups.
Assumptions: patch bump because the changes add guidance without changing any interface. The auto-merge sentence is conditional, since not every project auto-merges. No new reference links: the skill already says to consult current docs, and no Turborepo page was verified this session.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in C5.
Branch: ci-research-followups, from main (2750b37); carries the C4 follow-up lines.

### Bosun preflight slice (2026-10-10, verified)

Name: bosun-preflight (2026-10-10). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS WITH FOLLOW-UPS 2026-10-10 (first verify FAIL); its four follow-ups fixed in-slice at the user's request and re-verified PASS WITH FOLLOW-UPS; P6 human-check open.
Decisions (user, 2026-10-10): "Lets start with the bosun preflight skill." On the lead's recommendation that a beta never lowers legal findings or unrecoverable data loss, and that the four re-verify follow-ups be fixed in this PR: "Proceed". Marketing and go-to-market skills are a separate plugin, later, not Bosun.
Outcome: Both plugins ship a `bosun-preflight` skill that audits a feature-complete app for production readiness and turns chosen findings into verified Bosun slices.
Done-conditions:
P1. `verified 2026-10-10 bosun-verifier (claude-opus-5-5/high), first verify FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS after the follow-up fixes; skills/bosun-preflight/SKILL.md:2-3,12-13,19-22,28-33,37-41,47-110,114-122,126-133,137` `skills/bosun-preflight/SKILL.md` exists with frontmatter `name: bosun-preflight` and a description naming when to use it (app nearly done, before launch, "is this ready for production", "preflight", "harden"). Its body covers: audit (the default, read-only except a Production preflight record in an existing spec) and fix outcomes (chosen findings through `/bosun-brief` and `/bosun-verify`); scope (launch target, surfaces, stack detection, project and user lessons); evidence and safety rules (cited evidence, unknowns stated, no secret values, no spend or messages, no probes against production); three severities, where a beta or internal launch may lower reliability, polish, and operations findings but never access-control, abuse and cost, store-policy, or legal findings, or data loss with no recovery path; the areas access control and data exposure, abuse and cost guardrails, reliability, legal and data, product polish, operations, and native mobile; the report format and the spec record; fix-mode done-conditions that prove each fix; and boundaries (not a penetration test, not the diff-scoped security review, not infrastructure launch or deploy).
P2. `verified 2026-10-10 bosun-verifier (claude-opus-5-5/high), first verify FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS after the follow-up fixes; skills/bosun-preflight/SKILL.md:50-56,72,74-75` The access-control and reliability areas name these generalized checks: auth decisions from server-verified tokens, never client-editable session contents; gate pages ship no protected data in HTML or serialized props, checked in page source; redirect guards checked after normalization; session cookie flags read from real `Set-Cookie` headers, since library defaults may omit HttpOnly; privileged database functions not exposed through an auto-generated API; webhook signatures and idempotency; client-exposed build-time variables carry no secrets; outbound and AI calls have timeouts, and quota exhaustion is not retried; reads that can exceed a provider's row cap paginate; work after a durable commit is non-fatal.
P3. `verified 2026-10-10 bosun-verifier (claude-opus-5-5/high), first verify FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS after the follow-up fixes; diff shows only title, $ invocations, bosun_scout` `codex/skills/bosun-preflight/SKILL.md` matches the Claude skill except the title, `$` skill invocations, and Codex agent names (`diff` shows only those).
P4. `verified 2026-10-10 bosun-verifier (claude-opus-5-5/high), first verify FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS after the follow-up fixes; README.md:65,76,113-115,226; three manifests at 0.11.0` README: a skills-table row, the Codex skills row names `$bosun-preflight`, and a short "Production preflight" section. Version 0.11.0 in all three manifests and the README version line.
P5. `verified 2026-10-10 bosun-verifier (claude-opus-5-5/high), first verify FAIL, second PASS WITH FOLLOW-UPS, third PASS WITH FOLLOW-UPS after the follow-up fixes; quick_validate both valid; JSON, bash -n, claude plugin validate, git diff main --check exit 0` Checks pass: `quick_validate.py` (skill-creator, run with `uv run --with pyyaml`) on both skill directories; JSON parse of manifests and hooks; `bash -n scripts/*.sh codex/scripts/*.sh`; `claude plugin validate .`; `git diff --check`; the P3 diff.
P6. `human-check` A real preflight audit on one finished app produces a punch list the user finds accurate, and one fix runs through a slice.
Out of scope: marketing or go-to-market skills; changes to `factory` or any app; changes to core rules, agents, or other skills; automated or scheduled preflight runs; a portfolio view across apps.
Assumptions: launch target defaults to a public launch when the user does not say, and the report states it. One skill holds the native-mobile area instead of a separate skill. The Preflight record is the audit's one write, allowed because the user asked for a readiness result in the spec; with no spec, the report alone is the record. Checks are written for any stack, with common providers as examples, because the repo is public. Minor version bump for a new skill.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in P5.
Branch: bosun-preflight, from main (6035556).

### Bosun triage slice (2026-10-11, verified)

Name: bosun-triage (2026-10-11). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS WITH FOLLOW-UPS 2026-10-11; its six follow-ups fixed in-slice at the user's request ("Yes"); second verify PASS WITH FOLLOW-UPS found four errors in those fixes, corrected; third verify PASS WITH FOLLOW-UPS; G6 human-check open.
Decisions (user, 2026-10-11): approved the triage design ("Ok i approve"): resolved follow-ups are removed as an approved batch, each with cited evidence; triage runs on demand only, with no exhausted-roadmap hook yet. On the spec's history: "I'm just concerned that condensing the spec might cause issues with clarity", so nothing is condensed; history stays verbatim and is only reordered below live content.
Outcome: Both plugins ship a `bosun-triage` skill that reviews a project's spec against its code and history and, on approval, cleans up the spec's bookkeeping; new follow-ups carry a tag.
Done-conditions:
G1. `verified 2026-10-11 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS; skills/bosun-triage/SKILL.md:2-3,8,12,16,22-34,36-47,51-60` `skills/bosun-triage/SKILL.md` exists with frontmatter `name: bosun-triage` and a description naming when to use it. Its body covers: on-demand use only, and, when an active slice or a checkpoint is found, reporting it and asking the user before proceeding; a read-only report by default; working from meaning rather than fixed headings; reconciling done-condition statuses with commits and code (stale in-progress, delivered but unmarked, verified claims whose cited evidence no longer holds); classifying each follow-up as resolved (with evidence), still valid (bug, drift, or nit), deferral (with its revisit trigger), or obsolete, merging duplicates and grouping into draft slices; finding missed items (decisions with no done-condition, follow-ups from PRs or verify reports never recorded); listing open human-checks oldest first with the user's exact step, and deferrals whose trigger has happened; spec health (nothing condensed or reworded; live content first and finished work under one history heading, as a pure move proven by a check that every line survives; no reorder when the spec cross-references its own numbered sections; an existing history file respected); the report format; and applying on approval: bookkeeping and the move in separate commits, resolved follow-ups removed as one approved batch with evidence, drafts never promoted, no code changes.
G2. `verified 2026-10-11 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS; diff shows only title, $ invocations, bosun_scout` `codex/skills/bosun-triage/SKILL.md` matches the Claude skill except the title, `$` skill invocations, and the Codex scout name (`diff` shows only those).
G3. `verified 2026-10-11 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS; rules/core.md:17, codex/rules/core.md:18, both bosun-brief step 9 identical` Both core rules files' follow-ups clause says each follow-up carries one tag, `bug`, `drift`, `nit`, or `deferral`; that a follow-up also leaves when triage shows it resolved and the user approves the batch; and that a nit is folded into the next slice that touches its file, named as a done-condition in that slice's brief, or dropped through triage. Both `bosun-brief` skills' step 9 appends each follow-up with its tag.
G4. `verified 2026-10-11 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS; README.md:66,77,118-120,231; manifests 0.12.0` README: a skills-table row, `$bosun-triage` in the Codex skills row, and a short "Spec triage" section. Version 0.12.0 in all three manifests and the README version line.
G5. `verified 2026-10-11 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS; quick_validate both valid; JSON, bash -n, plugin validate, diff --check exit 0` Checks pass: `quick_validate.py` (run with `uv run --with pyyaml`) on both skill directories; JSON parse of manifests and hooks; `bash -n scripts/*.sh codex/scripts/*.sh`; `claude plugin validate .`; `git diff main --check`; the G2 diff; the edited follow-ups clause is identical in both core rules files, and the step 9 sentence is identical in both `bosun-brief` skills.
G6. `human-check` After merge, a read-only triage of `~/Dev Projects/factory` (457-line spec, 97 follow-ups) produces a report the user finds accurate.
Out of scope: triaging this repo's own spec or any app's spec in this slice; an exhausted-roadmap hook; retagging existing follow-ups (triage does that when run); changes to agents, other skills, or factory.
Assumptions: existing untagged follow-ups stay valid; triage tags them on its first run. The every-line check compares the sorted multiset of non-blank lines before and after the move, duplicates included, so it proves nothing was lost or reworded but allows exactly one added line, the history heading. Minor version bump for a new skill and a rule change.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in G5.
Branch: bosun-triage, from main (aff4252).

### E2E cadence slice (2026-10-16, verified)

Name: e2e-cadence (2026-10-16). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS WITH FOLLOW-UPS 2026-10-16 (first verify FAIL: the fingerprint missed quoted untracked names, external diff tools, and subdirectory runs; the worker default and the verifier's shell allowance did not match; all fixed).
Decisions (user, 2026-10-16): "see if we're running the local E2E suite, the full suite, too often ... I don't want to do a bunch of unnecessary EDE if we don't have to." On the lead's assessment (the full suite ran three to six times per slice in cre-list, through the implementer, the verifier, every fix loop, and "No regression" done-conditions, while CI's required e2e check already runs it before auto-merge) and its four rule changes, with Blacksmith Testbox piloted later rather than built in: "Okay, let's proceed with your plan."
Outcome: Bosun runs end-to-end tests targeted during a slice and the full end-to-end suite at most once, which is CI's required check when the project has one; the verifier skips reruns on a tree the implementer already ran green, and a fix reruns only the checks it could affect.
Done-conditions:
E1. `verified 2026-10-16 bosun-verifier (claude-opus-5-5/high), first verify FAIL, second PASS WITH FOLLOW-UPS; rules/core.md:69, codex/rules/core.md:64` Both core rules files' "Tests and CI" paragraph says: end-to-end (browser or UI) tests run targeted, the specs for the routes and flows the change touches plus the specs the done-conditions name; after a fix, the failed specs rerun first (for example Playwright's `--last-failed`), then the targeted set; the full end-to-end suite runs at most once per slice: when a required CI check runs it before merge, that check is the full run and it is not run locally, and otherwise it runs once after the last code change; no done-condition requires a full local end-to-end run; after a fix, rerun only the checks the fix could change, so a fix to comments or documentation reruns typecheck and lint only. The paragraph is identical in both files.
E2. `verified 2026-10-16 bosun-verifier (claude-opus-5-5/high), first verify FAIL, second PASS WITH FOLLOW-UPS; agents/bosun-worker-opus.md:26, codex/agents/bosun-worker-*.toml:14` `agents/bosun-worker-opus.md` and the four `codex/agents/bosun-worker-*.toml` carry the same end-to-end rule in their Tests and CI bullet, identical across the five files.
E3. `verified 2026-10-16 bosun-verifier (claude-opus-5-5/high), first verify FAIL, second PASS WITH FOLLOW-UPS; skills/bosun-verify/SKILL.md:28,38, codex/skills/bosun-verify/SKILL.md:17,25` Both `bosun-verify` skills: the verifier prompt carries the implementer's check results (command, exit code) for checks run after the last edit, with the working-tree fingerprint they ran on and the exact fingerprint command; on FAIL, the fix reruns only the checks it could change, and the re-verify prompt names the files the fix changed and the checks rerun for them. The fingerprint command is read-only, runs from the repo root in bash, leaves out the spec file, and changes when any other tracked or untracked file changes, including untracked names git quotes and with an external diff tool configured.
E4. `verified 2026-10-16 bosun-verifier (claude-opus-5-5/high), first verify FAIL, second PASS WITH FOLLOW-UPS; agents/bosun-verifier.md:17,28, agents/bosun-verifier-mobile.md:19,30, codex/agents/bosun-verifier*.toml:10,21` `agents/bosun-verifier.md`, `agents/bosun-verifier-mobile.md`, `codex/agents/bosun-verifier.toml`, and `codex/agents/bosun-verifier-mobile.toml`: step 3 always runs typecheck, lint, build, and unit tests; for end-to-end or UI tests it runs the specs the done-conditions name and the route-or-screen re-checks, skips other end-to-end specs the prompt reports green on a fingerprint matching its own, runs the ones the prompt names as affected when the fingerprint differs, and never runs the full end-to-end suite when the prompt says a required CI check runs it.
E5. `verified 2026-10-16 bosun-verifier (claude-opus-5-5/high), first verify FAIL, second PASS WITH FOLLOW-UPS; skills/bosun-brief/SKILL.md:49, codex/skills/bosun-brief/SKILL.md:41` Both `bosun-brief` skills' brief template `Checks:` line says end-to-end checks name the targeted specs, not the full suite, and says whether a required CI check runs the full end-to-end suite.
E6. `verified 2026-10-16 bosun-verifier (claude-opus-5-5/high), first verify FAIL, second PASS WITH FOLLOW-UPS; manifests and README:231 at 0.13.0; all E6 checks exit 0; fingerprint temp-repo matrix` Version 0.13.0 in all three manifests and the README version line; checks pass: `bash -n scripts/*.sh codex/scripts/*.sh`; JSON parses; TOML parses (python3.12 tomllib) for every `codex/agents/*.toml`; `claude plugin validate .`; `git diff main --check`; the E1 and E2 identity checks; `python3 scripts/configure-claude-agents.py` into a temp project regenerates verifiers containing the E4 rule; the fingerprint command, in a temp repo, prints the same id twice on an unchanged tree and from a subdirectory, a different id after a tracked file, an untracked file, or an untracked `café.txt` changes (also under `GIT_EXTERNAL_DIFF=true`), the same id after a spec edit, and writes no objects.
Out of scope: Blacksmith Testbox (piloted by hand on cre-list first; follow-up); any project's CI or spec (cre-list's "No regression" conditions and Checks lines change when its next slices are briefed); `bosun-ci` selection guidance; test-impact tooling; README beyond the version line.
Assumptions: "required CI check runs the full suite" is judged from the repo's workflows and branch protection, and the brief states it; a project without one still gets exactly one full local run. Typecheck, lint, build, and unit tests stay unconditional in the verifier because they are cheap and are its independent evidence; the skip applies only to end-to-end specs. The fingerprint is a hash of HEAD, `git diff HEAD --binary`, and each untracked non-ignored file's name and blob hash, computed without writing objects. Minor version bump for a rule change.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in E6.
Branch: e2e-cadence, from main (8194f09).

### Agents gitignore slice (2026-10-19, verified)

Name: agents-gitignore (2026-10-19). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS WITH FOLLOW-UPS 2026-10-19.
Decisions (user, 2026-10-18): on the lead's recommendation to stop tracking Bosun-generated agent files in the seven projects that committed them and to make Bosun add the ignore itself: "Yes".
Outcome: `scripts/configure-claude-agents.py` keeps the agent files it generates out of git, so a plugin update never shows as a diff in a project.
Done-conditions:
A1. `verified 2026-10-19 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS; scripts/configure-claude-agents.py:16-17,56-59,69-70` When it writes agents (not on `--dry-run`), the script writes `.claude/agents/.gitignore` containing the Bosun marker comment, `bosun-*.md`, and `.gitignore` (so the ignore file itself stays untracked), creating it when absent and rewriting it only when it carries the marker; an existing `.gitignore` there without the marker is left unchanged and the script prints that it was left alone. It refuses a symlinked `.gitignore` like it refuses symlinked agents.
A2. `verified 2026-10-19 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS; scripts/configure-claude-agents.py:71-79` When git still tracks any generated `bosun-*.md` in the project, the script prints a note naming them and the `git rm --cached` command; it never runs git commands that change state.
A3. `verified 2026-10-19 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS; README.md:168` README's agent-setup sentence (line 168) says the generated files are git-ignored through `.claude/agents/.gitignore`.
A4. `verified 2026-10-19 bosun-verifier (claude-opus-5-5/high) PASS WITH FOLLOW-UPS; manifests and README:231 at 0.13.1; all A4 checks exit 0; 7-case lead matrix plus 15 verifier cases` Version 0.13.1 in all three manifests and the README version line. Checks pass: `bash -n scripts/*.sh codex/scripts/*.sh`; JSON parses; `claude plugin validate .`; `git diff main --check`; `python3 -m py_compile scripts/configure-claude-agents.py`; temp-repo runs show: a fresh repo gets the agents and the ignore file and `git status --porcelain` lists nothing under `.claude/`; a second run changes nothing; `--dry-run` writes nothing; a user-owned `.claude/agents/.gitignore` is left byte-identical with the printed note; a repo that tracks `bosun-verifier.md` gets the A2 note; a symlinked ignore file is refused before any write.
Out of scope: Codex agent files (`$bosun-mode` installs those; no project tracks them); changing which agents are generated; the projects' own `.gitignore` files (handled by their seven PRs on 2026-10-19).
Assumptions: a nested `.gitignore` is used instead of editing the project's root `.gitignore` so the script never modifies a tracked project file. Patch bump because no interface changes.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in A4.
Branch: agents-gitignore, from main (7e0b5fa).

### Parallel lanes slice (2026-10-20, verified; removed 2026-10-26 by remove-lanes)

Name: parallel-lanes (2026-10-20). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS WITH FOLLOW-UPS 2026-10-20 (first verify PASS WITH FOLLOW-UPS with seven text findings, fixed; second FAIL: lane end dropped statuses and slice log, L1 text stale, staged briefs and mid-slice sessions skipped the check, stale local default branch, core stop list; all fixed).
Decisions: see the 2026-10-20 entry under Decisions.
Outcome: Bosun says when slices may run as parallel lanes, keeps parallel lanes from conflicting in the spec, checks a new slice against other open work before it starts, and never lets a lane run migrations or data-resetting suites on a stack another session uses.
Done-conditions:
L1. `verified 2026-10-20 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second FAIL, third PASS WITH FOLLOW-UPS; rules/core.md:55,61-69, codex/rules/core.md:50,56-64` Both core rules files gain an identical "Parallel lanes" section after "Run policy" that says: what a lane is; run in parallel only when slices touch different files and tables and neither needs the other's result, one after the other when one depends on the other, either is a wide refactor, or both change migrations or the same schema; two lanes per project by default; every writing lane in its own worktree and branch; while more than one lane is active, each lane keeps everything it would write to the spec (brief, done-conditions and statuses, slice log, follow-ups, lessons and lesson corrections) in `lanes/<lane>.md` next to the spec and does not edit the spec file; the spec file plus every lane file in `lanes/` is the spec; lanes find each other through the lane files in the repo's other worktrees; at lane end its last PR moves everything in the lane file into the spec and deletes the lane file; a session mid-slice when a second lane starts finishes that slice in the spec and becomes a lane from its next slice; the optional `Stack isolation: <command>` line, claimed stacks recorded in the lane file and released at lane end, one lane at a time on a shared stack without the line; never an unapproved or unmerged migration on, or a reset or stop of, a stack or server another session uses; an optional hub that decides lanes and merge order, relays approvals in the user's words, alone edits the spec's shared sections, and does not hand out resources a command can claim. Both files' run-policy stop lists include the overlap stop.
L2. `verified 2026-10-20 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second FAIL, third PASS WITH FOLLOW-UPS; skills/bosun-brief/SKILL.md:38,62-73,85,96, codex/skills/bosun-brief/SKILL.md:31,54-65,76,87` Both `bosun-brief` skills: step 2 points to a new "Parallel lanes" section, identical in both, which says that when another worktree holds an active lane file or the repo has open PRs other than this session's own and the branch step 4 stacks on, the lead lists the files each other lane or mid-slice worktree changes against `origin/<default>` (committed or not) and expects to change per its lane file, and each such PR's files (leaving out the spec and lane files), compares them with the files this slice expects to change, adds `Lane:`, `Files expected:`, `Overlap:`, and `Stack:` lines to the brief, re-runs the check when a staged brief is re-validated, does not start a slice that overlaps or is a wide refactor alongside another lane (picks the next runnable slice with no overlap, or reports and stops when none, which is also a stop condition under "Until blocked"), and in a lane sends every spec write the skill describes (steps 3, 4, 6, 8, 9) to the lane file.
L3. `verified 2026-10-20 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second FAIL, third PASS WITH FOLLOW-UPS; README.md:190,198-208,238,243; manifests 0.14.0` README gains a short "Parallel lanes" section and its "Not covered on purpose" parallel-agents bullet says lanes are covered there; version 0.14.0 in all three manifests and the README version line.
L4. `verified 2026-10-20 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second FAIL, third PASS WITH FOLLOW-UPS; all L4 checks exit 0 on fingerprint 9b98b1b` Checks pass: `bash -n scripts/*.sh codex/scripts/*.sh`; JSON parses for the manifests and hooks; `claude plugin validate .`; `git diff main --check`; the L1 section is byte-identical in both core rules files; the L2 section in the two brief skills differs only in plugin naming (`bosun-scout`/`bosun_scout`, `/bosun-brief`/`$bosun-brief`).
Out of scope: stack-isolation scripts, port bands, and migration-numbering checks in any project (cre-list's per-lane stacks are its own slice); a lease or lock tool; changes to `bosun-triage`, `bosun-verify`, `bosun-checkpoint`, or the agents (they read "the spec", which L1 defines to include lane files); converting any project to lanes.
Assumptions: lane files sit in a `lanes/` directory next to the spec so they work for root and docs-convention specs alike. The hub is optional because two lanes can be coordinated by the user directly. Minor version bump for a new rule.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in L4. No end-to-end suite; CI's `checks` job is the required check.
Branch: parallel-lanes, from main (2361b96).

### Build mode slice (2026-10-25, verified)

Name: build-mode (2026-10-25). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS WITH FOLLOW-UPS 2026-10-25 (Michael: "we just created a new brief i would like to build"; first verify FAIL: take recommendations still stopped at undecided items, fable-opus two-FAIL stop, milestone triage branch base, no re-verify after follow-up fixes, approval drift in the core rules and README; all fixed).
Decisions: see the 2026-10-25 entry under Decisions.
Outcome: A project can let the lead act on its own recommendations and keep running. It stops only for decisions that are Michael's. It handles follow-ups and CI audits without being asked, arms auto-merge on verified PRs, and holds every screen to a design-fidelity loop whose approval gate the project chooses.
Done-conditions:
B1. `verified 2026-10-25 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS; fingerprint 86ef731` Both core rules files gain an identical "Decisions" section after "Provider mode", covering the following.
   - **The setting.** The `Decisions: ask | take recommendations` spec line; no line means `ask`, today's behavior.
   - **What the lead decides itself under `take recommendations`:**
     - an open question that comes up mid-run;
     - an undecided item the spec's outcome or decisions lean on;
     - a two-FAIL disagreement, taking the fix it recommends.
   - **How it records each one.** In the spec's decisions as "(build mode, <date>)" with the choice and one line of why, then it continues without ending the turn.
   - **What it never decides itself; the work that needs it is parked:**
     - credentials, accounts and sign-ins;
     - prices, fees and any live spend;
     - production data and anything sent to real people;
     - legal, naming and trademark questions;
     - new-design approval when `Design approval: me`;
     - anything the spec lists as the user's.

     Parking means recording a human-check, or an undecided item phrased as a question with the lead's recommendation, then taking the next runnable work.
   - **The limit.** A third FAIL on the same finding stops the run under either setting.
B2. `verified 2026-10-25 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS; fingerprint 86ef731` Both core rules files' "Run policy" section says the following.
   - `until blocked` without a `max` means `max 10 slices`.
   - Under `until blocked`, the lead never ends the turn between slices to ask whether to continue or to announce the next slice. The stop list is the only way a run ends.
   - **Merging.** After a slice verifies, the lead pushes, opens the PR and arms auto-merge with `gh pr merge <n> --auto --merge`. If GitHub refuses because every required check is already green, it merges with `gh pr merge <n> --merge`. It never merges past a red or missing required check and never bypasses protection. Where the repo has no required checks or disallows auto-merge, it leaves the PR open and says so. Where the project's spec or instructions say merging is the user's, those win.
   - **No waiting on CI.** While a PR's CI runs, the lead briefs and starts the next slice, stacked when it depends on the unmerged branch.
   - **The stop list.** "The next runnable done-condition depends on an undecided item", which can never fire, is replaced by "every remaining runnable item needs a decision the lead may not make (see Decisions)", and the two-FAIL entry reads per B1.

   This resolves the run-policy follow-up of 2026-09-03 about the stop that can never fire.
B3. `verified 2026-10-25 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS; fingerprint 86ef731` Both core rules files gain an identical "Follow-ups and milestones" paragraph. Every follow-up gets a home when it is written:
   - **Bugs and security issues in the slice's own work:** fixed in that slice.
   - **Bugs in shipped code:** fixed by the next slice that touches the file, or by a hygiene slice before the milestone closes. No bug outlives its milestone.
   - **Nits:** folded into the next slice that touches the file. Dropped at milestone end if still open and not cheap.
   - **Deferrals:** name their target done-condition or milestone.
   - **Items that need the user or gate a launch:** go to the spec's human-checks.
   - **A milestone** is a group of done-conditions the spec names as one, or every fifth slice in a spec without groups.
   - **At each milestone end, under `until blocked`, the lead runs:**
     - `/bosun-triage`;
     - a hygiene slice, own PR, for the open bugs;
     - a `/bosun-ci` audit against recent runs, with findings recorded as follow-ups and fixes as their own slice, never folded into a feature slice.
   - **More than five open bugs** makes the next slice a hygiene slice.
B4. `verified 2026-10-25 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS; fingerprint 86ef731` Both core rules files gain an identical "Design" section, which applies to any slice that adds or changes a screen.
   - **The setting.** A `Design approval: me | critique` spec line. With no line, a project with UI is `me`.
   - **The loop:**
     1. Read the screen's board, the design system and any motion and mock-data notes before writing UI code.
     2. Mock up a screen with no board first, in the project's design system: on a design canvas artifact when the session has one, with a copy in the repo's design folder.
     3. Get the mockup approved:
        - under `me`, Michael approves it before product UI is written, and a new design direction or new interaction pattern always waits for that;
        - under `critique`, a fresh agent critiques it and the board is revised, with an "After critique" note.
     4. Build the screen.
     5. Before the first verify, check it at 390, 768, 1024, 1280 and 1440 wide (or the project's named widths), with empty, loading, error, hover and focus states and the board's motion including exits and reduced motion.
     6. A fresh agent compares the screenshots with the board, and open differences block the done-condition.
   - **New directions start fresh:** several new options, not variations on an older approved mockup.
   - **Screenshot paths** go in the evidence lines.
B5. `verified 2026-10-25 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS; fingerprint 86ef731` Both `bosun-brief` skills carry the changes as follows.
   - **Step 5:** stop only when B1's list blocks, and otherwise park the item and take other work.
   - **Step 6:** run B4's loop for screen done-conditions.
   - **Step 7:** apply B1's two-FAIL handling.
   - **"Until blocked":** apply B2's merging, no waiting on CI, no asking between slices, the stop list and B3's milestone-end steps.
   - **"Exhausted roadmap":** under `take recommendations`, hygiene slices built from open bug follow-ups count as runnable work. New features are still never invented.
   - **Worker prompts** in fable-crew and fable-opus mode include the Design section when the slice touches a screen.
   - **The brief template** gains `Decisions:` and `Design approval:` lines, with the effective value and its source.
B6. `verified 2026-10-25 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS; fingerprint 86ef731` Both `bosun-triage` skills say triage also runs at milestone end under `until blocked`.
   - Under `Decisions: take recommendations`, the lead applies that triage itself:
     - removals and status corrections, with evidence;
     - draft slices from open bugs promoted to hygiene done-conditions.

     Everything else stays a draft, decisions are never reworded, and the result goes in a commit on its own branch and PR.
   - Under `ask`, triage reports and waits as it does today.
B7. `verified 2026-10-25 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS; fingerprint 86ef731` Both `bosun-verify` skills pass the board path, the widths and the states to check for every screen done-condition that names a board. The verifier compares its screenshots with the board and reports each difference as a finding.
B8. `verified 2026-10-25 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS; fingerprint 86ef731` README:
   - "Run policy" describes B2;
   - new short "Decisions" and "Design" sections;
   - the "lead never merges" wording is removed;
   - version 0.15.0 in all three manifests (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `codex/.codex-plugin/plugin.json`), `.agents/plugins/marketplace.json` if it carries a version, and the README version line.
B9. `verified 2026-10-25 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS; fingerprint 86ef731` Checks pass, and the new sections in the two core rules files are byte-identical:
   - `bash -n scripts/*.sh codex/scripts/*.sh`;
   - JSON parses for the manifests and hooks;
   - TOML parses for `codex/agents/*.toml`;
   - `claude plugin validate .`;
   - `git diff main --check`;
   - B1–B4 byte-identical in `rules/core.md` and `codex/rules/core.md`;
   - the changed sections of the two brief, triage and verify skills differ only in plugin naming (`bosun-scout`/`bosun_scout`, `/bosun-x`/`$bosun-x`).
Out of scope:
- Changing any project's spec. Quillery, RV Rez and CRE Launch adopt the lines in their next slice.
- Michael's global `~/.claude/CLAUDE.md`.
- The agent definition files, apart from what the verify prompt carries.
- A design skill, and any automated design-diff tooling.
- Scheduled `bosun-ci` runs (still deferred).
- The other open follow-ups, apart from the one B2 resolves.
Assumptions:
- **The two-FAIL limit.** Under `take recommendations` a two-FAIL disagreement is decided by the lead because Michael took its fix every time it reached him in Quillery. A third FAIL on the same finding still stops the run, so a wrong fix cannot loop.
- **Money stays with Michael.** Prices, fees and spend are on the never-decide list because they are where he overrode recommendations most.
- **The design default.** `Design approval: me` is the default, because two of three projects gate on his approval. `critique` is opt-in for projects with an approved design system.
- **Merging an already-green PR.** `gh pr merge --merge`, used only when GitHub refuses auto-merge because every required check is already green, does what auto-merge would have done at once. Michael answered this case "Merge green prs." on RV Rez on 2026-10-18. Michael approved it on 2026-10-25 (see Decisions); his global CLAUDE.md's "never merge by hand" line is to be reworded to match.
- **The default cap of 10.** Michael raised CRE Launch and RV Rez to 10.
- **The milestone fallback.** "Every fifth slice" is used when a spec names no milestones, so triage and audits still happen.
- **Versioning.** Minor version bump for new rules.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in B9. No end-to-end suite; CI's `checks` job is the required check.
Branch: build-mode, from main (be42956).

### Remove lanes slice (2026-10-26, verified)

Name: remove-lanes (2026-10-26). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS 2026-10-26 (first verify FAIL: default branch and no-commit branches passed the ancestry test; ignored files such as `.env` were deleted; cleanup wording overstated under `ask`; fetch/prune ran before approval; all fixed; second PASS WITH FOLLOW-UPS: merged-PR test ignored the PR's base, README prune wording; fixed in-slice; third PASS).
Decisions: see the 2026-10-26 entry under Decisions.
Outcome: Bosun no longer carries the parallel-lanes machinery, keeps its safety rules for other sessions, and cleans up merged worktrees and branches at each milestone end; the deferred milestone gaps and the launch-and-operate plan are on record.
Done-conditions:
W1. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint fc72ff1` Both core rules files lose the "Parallel lanes" section and the Run policy overlap stop. Their "Follow-ups and milestones" paragraph says `bosun-triage` also removes merged, clean, idle worktrees and branches, and stays byte-identical across the two files. "While working" gains an identical "Other sessions" paragraph: every writing session in its own worktree and branch, only read-only sessions share a checkout, never an unapproved or unmerged migration on a database another session uses, never a reset or stop of another session's stack or server, never stopping processes by name.
W2. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint fc72ff1` Both `bosun-brief` skills lose the step 2 lane trigger, the "Parallel lanes" section, the overlap stop in "Until blocked", and the lane parts of staged-brief re-validation. The milestone-end paragraph points to triage's "Git cleanup". The two files still differ only in plugin naming and their existing harness differences.
W3. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint fc72ff1` Both `bosun-triage` skills gain an identical "Git cleanup" section, before "Milestone end", covering the following.
   - **Steps.** `git fetch --prune`, `git worktree prune`, then `git worktree list --porcelain`.
   - **Removable worktree.** All of these hold:
     - it is not the main checkout, not this session's worktree, and not locked;
     - it is not under `.claude/worktrees/`;
     - it has a branch, not a detached HEAD, and not the default branch;
     - its work is merged: a PR merged into the default branch (`--base <default>`) whose head commit is the branch tip (ancestry alone is not enough);
     - `status --porcelain --ignored` shows no uncommitted or untracked files and no ignored files beyond dependency and build output;
     - no process has its working directory inside it.
   - **Branches.** A local branch with no worktree is removable by the same merge test, never the default branch or this session's branch.
   - **Removal.** `git worktree remove` without `--force`; `git branch -D`, safe because of the merged-PR test. Never a remote branch.
   - **Report and approval.** The report lists removable items with evidence and every other worktree with its reason. Removal waits for approval under `Decisions: ask`, and is applied by the lead at a milestone end under `Decisions: take recommendations`.
   - **Other edits.** "Milestone end", "Apply on approval", "Boundaries" and the description say the same.
W4. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint fc72ff1` README loses the "Parallel lanes" section and the run-policy overlap stop. It gains a short "Other sessions" section, and its triage and milestone text mentions cleanup. The "Not covered on purpose" bullet says lanes were removed. Version 0.16.0 in all three manifests and the README version line.
W5. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint fc72ff1` This spec records the removal and the deferrals.
   - The 2026-10-26 decision is added in Michael's words.
   - The build-mode slice is moved under history, and the parallel-lanes slice heading is marked removed.
   - The out-of-scope line about parallel slices is updated.
   - The seven parallel-lanes follow-ups are removed, resolved by the removal: verify fingerprint, overlap trigger, step-2 wording, lane end, migration overlap, lane-file visibility, and the Design stop list.
   - Two deferrals record the milestone gaps.
   - "Launch and operate (drafts)" records the plan as proposals, not done-conditions.
W6. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint fc72ff1` Checks pass:
   - `bash -n scripts/*.sh codex/scripts/*.sh`;
   - JSON parses for the manifests and hooks;
   - `claude plugin validate .`;
   - `git diff main --check`;
   - no `lane` or `Stack isolation` text outside SPEC.md and the README's not-covered bullet;
   - the core "Follow-ups and milestones" section and "Other sessions" paragraph are byte-identical in both files;
   - the brief and triage skill pairs differ only as before plus naming.
   - A scratch-repo run of the W3 commands removes a merged clean worktree, and keeps a dirty one, an unmerged one, and one with a process running inside it.
Out of scope: the hygiene-slice rules themselves; the two deferred milestone gaps; any project's spec or worktrees (cre-list's cleanup happens when its next milestone triage runs or when Michael asks); factory changes (Sentry, PostHog, Intercom); building the launch skill.
Assumptions:
- **Where cleanup lives.** Cleanup lives in triage, which already runs first at each milestone end. Michael said "the hygiene slice", but cleanup changes no file and a hygiene slice is a code slice with its own PR; this keeps the timing he asked for.
- **App-made worktrees.** Worktrees under `.claude/worktrees/` are left alone because the desktop app tracks and cleans them itself.
- **Whether a worktree is in use.** `lsof` working-directory checks are the signal that a session is using a worktree; an idle session parked in a worktree with no process is not detectable and loses only a merged checkout with no uncommitted, untracked, or non-regenerable ignored files.
- **Versioning.** Minor bump, because a rule is removed and a behavior added.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in W6. No end-to-end suite; CI's `checks` job is the required check.
Branch: remove-lanes, from main (8b1569a).

### Merge flow slice (2026-10-26, verified)

Name: merge-flow (2026-10-26). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS 2026-10-26 (first verify FAIL: a dependent slice could wait forever on a PR that never merges on its own; every slice writes the spec, so "independent" never held and spec edits conflicted; triage still stacked; red-PR fixes skipped verify; update-branch restarted every PR's CI; no check of the default branch's runs; no `one slice` rule; all fixed; second PASS WITH FOLLOW-UPS: triage could wait forever, the brief still said not to wait, required reviews block auto-merge, spec drift, the staged-brief diff ref, the flake rule; all fixed; third PASS).
Decisions: see the 2026-10-26 "Merge flow" entry under Decisions.
Outcome: Under `until blocked`, the lead builds ahead only on independent slices, never stacks on unmerged ones, fixes red PRs before going on, and works with a merge queue where one exists or keeps behind PRs moving where none does. `bosun-ci` reports a merge setup that piles PRs up.
Done-conditions:
M1. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d49d553` Both core rules files gain an identical "Merge flow" section after "Run policy", covering the following.
   - **Build ahead.** Only slices that need nothing from an unmerged slice are built while a PR's checks run, each in its own worktree from the latest default branch. A dependent slice is briefed during CI and built after its base merges, with independent work taken meanwhile. Branches are never stacked on unmerged slices.
   - **Red PRs.** The lead checks open PRs before each slice and after each verify. A red PR pauses the current slice, is fixed on its own branch in its own worktree, and then the lead resumes. Slices that depend on it wait for the fix to merge.
   - **Merge setup.** A merge queue is recommended where GitHub offers one, with required checks on `merge_group` and a `merge_group` fallback for any job that reads a PR number. Without a queue, the up-to-date requirement is off and CI runs on pushes to the default branch. A repo that requires up-to-date branches without a queue gets the oldest behind PR updated with `gh pr update-branch`, one at a time, and a `bosun-ci` finding.
   - **Waiting.** When only dependent slices remain, the lead waits for a base PR that merges on its own. If the base cannot merge on its own, the run stops: a new stop-list entry in both core rules files and both brief skills.
   - **Spec edits.** The spec does not count toward independence. A built-ahead slice writes its brief as its own subsection and appends its log lines. Spec conflicts are resolved by keeping both sides.
   - **Watching.** The lead checks open PRs and the default branch's latest run before each slice, after each verify, and while waiting. A red or conflicting PR is fixed in its worktree, and a code fix is verified. A red default branch is fixed first.
   - **Updating behind PRs.** Without a queue, only the oldest behind PR is updated, one at a time.
   - **Run policy.** Its CI sentence says the lead does not idle on CI and waits only where "Merge flow" says.
   - **Worktree wording.** The fable-opus worker uses the slice's worktree (Claude core rules and brief).
   - **Triage.** Both `bosun-triage` skills wait for the run's open PRs to merge before milestone-end triage, then branch from the latest default branch.
M2. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d49d553` Both `bosun-brief` skills: step 4 starts from the latest default branch, builds a dependent slice only after its base merges, uses a new worktree while another slice's PR is open, and never stacks. Under `one slice`, a dependent slice is not started and the PR it waits for is reported. Staged briefs record and compare the default branch's HEAD. The "Until blocked" text drops stacking and adds the open-PR check: update behind PRs where required, and fix red PRs first. The pair still differs only as before.
M3. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d49d553` Both `bosun-ci` skills' baseline reads the default branch's merge setup. Requiring up-to-date branches without a queue is a finding. Under a queue, a required workflow without `merge_group`, or a PR-number job without a fallback, is a blocking finding. The pair still differs only as before.
M4. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d49d553` README gains a "Merge flow" paragraph under "Run policy", and its run-policy sentence points to it. Version 0.17.0 in all three manifests and the README version line.
M5. `verified 2026-10-26 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d49d553` Checks pass:
   - `bash -n scripts/*.sh codex/scripts/*.sh`;
   - JSON parse;
   - `claude plugin validate .`;
   - `git diff main --check`;
   - the "Merge flow" section is byte-identical in both core rules files;
   - no "stack on it" or "stacked on the previous" text remains in the brief or core rules;
   - skill-pair diff counts are unchanged.
Out of scope:
- `bosun-preflight`. It audits launch readiness, not repository merge settings; it already lists unreadable branch protection as unknown.
- Changing any project's repository settings. The lead does that outside this slice: for rv-rez, quillery and project-hearth, and for mom-ai once it has a repo; cre-list stays with its own session.
- A third-party merge queue.
Assumptions:
- **Never stacking.** "Stacking is only for real dependencies" in the relayed request is read together with "a dependent slice is briefed during CI and built only after its base merges": a dependent slice waits for its base to merge, so nothing is stacked. Stacked PRs are what piled up in cre-list.
- **When the lead looks at PRs.** Checking open PRs and the default branch's latest run before each slice, after each verify, and while waiting is how the lead notices a red PR without polling CI between those points.
- **Versioning.** Minor bump, because this changes run behavior.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in M5. No end-to-end suite; CI's `checks` job is the required check.
Branch: merge-flow, from main (6d2c26c).

### Remove Codex slice (2026-10-30, verified)

Name: remove-codex (2026-10-30). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS 2026-10-30 (first verify PASS WITH FOLLOW-UPS: the README checkpoint line rendered inside the plugin table, a missing "and", `/bosun-mode --verifier-effort` on a stored removed mode hit an argparse error, plural worker-mode wording, stale follow-up wording, "task routing"; all fixed; second PASS).
Decisions: see the 2026-10-30 entry under Decisions.
Outcome: Bosun is a Claude Code plugin only, with three provider modes (`fable`, `fable-opus`, `opus`); the Codex plugin, the Codex worker and the `fable-crew`, `astra-crew` and `astra` modes are gone, and a spec still naming one of them gets a clear message instead of a half-working run.
Done-conditions:
X1. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS; fingerprint e5f064c` Removed from the repo: `codex/` (the whole Codex plugin), `.agents/plugins/marketplace.json` (and the then-empty `.agents/`), and `scripts/codex-worker.sh`.
X2. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS; fingerprint e5f064c` `rules/core.md`: "Provider mode" lists three modes (`fable`, `fable-opus`, `opus`). The routing table, the `Route:` override, the `ultra` ban, the worker-never-commits and preflight text for crew workers, and the `astra*` and Codex sentences are gone. It says the values `codex`, `fable-crew`, `astra-crew` and `astra` were removed in 0.18.0 and that a spec naming one makes `/bosun-brief` and `/bosun-verify` stop and say to choose a mode with `/bosun-mode`. Staging under `until blocked` names `fable-opus` only. Nothing else in the file changes.
X3. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS; fingerprint e5f064c` Skills: `bosun-brief` loses the "Fable-crew mode" section, the fable-crew and astra handling in "Find the provider mode" (replaced by the removed-mode stop), fable-crew mentions in steps 3 and 6 and in staging, the No-spec step 2 mode list's removed values, and the codex-preflight stop. `bosun-verify` lists only the three modes, stops on a removed value with the same message, and loses its fable-crew worker bullets. `bosun-mode` (description, argument hint, table, steps and the routing table) offers only the three modes, refuses removed values naming the three, and has no Codex preflight. `scripts/configure-claude-agents.py` `MODES` has only the three. No other skill or agent mentions Codex, Astra, Sol, Luna or `fable-crew`.
X4. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS; fingerprint e5f064c` README, CONTRIBUTING, `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` describe a Claude Code plugin with three modes and no Codex install, worker, routing table or `$bosun-*` commands; README says in one sentence that the Codex plugin and crew modes were removed in 0.18.0. `.github/workflows/checks.yml` drops the `codex/` paths, the `.agents` manifest and the TOML step. Version 0.18.0 in both manifests and the README version line.
X5. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS; fingerprint e5f064c` Checks pass:
   - `bash -n scripts/*.sh`; JSON parses for both manifests and `hooks/hooks.json`; `python3 -m py_compile scripts/configure-claude-agents.py`;
   - `claude plugin validate .`;
   - `git diff origin/main --check`;
   - `grep -rniE 'codex|astra|fable-crew|gpt-5\.6|\bsol\b|luna|\$bosun' --exclude-dir=.git --exclude=SPEC.md .` prints only the removal notes X2–X4 call for;
   - `python3 scripts/configure-claude-agents.py --help` lists the three modes, and a dry invocation with `fable-crew` is refused.
X6. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS; fingerprint e5f064c` This spec: the decision entry; the merge-flow brief moved to history; Design gets a one-line note that its fable-crew, astra and Codex-plugin parts are superseded; Out of scope lines about Codex and crew workers marked superseded; Codex-only lessons removed; follow-ups about the removed files dropped as resolved by removal; the slice log line.
Out of scope:
- Lanes (the next slice).
- Editing other projects' specs. Four still name removed modes (`kurts-data`: astra; `Dev Projects/test`: astra-crew; `front-office` and `the-buildoff`: fable-crew); they get the stop message and Michael switches them when he next opens them.
- Uninstalling the Codex plugin from `~/.codex` or the `codex` CLI.
- Rewriting history sections of this spec beyond X6.
- Removing `fable` or `fable-opus`.
Assumptions:
- **Removed values stop, they don't map.** Mapping `fable-crew` to `fable-opus` or `opus` silently would change who implements and on which model; a stop with the fix named is safer and costs one command.
- **Staged briefs stay.** Staging exists for `fable-opus` too, so the rule stays with that mode only.
- **Versioning.** Minor bump, because modes are removed.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in X5. No end-to-end suite; CI's `checks` job is the required check.
Branch: remove-codex, from main (2a975fe).

### Lanes slice (2026-10-30, verified)

Name: lanes (2026-10-30). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS 2026-10-30 (first verify FAIL: the setup slice was unreachable, the no-start-session fallback contradicted itself, lane stops still went to the user, plus ten gaps on ownership, counting, milestones, model, proposal timing and wording; all fixed; second PASS WITH FOLLOW-UPS: red default branch, undecided items decided twice, hand-started lanes, hygiene vs lane areas, setup timing, woken hub, triage wording, spec text; all fixed; third PASS).
Decisions: see the 2026-10-30 "Lanes" entry under Decisions.
Outcome: Under `until blocked`, a lead whose spec has two or more independent areas can, with Michael's one approval per run, start lane sessions that each run their own Bosun loop in their own worktree on an isolated test stack, while the lead acts as the hub and the only channel to Michael, in the shape that worked in cre-list on 2026-10-29/30.
Done-conditions:
N1. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d3e6381` `rules/core.md` gains a "Lanes" section after "Merge flow", covering:
   - **What a lane is.** A separate Claude Code session the hub (the session running the run) starts in its own worktree, running its own Bosun loop on one area of the spec. Lanes are sessions, never subagents; subagents stay inside a slice as before.
   - **When.** All of: `Run policy: until blocked`; two or more areas, each with at least three runnable slices, that touch different files and tables and need nothing from each other; tests isolated or made so by the setup slice; and lane sessions can be started, by the hub or by the user from printed prompts. Otherwise there are no lanes.
   - **Approval.** The hub proposes lanes (areas, the shared files it keeps, lane count and slice caps) and starts them only after Michael approves, once per run, under either `Decisions:` value.
   - **Stack isolation.** When data-resetting checks share a stack and the spec has no `Stack isolation:` line, the first lane step is a setup slice that builds a per-lane stack command (own project id and port band generated from the committed config into an ignored folder, a holder record so one worktree holds a lane, refusal of plain data-resetting runs in a worktree that holds a lane, and a teardown that removes containers and volumes) and adds the line.
   - **Area split and shared files.** Lanes are split by area, not slice. The hub names the shared files it owns; a lane that needs a change there messages the hub instead of making it.
   - **Ceiling.** At most three sessions: the hub and one lane by default, a second lane only when a third independent area exists.
   - **Branches, PRs and the spec.** Each lane slice branches from the latest default branch, gets its own PR and auto-merge as "Run policy" says, and "Merge flow" applies inside each lane. Lanes write the spec directly as "Merge flow" "Spec edits" says (own subsection, appended lines, keep both sides on conflict).
   - **Michael goes through the hub.** A lane runs under the spec's `Decisions:` value. Anything only Michael can give is recorded in the slice and sent to the hub (what, why, where the screenshots are); the lane takes other runnable work. The hub batches these for Michael. Lanes never ask him directly.
   - **Checks in a lane.** A lane claims its stack before any data-resetting check, runs those checks only through it, tells its verifiers to do the same, gives every screenshot and output path as an absolute path inside its worktree, and releases the stack when it ends.
   - **Lane end.** At its slice cap, when its area has no runnable work, or at any "Run policy" stop, a lane releases its stack and reports to the hub: why it ended, each slice, PR, verify verdicts, follow-ups, and what waits on Michael. The hub checks those PRs before reporting them done.
   The "Other sessions" paragraph stays as is.
N2. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d3e6381` `skills/bosun-brief/SKILL.md` gains a "Lanes" section after "Until blocked", and "Until blocked" points to it at the start of a run and at each milestone end. The section holds:
   - the hub's check of the core rules' conditions;
   - the proposal it puts to Michael;
   - the setup slice when needed;
   - a fenced lane prompt template (area, done-conditions or spec rows, shared files the hub owns, the stack command and lane number, slice cap, protected paths, what goes to the hub, done and report);
   - starting each lane with the app's start-session tool (fresh context, its own worktree, wake the hub when done) after approval;
   - what the hub does while lanes run;
   - what a lane session does differently (it reads its prompt, runs `/bosun-brief` under the spec's policies with its own cap, messages the hub, and does not ask Michael).
   - Where the session cannot start sessions, the hub prints the lane prompt for Michael to start one by hand, and does not run lanes itself.
N3. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d3e6381` `skills/bosun-verify/SKILL.md` step 1: in a lane, the prompt names the lane's stack command for data-resetting checks and requires absolute paths inside the lane's worktree for screenshots and output.
N4. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d3e6381` README:
   - gains a "Lanes" section;
   - its "Not covered on purpose" first bullet no longer says parallel sessions are uncovered (parallel builders inside one slice stay uncovered);
   - version 0.19.0 in both manifests and the README version line.
N5. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d3e6381` Checks pass:
   - `bash -n scripts/*.sh`;
   - JSON parses for both manifests and `hooks/hooks.json`;
   - `python3 -m py_compile scripts/configure-claude-agents.py`;
   - `claude plugin validate .`;
   - `git diff origin/main --check`;
   - `grep -n '^## Lanes' rules/core.md skills/bosun-brief/SKILL.md README.md` finds one heading in each.
N6. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first FAIL, second PASS WITH FOLLOW-UPS, third PASS; fingerprint d3e6381` This spec:
   - the decision entry;
   - the remove-codex brief moved to history;
   - the Out of scope line on parallel slices updated to point here;
   - the slice log line.
Out of scope:
- Any project's own stack script or spec. cre-list already has `scripts/lane.sh` and rv-rez has `scripts/instance.sh`; converting projects happens in their own sessions.
- A lock or lease tool in Bosun, or a shared stack script; stack commands stay per project.
- Changes to the agents, `bosun-triage`, `bosun-checkpoint`, `bosun-ci`, `bosun-preflight` or `bosun-mode`.
- Lanes inside Codex (removed) or a lane mode.
- Parallel builder agents inside one slice.
Assumptions:
- **Approval even under `take recommendations`.** Lanes cost tokens and add to Michael's review queue, and in cre-list he made the call himself; the chat agreed the hub proposes and he approves once per run.
- **Lane runs keep the spec's policies.** In cre-list, Lane B ran under the spec's `until blocked`, `take recommendations` and design setting with its own cap of 5; the hub's prompt sets the cap.
- **The tool is named by what it does.** The rules say "the app's start-session tool" rather than a tool id, since the id belongs to the host.
- **The proposal is not a stop.** `until blocked` forbids stops between slices, so the hub states the proposal in its first slice report and at each milestone end and keeps working; a yes covers the rest of the run, a no stands until the next run.
- **Ownership while lanes run** (from the first verify). A lane's area belongs to it; each session counts, watches and fixes only its own slices and PRs; milestone-end work is the hub's alone; a lane's every stop ends it with a report to the hub; and anything Bosun would ask or report to the user goes to the hub. When only lane work is left, the hub ends its turn and the app wakes it.
- **Ownership, second verify.** A lane decides only its own area's undecided items; the default branch is the hub's to fix; the hub's hygiene slice skips a running lane's area; the setup slice runs only after Michael's yes; a woken hub continues the same run; hand-started lanes relay through Michael.
- **"Several" means at least three** runnable slices per area: fewer does not repay a lane's setup and review overhead.
- **No separate skill.** With the Codex copy gone, lanes live in the core rules and `/bosun-brief`, where the hub already is.
- **Versioning.** Minor bump: new behavior.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in N5. No end-to-end suite; CI's `checks` job is the required check.
Branch: lanes, from main (60b259e).

## Undecided

(none)

## Out of scope

(2026-10-30, remove-codex) Lines below about Codex, Astra, crew workers, the worker script and Sol, Luna, Terra or Reserve models are moot: those pieces were removed in 0.18.0.

- Any change to fable-mode behavior beyond inserting the mode branch.
- A cost ledger, dashboard, or budget cap. Usage numbers go in the spec's slice log and the report only.
- Porting the verifier or the brief to Codex. Both stay on Fable.
- Codex hooks, guard scripts, or hook-trust flags. The worker is bounded by the sandbox and the prompt only.
- `gpt-5.6-terra` or any model not in the table.
- Parallel workers.
- Parallel slices in separate worktrees (slice 3; covered 2026-10-20 by the parallel-lanes slice, removed 2026-10-26 by remove-lanes, covered again 2026-10-30 by the lanes slice as hub-started sessions; the core rules' "Lanes" section).
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
- Simulator MCP on the astra-crew worker TOMLs; those carry Playwright always, and a simulator server started in every project is not wanted. Follow-up (mobile-verify).
- Android as a named surface in the rule text. `mobile-mcp` supports it, but no rule names it until a project needs it (mobile-verify).
- Real devices, cloud devices, and the mobile MCP's location, clipboard, and recording tools (mobile-verify).
- Granting the desktop app's own iOS Simulator tool to any agent (mobile-verify).
- The design/prototyping skill discussed the same day; it is a separate skill, not part of Bosun (mobile-verify).

## Current slice

Name: planning-hub (2026-10-30). Mode: opus (Opus 5.5 leads and implements). Status: verified PASS 2026-10-30 (first verify PASS WITH FOLLOW-UPS: a lane could fix a red default branch itself, no milestones once lanes started, the hub's spec edits had no path to main, lane end with work left, caps past `max N`, hygiene ownership, shape precedence, README; all fixed; second PASS WITH FOLLOW-UPS: unscoped "no code", re-pick of parked work, held files; fixed; third PASS).
Decisions: see the 2026-10-30 "Planning hub" entry under Decisions.
Outcome: Once lanes start, the hub stops building and becomes the session Michael plans and decides in. It keeps the spec, reviews with him, watches the default branch, and hands every code change to a lane. A run uses one of three shapes: hub plus one lane, hub plus two lanes, or one session.
Done-conditions:
H1. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS, third PASS; fingerprint f3806ae` `rules/core.md` "Lanes" is rewritten around a hub that does not build:
   - **The hub's job.** While lanes run, the hub writes no code. It plans, decides with the user, keeps the spec, runs milestone triage and the CI audit, reviews screens with the user, watches the default branch, and relays between the user and the lanes.
   - **Shapes.** One session as before: fewer than five runnable slices in the run, or the user says they won't be steering (takes precedence). Hub plus two lanes: two independent areas, each with at least three runnable slices; work fitting neither goes to the first lane to finish. Otherwise hub plus one lane, taking all the run's work. At most three sessions run.
   - **Before the yes.** Until the user approves, the hub runs as one session as before. After the yes, it finishes its current slice and then stops building.
   - **Code goes to lanes.** Every change goes to a lane as a slice the hub assigns, at the top of that lane's queue: a shared-file change (one lane at a time holds a shared file), a red default branch (assigned as the next slice of one lane; a lane that sees it red tells the hub and finishes its current slice), the milestone hygiene slice and CI-audit fixes (given to the lane whose area holds the files).
   - **Count.** The run's `max N` bounds the slices the hub built before lanes started plus every lane's cap.
   - **Idle hub.** With lanes running and no planning work, the hub ends its turn. This is a pause, not a stop. A lane's message, a lane's end or the user wakes it, and it continues the same run.
   - Stack isolation, the user-only items, checks in a lane, lane end and hand-started lanes carry over.
H2. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS, third PASS; fingerprint f3806ae` The "Run policy" stop list in `rules/core.md` and the "Until blocked" stop list in `skills/bosun-brief/SKILL.md` drop the "hub's own area has no runnable work while lanes still run" stop. Each instead says that a hub with lanes running and no planning work pauses as H1 says.
H3. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS, third PASS; fingerprint f3806ae` `skills/bosun-brief/SKILL.md` "Lanes" follows H1:
   - step 1 chooses the shape;
   - step 2's proposal names the shape;
   - the hub stops building after the yes;
   - the template says the hub plans and does not build, that shared-file changes, red-default-branch fixes and hygiene come as hub-assigned slices at the top of the queue, and that a lane works only its own area and those assigned slices;
   - the "While lanes run" paragraph describes the planning hub.
H4. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS, third PASS; fingerprint f3806ae` README "Lanes" describes the planning hub and the three shapes. Version 0.20.0 in both manifests and the README version line.
H5. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS, third PASS; fingerprint f3806ae` Checks pass:
   - `bash -n scripts/*.sh`;
   - JSON parses for both manifests and `hooks/hooks.json`;
   - `python3 -m py_compile scripts/configure-claude-agents.py`;
   - `claude plugin validate .`;
   - `git diff origin/main --check`;
   - `grep -n "own area has no runnable work" rules/core.md skills/bosun-brief/SKILL.md README.md` finds nothing.
H6. `verified 2026-10-30 bosun-verifier (claude-opus-5-5/high), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS, third PASS; fingerprint f3806ae` This spec:
   - the decision entry;
   - the lanes brief moved to history;
   - the three lanes follow-up nits (stop vs pause, bugs outliving a milestone, waking the hub on a red default branch) removed as resolved by H1;
   - a deferral follow-up for a third lane;
   - the slice log line.
Out of scope:
- A third lane, or a `Lanes: max N` spec line (deferred by Michael).
- Any project's spec or stack script.
- Changes to agents or to other skills.
- Running this on a project.
Assumptions:
- **"Short" means fewer than five runnable slices.** Below that, a lane's cold start and the extra session cost more than a planning hub saves.
- **The hub still edits the spec.** Bookkeeping, decisions and triage are planning, not code. A slice's own brief and statuses stay with the lane that runs it.
- **Shared files are held one lane at a time.** The hub assigns the change to one lane as a slice, so two lanes never edit a shared file at once.
- **A red default branch goes to one lane.** It becomes that lane's next slice. The other lane finishes its current slice and keeps going; its PRs merge once the fix lands, as "Merge flow" says.
- **From the first verify.** A lane that sees a red default branch never fixes it unassigned and keeps working its area. Without milestone groups, milestones count every fifth slice merged across the run. The hub lands its spec edits through short spec-only PRs. When lanes end with work left, the hub picks the shape again under the same yes, building again as one session if no lane shape fits. Caps are set at lane start within `max N`. Hygiene and CI work spanning areas or shared files goes to one lane, and a lane's own hygiene trigger counts only its area's bugs. From the second verify: "no code" applies while lanes run; the re-pick after the last lane leaves out work parked on two FAILs or a user-only item; the hub tells a lane which of its files another lane holds.
- **Lane messages wake the hub.** In the cre-list run, Lane B's messages arrived as new turns in the hub, which resolves the third nit.
- **Versioning.** Minor bump, because behavior changes.
Effort assumed: the session's setting (not exposed to the lead).
Verifier effort: high (no override at any scope).
Checks: as in H5. No end-to-end suite; CI's `checks` job is the required check.
Branch: planning-hub, from main (2422d2a).

## Launch and operate (drafts)

Proposals from the 2026-10-26 discussion, recorded at Michael's request; none is a done-condition until he says so.

- D1 (draft): a thin `bosun-launch` skill writes a "Launch" milestone into an app's spec, built through ordinary slices. It has three parts.
  - **Harden:**
    - security review, including auth, row-level security and rate limits;
    - no secrets in client bundles;
    - backup and a tested restore;
    - error tracking and uptime checks;
    - legal pages;
    - prompt-injection tests and spend caps for AI features;
    - help docs for each core task, which AI support answers from.
  - **Go to market:**
    - a public page that explains and sells the product, kept deliberately vague, with no design instructions (Michael works it out with Claude and may codify a skill after a few runs);
    - a short marketing plan: the buyer, where they spend time, two or three chosen channels (directories, communities such as Reddit and X, social sharing, Google Ads after conversion is measured, AI search, an email list), a launch-week sequence, and attribution through UTM tags and PostHog. Claude drafts posts and Michael posts as himself.
  - **Cut-over:** `factory launch` and its manual steps.
  - Checklists live in reference files. AI-search practice needs its own research pass when the skill is written.
- D2 (draft): a Bosun rule that a slice changing user-visible behavior updates the affected help docs as one of its done-conditions.
- D3 (draft, factory): factory gains Sentry and PostHog groups (already listed there as deferred), and an `intercom` group only when the first app chooses Fin (Doppler holds the app ID and identity-verification secret; the widget is wired with identity verification). Pick a support tool Claude Code can operate through an API or MCP.
- D4 (draft): an operate routine for a solo operator, after an app has real users.
  - A daily pass reads escalated support conversations and drafts replies for Michael to approve and send.
  - It files bugs as spec follow-ups and updates docs where AI support answered badly.
  - An on-call triage agent on the `anthropics/oncall-kit` pattern: read-only toward production, proposes PRs, keeps `lessons.md`, and runs in shadow mode until it clears a replay eval.
  - Agents that read logs never hold factory account tokens or write access to DNS, Doppler or production data, because logs can carry injected instructions ("GhostJacking", DEF CON 34).
- Not planned: a custom in-app AI assistant by default. The support widget answers "how do I"; an assistant that acts on user data is a per-app product feature.

## Follow-ups

(noticed and not done; one line each with the slice, the date, and a tag: `bug`, `drift`, `nit`, or `deferral`; removed when promoted to a done-condition, dropped by the user, or shown resolved in an approved triage batch; lines before 2026-10-11 are untagged)

- provider-modes, 2026-09-02: `marketplace.json` `tags` array was reflowed one-per-line by the JSON rewrite; cosmetic.
- run-policy, 2026-09-03: `skills/bosun-brief/SKILL.md` step 9 reports before "Until blocked" commits and opens the PR, while the rules, README, and design say commit, push, PR, then report; the per-slice report cannot name its PR. Pick one order.
- run-policy, 2026-09-03: `skills/bosun-verify/SKILL.md:20` invites staging under `until blocked` without saying fable-opus mode only, while the brief skill and core rules scope staging to fable-opus mode (crew modes removed 2026-10-30). Say which applies.
- run-policy, 2026-09-03: `README.md` "Version" line says 0.2.0; manifests are at 0.3.0 (already stale on main at 0.2.1).
- runtime-verify, 2026-09-05: `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` descriptions still say "Built from Anthropic's Fable 5.1 docs" while the README intro now also credits Claude Code guidance.
- tests-ci-standard, 2026-09-25: the worker's Tests and CI bullet says to report a test change but not to name the done-condition requiring it, which `bosun-verify` asks the lead for.
- tests-ci-standard, 2026-09-25: `README.md:110` says bosun-ci's guidance references GitHub's documentation; it now also cites Blacksmith and Linear.
- core-rules-rename, 2026-09-25: Blacksmith Testbox (agent-run CI environment, early beta, billed per minute with a 30-minute idle timeout) is deferred by the user. Try it by hand on one project with service-dependent tests before deciding whether the verifier uses it.
- ci-research, 2026-10-07: two-tier CI (Phase 3 of the user's "CI & Testing for Agentic Development" research doc, 2026-10-07, not in this repo: affected-only tests on PRs, full suite on merge and nightly) is deferred by the user. Because PRs auto-merge when green, a design that runs affected-only tests on PRs and the full suite only after merge or nightly lets selection misses land on main; if revisited, run affected tests on PR pushes and the full suite as the required check in a GitHub merge queue (`merge_group`), keep e2e full or path-gated, and confirm merge-queue availability for the repo's plan first. Revisit only if a `bosun-ci` audit shows test execution, not setup, dominates PR time.
- ci-research, 2026-10-07: scheduled `bosun-ci` runs are deferred by the user. If revisited: weekly per project, audit-only (slowest jobs and week-over-week change, runner minutes, flake candidates, setup vs. test time) reported as an issue, fixes through a normal slice, and a CODEOWNERS required review on `.github/workflows/` so CI changes never auto-merge; a nightly full-suite run can feed flake evidence to it. First confirm a scheduled cloud routine has the `gh` access the audit needs.
- bosun-preflight, 2026-10-10: fix-mode header line (`skills/bosun-preflight/SKILL.md:130`) says every header fix is a route done-condition, but a host-config fix is proved by citing the file and line, and a preview route needs its URL supplied in the brief since the verifier starts apps only locally.
- bosun-preflight, 2026-10-10: the beta severity rule (`SKILL.md:41`) does not classify native-mobile findings outside store policy (release debug flags, token storage, deep links, crash reporting); map each to access control or reliability.
- bosun-triage, 2026-10-11, bug: the triage gate (`skills/bosun-triage/SKILL.md:12`) cannot see a slice paused between `bosun-brief` step 6 and verify, since conditions are already `done` and no checkpoint is written; low impact, because the report still lists them for verify and nothing applies without approval.
- runtime-verify, 2026-09-05: whether Claude Code honors the `mcpServers` list-of-maps frontmatter in `agents/bosun-verifier.md` has not been probed; done-condition 46's fable-mode run shows it.
- e2e-cadence, 2026-10-16, nit: `bosun-verify` says the fingerprint command "writes nothing", but `git diff` refreshes the index stat cache (`.git/index` rewritten after a `touch`); no objects are written. A `GIT_OPTIONAL_LOCKS=0` prefix would make the claim exact.
- e2e-cadence, 2026-10-16, nit: the worker Tests and CI bullet lacks the core rules' "at most once per slice", so a fresh worker in a fix round with no required CI e2e check could read its fix as the last change and rerun the full suite.
- e2e-cadence, 2026-10-16, deferral: the fingerprint ignores gitignored files (for example `.env`) and untracked file modes, so an edit to one can leave end-to-end specs skipped on a stale green. Revisit if a project's e2e results depend on ignored files.
- e2e-cadence, 2026-10-16, deferral: cre-list (and its fs3 copies) still carry "No regression" done-conditions and Checks lines that require the full local dev e2e suite; change them when their next slices are briefed. Pilot Blacksmith Testbox there by hand (see the core-rules-rename deferral) only for the slices that still need a pre-push full run, timed against a local run.
- agents-gitignore, 2026-10-19, bug: `bosun-*.md` (the nested ignore and the `git ls-files` pathspec, where `*` also matches `/`) catches user-written agents such as `bosun-custom.md`: they are hidden from `git status`, and the tracked-files note tells the user to `git rm --cached` them. Match only the four generated names. The seven projects' root `.gitignore` lines from 2026-10-19 use the same glob.
- agents-gitignore, 2026-10-19, nit: the tracked-files note splits names on whitespace and prints them unquoted, and its paths are relative to the project, so the command works only from the project directory.
- agents-gitignore, 2026-10-19, bug: a non-UTF-8 user `.claude/agents/.gitignore` makes the run exit 2 (UnicodeDecodeError) instead of being left alone with the note; nothing is written.
- agents-gitignore, 2026-10-19, nit: a read-only marker-owned ignore with stale content fails after the agents are written, so the run applies partially.
- build-mode, 2026-10-25, nit: `bosun-triage`'s "Apply on approval" still says "a new branch from the default branch" while "Milestone end" branches from the latest slice branch when earlier PRs are unmerged; add "(or the branch 'Milestone end' names)".
- build-mode, 2026-10-25, bug: `bosun-verify`'s PASS WITH FOLLOW-UPS path (fix slice-own bugs, then verify again) has no cap, so a run of re-verifies that each find a new slice-own bug never ends; give it the same limit as the FAIL path.
- remove-lanes, 2026-10-26, deferral: "every fifth slice" (core rules, "Follow-ups and milestones") does not say whether the count is per run or across the project's history, so a spec without milestone groups can end milestones inconsistently. Michael deferred it until build mode has run a few real milestones; revisit then, or when a project names its milestone groups.
- remove-lanes, 2026-10-26, deferral: `bosun-brief` step 9 appends each follow-up with a tag but does not make it name its home (the slice, hygiene slice or milestone it waits for), which the core rules' "Follow-ups and milestones" require. Deferred with the item above; revisit at the same time.
- planning-hub, 2026-10-30, deferral: a third lane (hub plus three), or a `Lanes: max N` spec line. Michael deferred it "after we've continued to use this and explored it"; revisit after a real hub-plus-two-lanes run shows both lanes staying busy without waiting on him or on shared files.

## Slice log

- 2026-10-30, planning-hub, opus (implemented by lead), first verify PASS WITH FOLLOW-UPS (8 gaps, fixed), second PASS WITH FOLLOW-UPS (3 gaps, fixed), third PASS; all bosun-verifier on claude-opus-5-5 / high; route-or-screen done-conditions: 0 of 0.
- 2026-10-30, lanes, opus (implemented by lead), first verify FAIL (13 findings, fixed), second PASS WITH FOLLOW-UPS (8 gaps, fixed), third PASS; all bosun-verifier on claude-opus-5-5 / high; route-or-screen done-conditions: 0 of 0.
- 2026-10-30, remove-codex, opus (implemented by lead), first verify PASS WITH FOLLOW-UPS (one README rendering bug and five wording nits; fixed), second PASS; both bosun-verifier on claude-opus-5-5 / high; route-or-screen done-conditions: 0 of 0.
- 2026-10-26, merge-flow, opus (implemented by lead), first verify FAIL (wait deadlock, spec edits broke independence, triage still stacked, unverified red-PR fixes, update-branch churn, no default-branch check, no `one slice` rule; all fixed), second PASS WITH FOLLOW-UPS (six wording and stall gaps; fixed), third PASS; all bosun-verifier on claude-opus-5-5 / high; route-or-screen done-conditions: 0 of 0. Repos: rv-rez's up-to-date requirement turned off; quillery and project-hearth already matched; mom-ai (amdg-org/ruthie) has no CI yet.
- 2026-10-26, remove-lanes, opus (implemented by lead), first verify FAIL (cleanup could delete the default branch and branches with no commits of their own, and ignored files such as `.env`; two wording nits; all fixed), second PASS WITH FOLLOW-UPS (merged-PR test now limited to PRs into the default branch; README nit; fixed), third PASS; all bosun-verifier on claude-opus-5-5 / high; route-or-screen done-conditions: 0 of 0.
- 2026-10-25, build-mode, opus (implemented by lead), first verify FAIL (undecided items still stopped take-recommendations runs, plus six text findings; all fixed), second PASS WITH FOLLOW-UPS (two follow-ups recorded); both bosun-verifier on claude-opus-5-5 / high; B1–B9 verified; route-or-screen done-conditions: 0 of 0.
- 2026-10-20, parallel-lanes, opus (implemented by lead), first verify PASS WITH FOLLOW-UPS (seven text findings, fixed), second FAIL (lane end lost statuses and slice log; L1 text stale; staged briefs and mid-slice sessions skipped the overlap check; stale local default branch; core stop list; all fixed), third PASS WITH FOLLOW-UPS (six follow-ups recorded); all bosun-verifier on claude-opus-5-5 / high; L1–L4 verified; route-or-screen done-conditions: 0 of 0.
- 2026-10-19, ci-checks, opus (implemented by lead, at the user's request "Lets do it"; no verifier run, one-file workflow): `.github/workflows/checks.yml` runs the slice checks (shell syntax, JSON and TOML parsing, Python compile, `git diff --check`, `claude plugin validate .`) on every PR on a GitHub-hosted runner (personal repo, so no Blacksmith); its `checks` job is the required check on `main` (strict, admins enforced), so PRs here auto-merge on green. First run 13 s, all steps passed; merged as #20.
- 2026-10-19, agents-gitignore, opus (implemented by lead), first verify PASS WITH FOLLOW-UPS (bosun-verifier on claude-opus-5-5 / high; four follow-ups recorded); A1–A4 verified; route-or-screen done-conditions: 0 of 0.
- 2026-10-16, e2e-cadence, opus (implemented by lead), first verify FAIL (six findings: fingerprint quoting, external diff, subdirectory, spec edits and worker modes; worker default; verifier shell allowance; all fixed), second PASS WITH FOLLOW-UPS (two nits and one deferral recorded); both bosun-verifier on claude-opus-5-5 / high; E1–E6 verified; route-or-screen done-conditions: 0 of 0.
- 2026-10-11, bosun-triage, opus (implemented by lead), first verify PASS WITH FOLLOW-UPS (six follow-ups, fixed in-slice at the user's request), second PASS WITH FOLLOW-UPS (four errors in the fixes, corrected), third PASS WITH FOLLOW-UPS (one follow-up recorded); all bosun-verifier on claude-opus-5-5 / high; G1–G5 verified, G6 human-check; route-or-screen done-conditions: 0 of 0.
- 2026-10-10, bosun-preflight, opus (implemented by lead), first verify FAIL (P1 severity clause narrower than written, plus eight skill-text correctness findings, all fixed; P1 reworded to the chosen rule), second verify PASS WITH FOLLOW-UPS; four follow-ups fixed at the user's request, third verify PASS WITH FOLLOW-UPS (two wording follow-ups recorded); all bosun-verifier on claude-opus-5-5 / high; P1–P5 verified, P6 human-check; route-or-screen done-conditions: 0 of 0.
- 2026-10-07, ci-research-guidance, opus (implemented by lead), first verify PASS WITH FOLLOW-UPS (bosun-verifier on claude-opus-5-5 / high); C1–C5 verified; the three wording follow-ups fixed at the user's request, re-verify PASS (same verifier and effort); route-or-screen done-conditions: 0 of 0.
- 2026-09-25, tests-ci-standard, opus (implemented by lead), first verify FAIL (worker bullets missed the don't-undo-optimizations clause; the verifier had no way to receive the implementer's test and CI statements), second verify PASS WITH FOLLOW-UPS, both bosun-verifier on claude-opus-5-5 / high; T1–T8 verified; route-or-screen done-conditions: 0 of 0.
- 2026-09-25, core-rules-rename, opus (implemented by lead), first verify PASS (bosun-verifier on claude-opus-5-5 / high); R1–R7 verified; route-or-screen done-conditions: 0 of 0.
- 2026-09-22, opus-modes-and-verifier-effort, astra (implemented by lead), first structural verify PASS WITH FOLLOW-UPS; final verify PASS, O1–O6 verified. Model ID `claude-opus-5-5` confirmed from Anthropic live announcement. Lead: temporary-project mode/effort mutation matrix, idempotence, return-to-Fable, invalid inputs, collision and symlink refusal. Independent verifier: 20 dry-runs, five invalid inputs, shell syntax, 13 JSON/TOML files, changed frontmatter, both Claude validators, existing Sol worker dry-run, diff whitespace. Route/screen checks: 0 of 0. No live Claude agent execution, installation, or publication.

- 2026-09-16, mobile-verify-followups, fable-crew (gpt-5.6-luna / max, task class small), first verify PASS; the five mobile-verify follow-ups fixed and removed from the follow-ups section; route-or-screen done-conditions: 0 of 0. Usage: 162 s wall, 291,516 input (246,784 cached), 8,183 output (3,650 reasoning).
- 2026-09-16, mobile-verify, fable-crew (gpt-5.6-sol / high, task class feature), first verify PASS WITH FOLLOW-UPS; done-conditions 51–58 verified, 59 human-check; route-or-screen done-conditions: 0 of 0. Usage: not recorded; the worker was killed by a Claude Code session restart after its last edit and before its report (events.jsonl has 32 events and no turn.completed), so no usage.json exists. Lead-run checks: MCP handshake, and a no-op --simulator worker run (Luna/low, 5 s, 12,742 input of which 8,960 cached, 5 output).
- 2026-09-15, bosun-ci, astra mode (implemented by Astra), first verify PASS; done-conditions 47–49 verified, 50 human-check; route-or-screen done-conditions: 0 of 0.

(each codex-mode slice appends: date, slice name, task class, route, first-verify verdict, usage)

- 2026-09-05, runtime-verify, fable mode (implemented by Fable), first verify PASS WITH FOLLOW-UPS; route-or-screen done-conditions: 0 of 0.
- 2026-09-04, bosun-rename, fable mode (implemented by Fable), first verify PASS WITH FOLLOW-UPS.
- 2026-09-04, codex-port, fable mode (implemented by Fable), first verify PASS WITH FOLLOW-UPS.
- 2026-09-03, run-policy, fable mode (implemented by Fable), first verify PASS WITH FOLLOW-UPS.
- 2026-09-02, provider-modes, fable mode (this slice was implemented by Fable), first verify PASS WITH FOLLOW-UPS. Smoke run of the worker script only: gpt-5.6-luna / low, 4 s, 16,824 input (8,960 cached), 5 output tokens.

## Lessons

(none; the Codex-only lessons were removed with the Codex side on 2026-10-30)

## Public readiness slice — September 15, 2026

Authority: Michael approved reviewing and cleaning Bosun for public sharing; selected MIT explicitly.
Outcome: clear public onboarding, accurate validation limits, MIT license, and contribution guidance.
Done-conditions: P1 README explains intended user, role split, quickstart and prerequisites; P2 stale blanket untested claims replaced with evidence-linked limitations; P3 MIT license and contribution checks present; P4 manifest/shell/parser checks and CLI install-command availability checked with results reported; P5 tracked-file/history pattern scan reports findings without exposing secrets.
Out of scope: runtime/model routing changes, paid model runs, broad refactoring, production changes, automatic merge.
Assumptions: public-readiness changes are based on published main, excluding the separate uncommitted CI skill work.
Mode: astra. Branch: codex/public-readiness. Status: verified, ready for PR review.
Validation limits: clean installation and full live runs in every supported mode remain unverified. Static checks do not establish those outcomes.

Verification (2026-09-15): independent verifier PASS after correcting quickstart order and shell escaping. Shell syntax, both Claude validators, 12 JSON/TOML parses, worker dry-run, CLI install-command help, and diff whitespace checks all passed. Pattern screening was independently repeated across 27 reachable commits, 140 unique blobs, and 32 working files with no matches; public author email remains in metadata. Screening excludes unreachable objects and external artifacts and is not proof of absence. No runtime, global installation, model execution, or production changes were made. Next action: review and merge this documentation-only PR before sharing the updated onboarding.
