# Bosun

Bosun coordinates coding work through a durable spec, scoped implementation tasks, and verification in a fresh session. It is for developers who want their coding agents to keep track of the requirements and check the result before calling a task done.

Bosun is a Claude Code plugin with three provider modes: `fable` (Fable 5.1 in every role), `fable-opus` (Fable 5.1 leads and verifies, an Opus 5.5 subagent implements) and `opus` (Opus 5.5 in every role). The Codex plugin and the `fable-crew`, `astra-crew` and `astra` modes were removed in 0.18.0.

## Start here

1. Install the plugin below.
2. In a new project, invoke `/bosun-brief <your task>`. Bosun creates a spec and stops for your review.
3. Review the spec, then select a mode with `/bosun-mode opus` (or `fable`, `fable-opus`). With an existing spec, select the mode before briefing. Say go to start the slice.
4. Review the result and verification evidence. A failed or unavailable check is not proof of completion.

For example, ask Bosun to add a CSV export to an existing report, preserving its current filters. The spec defines the expected columns and behavior; the lead (or its worker) implements the scoped change; a separate verifier checks it against those requirements. This is an illustrative workflow, not a benchmark result.

You need Claude Code installed, authenticated access to the configured models, and Git. Browser checks additionally use Node.js/npx and Playwright; native-screen checks require macOS with Xcode and an iOS simulator. Model availability depends on your host and account. Bosun does not bundle models or bypass usage limits. Start in a disposable project before using continuous runs on important work.

## Install

```bash
claude plugin marketplace add mckissinger/bosun
claude plugin install bosun@bosun
```

The plugin's core rules load automatically at session start through a hook. To make them part of your global instructions instead (one less thing printed each session), append `rules/core.md` to `~/.claude/CLAUDE.md`; the hook detects its heading, `# Bosun core rules (Claude Code)`, and stops printing them. Before 0.9.0 the file was `rules/fable.md` with the heading `# Fable 5.1 agentic development`; if you appended that, remove it and append the new file.

Optional, per the effort doc's "set effort explicitly": add to `~/.claude/settings.json`

```json
{ "modelSettings": { "claude-fable-5-1": { "effortLevel": "high" } } }
```

## The shape

```
launch session at the right effort
  -> /bosun-brief   (no spec: write it, stop for review | spec: brief next slice, run)
  -> work, updating spec status as done-conditions land
  -> /bosun-verify  (fresh read-only verifier; marks verified in spec)
  -> report; /bosun-checkpoint only if stopping mid-slice
  -> under "Run policy: until blocked": commit, push, PR with auto-merge, next slice, until something stops it
```

## What is in the plugin

| Piece | Path | Job |
| --- | --- | --- |
| Core rules | `rules/core.md` | Effort policy, spec contract, scope and test limits, tests and CI rules, targeted edits, delegation, refusal recovery, finishing |
| `/bosun-brief` | `skills/bosun-brief/SKILL.md` | Creates the spec on first run and stops for review; afterwards briefs a slice and runs it to completion |
| `/bosun-verify` | `skills/bosun-verify/SKILL.md` | Fresh-context verification against the spec, records verified status |
| `/bosun-checkpoint` | `skills/bosun-checkpoint/SKILL.md` | Transient mid-slice state the spec does not hold |
| `/bosun-ci` | `skills/bosun-ci/SKILL.md` | Audit GitHub Actions bottlenecks or implement and verify a focused CI improvement |
| `/bosun-preflight` | `skills/bosun-preflight/SKILL.md` | Audit a feature-complete app for production readiness, or fix chosen findings through verified slices |
| `/bosun-triage` | `skills/bosun-triage/SKILL.md` | Review the spec against code and history: fix statuses, clear resolved follow-ups, surface what is waiting on you |
| `/bosun-mode` | `skills/bosun-mode/SKILL.md` | Sets or reports the provider mode line in the spec and configures the project-local agents |
| Claude agent setup | `scripts/configure-claude-agents.py` | Generates project-local worker/verifier definitions; applies verifier effort without changing lead or worker effort |
| `bosun-worker-opus` agent | `agents/bosun-worker-opus.md` | Opus 5.5 implementation at high; no spec edits, commits, or delegation |
| `bosun-scout` agent | `agents/bosun-scout.md` | Read-only background investigator, medium effort |
| `bosun-verifier` agent | `agents/bosun-verifier.md` | Read-only Fable/Opus verifier selected by mode, selectable effort (default high), with Playwright for done-conditions that name a route or screen |
| `bosun-verifier-mobile` agent | `agents/bosun-verifier-mobile.md` | Read-only Fable/Opus verifier selected by mode, selectable effort (default high), with a simulator MCP server for done-conditions that name a native iOS screen |
| SessionStart hook | `scripts/session-start.sh` | Loads the rules if needed, points at the spec with its provider mode and run policy, prints any checkpoint; on compaction, tells the model to re-read the spec |

Checkpoints are written to `~/.claude/bosun/checkpoints/<project-slug>.md`.

## The spec

`SPEC.md` at the repo root, or wherever the repo's docs convention puts it. It is the only input a fresh session needs. The harness fixes what it must contain, not how it is laid out:

- the outcome
- decisions, in the user's own words
- done-conditions with a status, each checkable by the verifier's tools (git diff, file reads, the repo's checks, and a browser for a done-condition that names a route or screen) or marked human-check
- undecided items, as questions
- out-of-scope items
- the current slice
- follow-ups: things noticed and not done, one line each with the slice, the date, and a tag (`bug`, `drift`, `nit`, `deferral`); the exhausted-roadmap report draws its proposals from here, and `/bosun-triage` clears the ones it shows resolved once you approve (or itself, at a milestone end under `Decisions: take recommendations`)
- lessons: what a fresh session needs to know about this codebase that the repo does not already record

The model chooses the layout per project, keeps it reviewable by a person in one sitting, and reorganizes or splits it when it stops being that. Status is updated as work lands, so a crash mid-run loses little. The test of the spec: with the checkpoint deleted, can a fresh session continue from spec, branch, and git log? If not, the spec is incomplete.

## Daily use

1. Launch at the effort the work needs: `claude --effort high` for most slices, `xhigh` for long runs, migrations, hard bugs. Effort is held for the session; the model cannot change it.
2. New project: `/bosun-brief <task>` with your structures pasted or pointed at. Review the spec it writes, fill in what you can, say go. That is the one planned stop.
3. Existing spec: `/bosun-brief` (optionally naming the slice). It runs to completion, verifies, and reports. With `Run policy: until blocked, max N slices` in the spec it keeps going, one branch and one PR per slice, until something stops it; see "Run policy".
4. Read the report: done-conditions with evidence, follow-ups, anything left out. Human-check conditions are yours.
5. Stopping mid-slice: `/bosun-checkpoint`. The next session in that directory loads it.

## CI improvement

Use `/bosun-ci audit CI` for a read-only review of GitHub Actions workflows and recent runs. The report ranks bottlenecks by evidence, expected benefit, effort, and coverage risk. Run history requires authenticated GitHub tooling or exported data; without it, the skill can produce a static audit with unmeasured hypotheses.

Use `/bosun-ci speed up CI` to investigate and implement a focused improvement through the existing brief and independent verification workflow. It compares elapsed time, total runner minutes, and reliability, preserving required checks and explaining every removed or conditional check. Warm/cold caches and differences between runs are reported; local validation alone never establishes a hosted speedup. Findings and evidence go in the existing spec.

V1 supports GitHub Actions. Blacksmith runners are the standard: the skill recommends moving GitHub-hosted jobs to them and makes the move only when asked. Deployment changes and repository protection changes need their own scope. This skill is an engineering extension to Bosun; its CI-specific guidance references GitHub's official documentation.

## Production preflight

Use `/bosun-preflight` when an app is feature-complete and before it launches. The audit reads the whole app and reports a ranked punch list (blockers, should-fix, later) across security, abuse and cost guardrails, reliability, legal and data, product polish, operations, and native mobile. Every finding cites a file, a command's output, or a browser observation, and what could not be checked is listed separately. When the project has a spec, the audit records its verdict there in a "Production preflight" section. Ask it to fix chosen findings, or "fix the blockers", and each fix runs as a slice with a done-condition that proves it, such as a test of the denied case. It does not deploy or change hosted settings; those go to you as manual steps.

## Spec triage

Follow-ups pile up, statuses drift, and deferrals get lost as slices land. Use `/bosun-triage`, between slices, to review the spec against the code and git history. The report proposes removing follow-ups that are resolved, obsolete, or duplicated (each with its evidence), corrects statuses, tags the follow-ups that remain (`bug`, `drift`, `nit`, `deferral`), groups them into draft slices, finds decisions that never became done-conditions, and lists the human-checks and deferrals waiting on you. It also lists leftover worktrees and local branches, and marks as removable each one, never the default branch, whose PR merged into the default branch has its tip as head commit, with no uncommitted or untracked files, no ignored files beyond dependency and build output, and no process running inside it; worktrees the Claude desktop app made are left to the app, and remote branches are never touched. Nothing changes until you approve (apart from refreshing remote-tracking refs and dropping records of worktrees whose directory is already gone), except at a milestone end under `Decisions: take recommendations`, where the lead applies the evidence-backed removals and status corrections, promotes open bugs to a hygiene slice, and removes the removable worktrees and branches itself. Approved changes land as spec bookkeeping only; a reorder that puts live content ahead of finished work is a pure move, checked line by line, and nothing is condensed or reworded.

## Provider modes

The mode is a line in the project's spec, `Provider mode: <mode>`. No line means `fable`. `/bosun-mode <mode>` sets it; `/bosun-mode` alone reports it.

| Mode | Lead | Implementation |
| --- | --- | --- |
| `fable` | Fable 5.1 | Fable 5.1 |
| `fable-opus` | Fable 5.1 | Opus 5.5 at high as a native subagent |
| `opus` | Opus 5.5 | Opus 5.5 (also scout and verifier) |

The values `codex`, `fable-crew`, `astra-crew` and `astra` were removed in 0.18.0 with the Codex plugin and the Codex worker. A spec that still names one makes `/bosun-brief` and `/bosun-verify` stop and say to pick one of the three modes with `/bosun-mode`.

**Opus throughout.** In Claude Code, select `/bosun-mode opus` and use an Opus 5.5 lead session (`claude --model claude-opus-5-5` or `/model claude-opus-5-5`). Opus briefs, implements directly, keeps the spec, and commits; the local scout and fresh web/mobile verifier also use Opus. Mode selection changes the spec and generated agents, not the active session model: confirm that model before starting a slice. Switching back to a Fable mode regenerates the local scout/verifiers on Fable and requires a Fable lead session. There is no model fallback. Live account/model access must be verified separately.

**Fable with Opus implementation.** In Claude Code, select `/bosun-mode fable-opus`. Fable 5.1 briefs, keeps the spec, reviews, commits, and verifies; a native `bosun-worker-opus` subagent implements on `claude-opus-5-5` at `high`. FAIL findings return to Opus. The worker cannot delegate and never commits or edits the spec. This mode needs access to Opus 5.5 and Fable 5.1 in Claude Code. Worker or model failures stop the slice; there is no provider fallback. The route and verdict are recorded in the spec.

**Verifier effort.** Set a project default while selecting a mode, or change it independently:

```text
/bosun-mode fable-opus --verifier-effort xhigh
/bosun-mode --verifier-effort medium
/bosun-verify --effort max
```

The last command overrides effort for that verification and its retries only. Supported values are `low`, `medium`, `high`, `xhigh`, `max`; default is `high`. Resolution is invocation override, current-slice `Verifier effort:`, top-level `Verifier effort:`, then `high`. The mode command changes the top-level default, preserving a current-slice override if present. Effort is recorded per attempt. Both web and mobile verifiers use Opus 5.5 in `opus` and Fable 5.1 in the Fable modes, independently of the lead session and Opus worker. These controls work in all three modes.

Mode selection and verification run `scripts/configure-claude-agents.py` to write the effective settings into `.claude/agents/bosun-scout.md`, `bosun-verifier.md`, and `bosun-verifier-mobile.md`; `fable-opus` also installs `bosun-worker-opus.md`. These project-local copies take precedence over plugin definitions and retain their MCP servers. The next verification regenerates the copies from the current setting, so a one-run override cannot become the default. The generator refuses to overwrite unrelated user-owned files or symlinks. Keep the spec as the settings source. The generator also writes `.claude/agents/.gitignore` so git ignores the generated copies, and names any that a project still tracks with the `git rm --cached` command to stop; it leaves a `.gitignore` there that it did not write unchanged. Plugin installation alone does not generate these files.

Restart Claude Code if setup creates the project's first `.claude/agents/` directory, then confirm the local agents are loaded. Invoke those local names, not plugin-scoped `bosun:...` agents. Claude Code ignores MCP configuration on plugin-bundled agents; project-local definitions are used so the worker and verifier actually receive their browser/simulator tools. Existing generated files are refreshed by setup, including after a plugin update. A conflicting model environment override must be resolved before claiming a pinned model ran. See [Claude Code's subagent configuration](https://code.claude.com/docs/en/sub-agents) and [Opus 5.5 release and model identifier](https://www.anthropic.com/claude-opus-5-5).

## Runtime verification

A done-condition may name a route or screen ("`/settings` shows the new toggle") and still count as checkable, because both the implementer and the verifier have a browser.

The implementer runs the app and looks before marking such a done-condition done, and records one evidence line per done-condition: the route, what was checked, and a screenshot path if one was taken. The lead uses the desktop browser pane or Playwright MCP, and the `bosun-worker-opus` worker gets Playwright MCP through its project-local definition. Screenshots are evidence when appearance matters; the accessibility snapshot is the cheaper check for text and structure. Nobody walks the whole app.

The verifier gets Playwright too (an inline `mcpServers` entry on `bosun-verifier`). It uses the browser only to re-check the route-or-screen done-conditions, following the implementer's evidence lines, may start the app with the launch command the brief names, stops it afterward, and reports screenshot paths as evidence. Each slice-log line records how many done-conditions named a route or screen and how many the verifier confirmed, so runtime verification can be compared across modes and projects.

For native iOS screens, the brief says `Surface: ios` and the evidence line records the screen, device, what was checked, and screenshot path. `bosun-verifier-mobile` uses the mobile simulator MCP server. The lead or verifier may boot the named device with `xcrun simctl boot` and must shut down any simulator it booted with `xcrun simctl shutdown`. Native-screen checks require macOS with Xcode and an iOS simulator.

Requires `npx` able to fetch or find `@playwright/mcp` and a Chromium; the first run downloads them.

## Run policy

A Claude Code session is turn-based: when the model ends its turn, nothing happens until something wakes it. The default harness ends the turn after every slice, so the user waits between slices. The run policy removes most of that idle time without changing what gets built.

The policy is a line in the spec next to the provider mode: `Run policy: one slice` (the default; no line means the same) or `Run policy: until blocked, max N slices` (`until blocked` alone means `max 10 slices`). Under `until blocked`, after a slice verifies, the lead commits, pushes, opens a PR for that slice's branch, arms auto-merge (`gh pr merge <n> --auto --merge`), reports, and briefs the next slice in the same turn, without idling on CI and without asking whether to go on (see "Merge flow" for which slices it builds while CI runs, and when it waits). Every slice keeps its own branch and PR. Auto-merge lands it once the required checks pass; if GitHub refuses auto-merge because every required check is already green, the lead merges it with `gh pr merge <n> --merge`. It never merges past a red or missing required check or bypasses branch protection, and it leaves the PR open and says so when the repo has no required checks, disallows auto-merge, or the spec or your instructions keep merging for you. The run stops, and the report says why, at the first of: no runnable done-condition left; every remaining runnable item needs a decision the lead may not make (see "Decisions"); two FAILs on one verify finding (three under `Decisions: take recommendations`); every remaining slice waiting on a PR that cannot merge on its own; the slice cap. A done-condition is runnable when it is `todo` or `in progress`, not `human-check`, and needs nothing on the undecided list.

**Merge flow.** While a PR's checks run, the lead builds ahead only on slices that need nothing from an unmerged slice, each in its own worktree cut from the latest default branch; a dependent slice is briefed then and built after its base merges, and branches are never stacked on unmerged ones. When only dependent work is left, the lead waits for the base PR, but only if it merges on its own; otherwise the run stops and names it. Every slice writes the spec, so each built-ahead slice adds its brief as its own subsection and appends to the log, and a spec conflict between two PRs is resolved by keeping both sides. Before each slice, after each verify, and while waiting, the lead checks its open PRs and the default branch's latest CI run: a red or conflicting PR pauses the current slice while the lead fixes it on that PR's branch (verifying a code fix), then it resumes, and a red default branch is fixed first. The recommended setup is a GitHub merge queue (available on organization-owned public repositories and on GitHub Enterprise Cloud) with required checks also triggered on `merge_group`, and a `merge_group` fallback for any job that reads a PR number. Without a queue, turn off "require branches to be up to date" and run CI on every push to the default branch: PRs then merge as soon as their own checks pass, and a red run on the default branch is fixed like a red PR. If a repo keeps the up-to-date requirement without a queue, the lead updates the oldest behind PR, one at a time, and `/bosun-ci` reports the setting.

**Exhausted roadmap.** When no runnable done-condition remains, under either policy, the lead does not invent work. It reports that the roadmap is exhausted, lists the open human-checks and the undecided questions, proposes next slices drawn from the spec's follow-ups section as clearly marked drafts, and asks what next. A proposal becomes a done-condition only when you say so; under `Decisions: take recommendations`, the lead first decides the undecided items it may decide, and a hygiene slice built from open bug follow-ups counts as runnable work.

**Staging (fable-opus mode).** While the worker runs, under `until blocked` with the cap not reached, Fable scouts the next slice and, if it does not depend on the running one, writes a staged brief to `~/.claude/bosun/workers/<slug>/<next-slice>/brief.md` with a `Based on: <sha>` line. It never writes to the worktree while the worker owns it. If the next slice does depend on the running one, it scouts only.

**Re-validation.** Before a staged brief runs, Fable compares its `Based on:` sha with HEAD. If the previous slice moved it, Fable re-reads the spec and the landed diff, checks every file reference and assumption in the brief, folds in the previous verify's follow-ups that belong to this slice, and only then writes the brief into the spec and generates the worker prompt from it. A staged brief waits on a FAIL, and stays on disk (named in the report) if the run stopped.

**Milestones.** Every follow-up gets a home when it is written: bugs in the slice's own work are fixed in that slice, other bugs by the next slice that touches the file or a hygiene slice before the milestone closes, nits by the next slice that touches the file, deferrals name their target, and anything that needs you goes to human-checks. A milestone is a group of done-conditions the spec names, or every fifth slice. At each milestone end under `until blocked`, the lead runs `/bosun-triage` (which also finds worktrees and local branches whose work is merged and that are clean and idle, and removes them when the triage is applied), a hygiene slice for the open bugs, and a `/bosun-ci` audit. More than five open bugs makes the next slice a hygiene slice.

## Decisions

`Decisions: take recommendations` in the spec (no line means `ask`) lets the lead act on its own recommendations instead of stopping: it decides open questions that come up mid-run, undecided items the spec's outcome or decisions point to, and a two-FAIL disagreement on one verify finding, records each in the spec's decisions as "(build mode, <date>)" with a line of why, and keeps going. A third FAIL on the same finding still stops the run. It never decides credentials, accounts, or sign-ins; prices, fees, or live spend; production data or anything sent to real people; legal, naming, or trademark questions; new-design approval under `Design approval: me`; or anything the spec lists as yours. Work that needs one of those is parked as a human-check or an undecided question with the lead's recommendation, and the run takes other work.

## Design

Every slice that adds or changes a screen runs one loop: read the board and design system, mock up any screen without a board first (on a design canvas when the session has one, with a copy in the repo), get the mockup approved, build, check it at 390, 768, 1024, 1280, and 1440 wide (or the project's widths) in its empty, loading, error, hover, and focus states and its motion, and have a fresh agent compare the screenshots with the board; open differences block the done-condition, and the verifier compares against the board too. `Design approval: me` (the default for a project with UI) means you approve each mockup, and a new direction or interaction pattern always waits for you; `Design approval: critique` means a fresh agent critiques the mockup and the board is revised with an "After critique" note. A new direction starts from several fresh options, not variations on an older mockup.

## Other sessions

You can run more than one session on a project, but Bosun does not coordinate them. The core rules keep them from damaging each other: every session that writes code uses its own worktree and branch, never applies an unapproved or unmerged migration to a database another session uses, never resets or stops another session's stack or server, and never stops processes by name.

## Why each piece exists

Sources: [Overview](https://platform.claude.com/docs/en/models/fable-5-1/overview), [What's new](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1), [Migration guide](https://platform.claude.com/docs/en/models/fable-5-1/migration-guide), [Prompting Claude Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1), [Effort](https://platform.claude.com/docs/en/build-with-claude/effort), [Refusals and fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback), [Claude Code effort controls](https://code.claude.com/docs/en/model-config).

**Effort is the primary control.** Adaptive thinking is always on and cannot be turned off. Default is `high`. The prompting guide says start at `high`, step down to `medium` or `low` where quality holds, step up to `xhigh` or `max` only where measured. At `low` the model answers from memory instead of searching. At `xhigh` and `max` it may draft a long deliverable in thinking and again in the reply. Claude cannot change effort inside a session, and the effort doc says to hold it constant within a conversation, so effort is chosen at launch and the brief states the level it assumes.

**Sizing.** The guide says Fable 5.1 "can execute very long tasks without much guidance on methodology, especially when the goal is clear," and pairs `xhigh` with runs over thirty minutes. The harness sizes work as outcomes with done-conditions, not step lists, and drains ambiguity once, in the spec, at the one planned stop.

**Finish the whole task.** The guide's autonomous-operation and "Delivering work" blocks are already injected by Claude Code on Fable 5.1, along with the progress-update line and the per-turn batching nudge, so the harness does not repeat them.

**Scope and tests.** The guide's block on keeping changes and tests to what the task asks for is in the core rules verbatim; the guide reports it cuts unrequested additions with no measurable change in task success.

**Targeted edits.** Fable 5.1 rewrites whole files more than Fable 5 did. The guide's one-sentence fix is in the core rules verbatim.

**Delegation.** The guide says letting the lead keep working while subagents run lowers time to completion at similar quality and cost. `bosun-scout` runs in the background; the core rules tell the lead to keep working.

**Safeguard false positives.** The guide names three triggers: compile-check phrasing, lesser-known languages without context, base64 in tool output. The core rules carry the phrasing and a recovery step: rephrase once, then record the blocked step in the spec and move on.

**Verification.** `/bosun-verify` runs a fresh-context, read-only verifier at the selected effort (default `high`, the documented starting point), so the judgment is independent of the session that did the work. Two FAILs on the same finding stop the loop and go to the user, unless `Decisions: take recommendations` lets the lead decide it; a third FAIL stops it either way.

**Runtime verification.** This is the one rule that does not come from the Fable 5.1 model guide, which says nothing about browsers. It comes from Anthropic's guidance for running Fable in Claude Code: the [Claude Code best practices](https://code.claude.com/docs/en/best-practices) ("Give Claude a check it can run: tests, a build, a screenshot to compare"; "Always provide verification (tests, scripts, screenshots). If you can't verify it, don't ship it"; verification by a second-opinion subagent; show evidence, including screenshots, rather than asserting success), and Anthropic's [long-running agents article](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (the coding agent "needed explicit prompting to use browser automation tools and do all testing as a human would", and a browser "dramatically improved performance"). The model guide says finish the task and keep tests to what the change warrants; the product guidance says a check for visible behavior is a browser. Both roles get one because the implementer's check is the loop that makes the work correct and the verifier's is the independent gate; self-review measurably favors its own output, so the overlap is the point, and it stays cheap because the verifier re-checks named done-conditions only.

**Lessons.** The prompting guide says Fable 5.1 performs notably better when it can write learnings somewhere for future reference, even a plain markdown file, and gives the format: one lesson per entry with a one-line summary, corrections and confirmed approaches alike with why they mattered, update rather than duplicate, delete what turns out wrong, and skip what the repo or history already records. The harness keeps them as a section of the spec, because every point where the harness already forces a spec read (session start, compaction, the brief) then covers them for free. The section splits into its own file only when it stops being readable in one sitting, by the same rule as the rest of the spec.

**Continuity.** The guide's compaction instruction lists six things a summary must preserve. Claude Code does not expose custom compaction instructions, so the harness keeps expectations in the spec, fires a "re-read the spec" reminder from the SessionStart hook when compaction happens, and uses the checkpoint only for transient mid-slice state.

## Lanes

Under `Run policy: until blocked`, a spec with two or more independent areas can run as lanes: separate Claude Code sessions that the lead (the hub) starts, each in its own worktree, each running its own Bosun loop with its own slice cap. The hub proposes the split (areas, the shared files it keeps, lane count, caps) in its first slice report and at each milestone end, and starts lanes only after you say yes, once per run; until then it keeps working as one session. Lanes need isolated tests: when migrations or end-to-end runs share a local stack, the first step is a setup slice that gives each lane its own stack and ports through a command the spec names on a `Stack isolation:` line. Each lane slice branches from the latest default branch and gets its own PR, so nothing stacks; spec conflicts are resolved by keeping both sides. Lanes run under the spec's `Decisions:` setting and send anything that needs you to the hub, which batches it, so you hear from one session. The default is the hub plus one lane, and at most three sessions run. The hub starts lanes itself where the host can start sessions (the Claude Code desktop app); elsewhere it prints the lane prompts for you to start by hand. Milestone-end triage, hygiene and CI audits stay with the hub. The procedure is in `/bosun-brief` ("Lanes") and the rules in the core rules ("Lanes").

## Not covered on purpose

- Parallel builder agents inside one slice. Parallel sessions on one project are covered by "Lanes"; inside a slice, the docs credit the model's gains to long single-context runs.
- API-side migration concerns (beta headers, append-only message arrays, `tool_choice`, `input_transformations`, fallback middleware). Claude Code manages the conversation prefix itself. If you call the Messages API directly, read the migration guide's "Preserved thinking" section first.

## Status

Version 0.19.0. The [spec](SPEC.md) records implemented slices, verification evidence, and outstanding human checks. Static validation and worker/browser smoke checks are recorded there, along with verified development slices. Full end-to-end checks across all modes, host hook behavior remain partially unverified. Do not interpret the version number as a guarantee that every host/model combination has been exercised.

There is no controlled performance benchmark establishing cost, speed, or quality improvements. Those depend on the project, model access, provider mode, and verification workload.

## Safety and local data

Bosun delegates through your installed tools and their permissions. Workers can edit project files. Review the rules and SessionStart hooks before enabling them.

Specs, checkpoints, and worker prompts can contain project information. Review them before sharing or committing them. Do not include credentials or customer records in a public example or issue. Continuous runs can commit, push, open pull requests, and arm auto-merge on them under the documented run policy; start with one slice.

## Contributing and license

See [CONTRIBUTING.md](CONTRIBUTING.md) for checks and issue guidance. Bosun is available under the [MIT License](LICENSE). Provider products and dependencies retain their own terms.
