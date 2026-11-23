# Bosun

Bosun coordinates coding work through a durable spec, scoped implementation tasks, and verification in a fresh session. It is for developers who want their coding agents to keep track of the requirements and check the result before calling a task done.

Bosun is a Claude Code plugin that runs on Opus 5.5 in every role: the lead briefs, implements and keeps the spec, and the scout and verifiers run on Opus 5.5 too. The `fable` and `fable-opus` modes were removed in 0.24.0, and the Codex plugin with the `fable-crew`, `astra-crew` and `astra` modes in 0.18.0.

## Start here

1. Install the plugin below.
2. In a new project, invoke `/bosun-brief <your task>`. Bosun creates a spec and stops for your review.
3. Review the spec, then run `/bosun-mode opus` once to write the project's local scout and verifier agents. Run the session on Opus 5.5 (`claude --model claude-opus-5-5`). Say go to start the slice.
4. Review the result and verification evidence. A failed or unavailable check is not proof of completion.

For example, ask Bosun to add a CSV export to an existing report, preserving its current filters. The spec defines the expected columns and behavior; the lead implements the scoped change; a separate verifier checks it against those requirements. This is an illustrative workflow, not a benchmark result.

You need Claude Code installed, authenticated access to the configured models, and Git. Browser checks additionally use Node.js/npx and Playwright; native-screen checks require macOS with Xcode and an iOS simulator. Model availability depends on your host and account. Bosun does not bundle models or bypass usage limits. Start in a disposable project before using continuous runs on important work.

## Install

```bash
claude plugin marketplace add mckissinger/bosun
claude plugin install bosun@bosun
```

The plugin's core rules load automatically at session start through a hook. To make them part of your global instructions instead (one less thing printed each session), append `rules/core.md` to `~/.claude/CLAUDE.md`; the hook detects its heading, `# Bosun core rules (Claude Code)`, and stops printing them. Before 0.9.0 the file was `rules/fable.md` with the heading `# Fable 5.1 agentic development`; if you appended that, remove it and append the new file.

Optional, per the effort doc's "set effort explicitly": add to `~/.claude/settings.json`

```json
{ "modelSettings": { "claude-opus-5-5": { "effortLevel": "high" } } }
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
| `/bosun-mode` | `skills/bosun-mode/SKILL.md` | Writes the project-local scout and verifier agents, sets or reports the verifier effort, and fixes a spec that names a removed mode |
| Claude agent setup | `scripts/configure-claude-agents.py` | Generates project-local scout and verifier definitions on Opus 5.5; applies verifier effort without changing the lead's effort |
| `bosun-scout` agent | `agents/bosun-scout.md` | Read-only background investigator, medium effort |
| `bosun-verifier` agent | `agents/bosun-verifier.md` | Read-only Opus 5.5 verifier, selectable effort (default high), with Playwright for done-conditions that name a route or screen |
| `bosun-verifier-mobile` agent | `agents/bosun-verifier-mobile.md` | Read-only Opus 5.5 verifier, selectable effort (default high), with a simulator MCP server for done-conditions that name a native iOS screen |
| SessionStart hook | `scripts/session-start.sh` | Loads the rules if needed, points at the spec with its provider mode line (when present) and run policy, prints any checkpoint; on compaction, tells the model to re-read the spec |

Checkpoints are written to `~/.claude/bosun/checkpoints/<project-slug>.md`.

## The spec

`SPEC.md` at the repo root, or wherever the repo's docs convention puts it. It is the only input a fresh session needs. The harness fixes what it must contain, not how it is laid out:

- the outcome
- decisions, in the user's own words
- done-conditions with a status, each checkable by the verifier's tools (git diff, file reads, the repo's checks, and a browser for a done-condition that names a route or screen) or marked human-check
- undecided items, as questions
- out-of-scope items
- the current slice
- follow-ups: things noticed and not done, one line each with the slice, the date, and a tag (`bug`, `drift`, `nit`, `deferral`; new nits are no longer written down, so `nit` marks only older ones); the exhausted-roadmap report draws its proposals from here, and `/bosun-triage` clears the ones it shows resolved once you approve (or itself, at a milestone end under `Decisions: take recommendations`)
- lessons: what a fresh session needs to know about this codebase that the repo does not already record

The model chooses the layout per project, keeps it reviewable by a person in one sitting, and reorganizes or splits it when it stops being that. Status is updated as work lands, so a crash mid-run loses little. The test of the spec: with the checkpoint deleted, can a fresh session continue from spec, branch, and git log? If not, the spec is incomplete.

## Daily use

1. Launch at the effort the work needs: `claude --effort high` for most slices, `xhigh` for long runs, migrations, hard bugs. Effort is held for the session; the model cannot change it.
2. New project: `/bosun-brief <task>` with your structures pasted or pointed at. Review the spec it writes, fill in what you can, say go. That is the one planned stop.
3. Existing spec: `/bosun-brief` (optionally naming the slice). It runs to completion, verifies, and reports. With `Run policy: until blocked, max N slices` in the spec it keeps going, one branch and one PR per slice, until something stops it; see "Run policy".
4. Read the report: done-conditions with evidence, follow-ups, anything left out. Human-check conditions are yours.
5. Stopping mid-slice: `/bosun-checkpoint`. The next session in that directory loads it.

## CI improvement

Use `/bosun-ci audit CI` for a read-only review of GitHub Actions workflows and recent runs. It starts with a conformance check (`scripts/ci-conformance.py`) that reads any project's workflows, test-runner retry settings and branch protection, whatever its stack, and reports FAIL, WARN or INFO against the skill's standard. It fails on up-to-date branches required without a merge queue, required checks that never report on PRs or in the queue, retries above one, and a push-run skip missing its guards; it warns on no queue, jobs off Blacksmith, no change-based selection, no flake hunt, no PR-run cancellation and no CI budget. Its selection, skip and hunt detections read workflow text, so those warnings are confirmed before acting. Every CI improvement slice ends with no FAIL (retries held above one until the flake hunt clears them excepted) and each remaining WARN fixed or justified in the spec. The report ranks bottlenecks by evidence, expected benefit, effort, and coverage risk. Besides queue, setup and run time per job, it measures CI runs and pushes per merged PR, the share of runs that only followed an update from the default branch, the wait from a PR's last green check to its merge, cache health (usage against the repository's limit, hit rates, whether the default branch saves what PRs restore), push runs that repeat a commit the merge queue already passed, and which test suites the nightly flake hunt leaves out; it also flags change-based selection that has never been shown to go red on a real change. Run history requires authenticated GitHub tooling or exported data; without it, the skill can produce a static audit with unmeasured hypotheses.

Use `/bosun-ci speed up CI` to investigate and implement a focused improvement through the existing brief and independent verification workflow. It compares elapsed time, total runner minutes, and reliability, preserving required checks and explaining every removed or conditional check. Warm/cold caches and differences between runs are reported; local validation alone never establishes a hosted speedup. Findings and evidence go in the existing spec.

V1 supports GitHub Actions. Blacksmith runners are the standard: the skill recommends moving GitHub-hosted jobs to them and makes the move only when asked. Deployment changes and repository protection changes need their own scope. On request, it also holds the steps for turning on a merge queue, a time-limited flake quarantine with a nightly hunt, a path gate for end-to-end tests, and an opt-in migrations flow with production behind approval or automatic. A daily flake-fix loop, also on request, takes the worst flakes from the nightly hunt, fixes each in its own verified slice (a longer timeout, more retries or a weaker assertion does not count), and quarantines the ones whose cause it cannot find; a weekly report-only routine tracks CI time against the spec's `CI budget:` line. End-to-end retries in CI stay at most one, so a test that passes only on a retry is reported as a flake, and an audit flags a higher setting. Audits time runs from job timestamps on the last attempt and read rulesets as well as classic branch protection. This skill is an engineering extension to Bosun; its CI-specific guidance references GitHub's official documentation.

## Production preflight

Use `/bosun-preflight` when an app is feature-complete and before it launches. The audit reads the whole app and reports a ranked punch list (blockers, should-fix, later) across security, abuse and cost guardrails, reliability, legal and data, product polish, operations, and native mobile. Every finding cites a file, a command's output, or a browser observation, and what could not be checked is listed separately. When the project has a spec, the audit records its verdict there in a "Production preflight" section. Ask it to fix chosen findings, or "fix the blockers", and each fix runs as a slice with a done-condition that proves it, such as a test of the denied case. It does not deploy or change hosted settings; those go to you as manual steps.

## Spec triage

Follow-ups pile up, statuses drift, and deferrals get lost as slices land. Use `/bosun-triage`, between slices, to review the spec against the code and git history. The report proposes removing follow-ups that are resolved, obsolete, or duplicated (each with its evidence), corrects statuses, tags the follow-ups that remain (`bug`, `drift`, `nit`, `deferral`), groups them into draft slices, finds decisions that never became done-conditions, and lists the human-checks and deferrals waiting on you. It also lists leftover worktrees and local branches, and marks as removable each one, never the default branch, whose PR merged into the default branch has its tip as head commit, with no uncommitted or untracked files, no ignored files beyond dependency and build output, and no process running inside it; worktrees the Claude desktop app made are left to the app, and remote branches are never touched. Nothing changes until you approve (apart from refreshing remote-tracking refs and dropping records of worktrees whose directory is already gone), except at a milestone end under `Decisions: take recommendations`, where the lead applies the evidence-backed removals and status corrections, promotes open bugs to a hygiene slice, and removes the removable worktrees and branches itself. Approved changes land as spec bookkeeping only; a reorder that puts live content ahead of finished work is a pure move, checked line by line, and nothing is condensed or reworded.

## Model

Bosun runs on Opus 5.5 (`claude-opus-5-5`) in every role. The lead briefs, implements directly, keeps the spec, and commits; the local scout and the fresh web and mobile verifiers also use Opus 5.5. Run the session on Opus 5.5 (`claude --model claude-opus-5-5` or `/model claude-opus-5-5`): a spec line cannot change the session's model, so confirm it before starting a slice. There is no model fallback.

A spec may carry `Provider mode: opus`, the only value; no line means the same. `fable` and `fable-opus` were removed in 0.24.0, and `codex`, `fable-crew`, `astra-crew` and `astra` in 0.18.0. A spec that names one makes `/bosun-brief` and `/bosun-verify` stop and say to change the line to `Provider mode: opus` or delete it; `/bosun-mode opus` makes that change.

**Verifier effort.** Set a project default, or override it for one verification:

```text
/bosun-mode --verifier-effort xhigh
/bosun-verify --effort max
```

The last command overrides effort for that verification and its retries only. Supported values are `low`, `medium`, `high`, `xhigh`, `max`; default is `high`. Resolution is invocation override, current-slice `Verifier effort:`, top-level `Verifier effort:`, then `high`. `/bosun-mode --verifier-effort <level>` changes the top-level default, preserving a current-slice override if present. Effort is recorded per attempt, independently of the lead session's effort.

`/bosun-mode opus` (or with `--verifier-effort`) and every verification run `scripts/configure-claude-agents.py` to write the effective settings into `.claude/agents/bosun-scout.md`, `bosun-verifier.md`, and `bosun-verifier-mobile.md`. These project-local copies take precedence over plugin definitions and retain their MCP servers. The next verification regenerates the copies from the current setting, so a one-run override cannot become the default. The generator refuses to overwrite unrelated user-owned files or symlinks. Keep the spec as the settings source. The generator also writes `.claude/agents/.gitignore` so git ignores the generated copies, and names any that a project still tracks with the `git rm --cached` command to stop; it leaves a `.gitignore` there that it did not write unchanged. Plugin installation alone does not generate these files.

Restart Claude Code if setup creates the project's first `.claude/agents/` directory, then confirm the local agents are loaded. Invoke those local names, not plugin-scoped `bosun:...` agents. Claude Code ignores MCP configuration on plugin-bundled agents; project-local definitions are used so the verifiers actually receive their browser and simulator tools. Existing generated files are refreshed by setup, including after a plugin update. A conflicting model environment override must be resolved before claiming a pinned model ran. See [Claude Code's subagent configuration](https://code.claude.com/docs/en/sub-agents) and [Opus 5.5 release and model identifier](https://www.anthropic.com/claude-opus-5-5).

## Runtime verification

A done-condition may name a route or screen ("`/settings` shows the new toggle") and still count as checkable, because both the implementer and the verifier have a browser.

The implementer runs the app and looks before marking such a done-condition done, and records one evidence line per done-condition: the route, what was checked, and a screenshot path if one was taken. The lead uses the desktop browser pane or Playwright MCP; a lane, or any session no one is watching, uses headless Playwright only and never a tool that waits on an approval prompt, and when the stack or app will not start it records the done-condition as blocked rather than checking a weaker stand-in. Screenshots are evidence when appearance matters; the accessibility snapshot is the cheaper check for text and structure. Nobody walks the whole app.

The verifier gets Playwright too (an inline `mcpServers` entry on `bosun-verifier`). It uses the browser only to re-check the route-or-screen done-conditions, following the implementer's evidence lines, may start the app with the launch command the brief names, stops it afterward, and reports screenshot paths as evidence. Each slice-log line records how many done-conditions named a route or screen and how many the verifier confirmed, so runtime verification can be compared across projects.

For native iOS screens, the brief says `Surface: ios` and the evidence line records the screen, device, what was checked, and screenshot path. `bosun-verifier-mobile` uses the mobile simulator MCP server. The lead or verifier may boot the named device with `xcrun simctl boot` and must shut down any simulator it booted with `xcrun simctl shutdown`. Native-screen checks require macOS with Xcode and an iOS simulator.

Requires `npx` able to fetch or find `@playwright/mcp` and a Chromium; the first run downloads them.

## Run policy

A Claude Code session is turn-based: when the model ends its turn, nothing happens until something wakes it. The default harness ends the turn after every slice, so the user waits between slices. The run policy removes most of that idle time without changing what gets built.

The policy is a line near the top of the spec: `Run policy: one slice` (the default; no line means the same) or `Run policy: until blocked, max N slices` (`until blocked` alone means `max 10 slices`). Under `until blocked`, after a slice verifies, the lead commits, pushes, opens a PR for that slice's branch, arms auto-merge (`gh pr merge <n> --auto --merge`), reports, and briefs the next slice in the same turn, without idling on CI and without asking whether to go on (see "Merge flow" for which slices it builds while CI runs, and when it waits). Every slice keeps its own branch and PR. Auto-merge lands it once the required checks pass; if GitHub refuses auto-merge because every required check is already green, the lead merges it with `gh pr merge <n> --merge`. It never merges past a red or missing required check or bypasses branch protection, and it leaves the PR open and says so when the repo has no required checks, disallows auto-merge, or the spec or your instructions keep merging for you. The run stops, and the report says why, at the first of: no runnable done-condition left; every remaining runnable item needs a decision the lead may not make (see "Decisions"); two FAILs on one verify finding (three under `Decisions: take recommendations`); a slice whose third verify run FAILs; every remaining slice waiting on a PR that cannot merge on its own; an environment failure that blocks all remaining work; the slice cap. A done-condition is runnable when it is `todo` or `in progress`, not `human-check`, and needs nothing on the undecided list.

**Merge flow.** While a PR's checks run, the lead builds ahead only on slices that need nothing from an unmerged slice, each in its own worktree cut from the latest default branch; a dependent slice is briefed then and built after its base merges, and branches are never stacked on unmerged ones. When only dependent work is left, the lead waits for the base PR, but only if it merges on its own; otherwise the run stops and names it. Every slice writes the spec, so each built-ahead slice adds its brief as its own subsection and appends to the log, and a spec conflict between two PRs is resolved by keeping both sides. Before each slice, after each verify, and while waiting, the lead checks its open PRs and the latest run of every workflow on the default branch: a red or conflicting PR pauses the current slice while the lead fixes it on that PR's branch (verifying a code fix), then it resumes, and a red default branch is fixed first, except that an environment failure is rerun once and reported, and a flake candidate or a red run of a workflow that only reports (such as the nightly flake hunt) is reported instead. The recommended setup is a GitHub merge queue (available on organization-owned public repositories and on GitHub Enterprise Cloud) with required checks also triggered on `merge_group`, and a `merge_group` fallback for any job that reads a PR number. Without a queue, turn off "require branches to be up to date" and run CI on every push to the default branch: PRs then merge as soon as their own checks pass, and a red run on the default branch is fixed like a red PR. If a repo keeps the up-to-date requirement without a queue, the lead updates the oldest behind PR, one at a time, and `/bosun-ci` reports the setting.

**Exhausted roadmap.** When no runnable done-condition remains, under either policy, the lead does not invent work. It reports that the roadmap is exhausted, lists the open human-checks and the undecided questions, proposes next slices drawn from the spec's follow-ups section as clearly marked drafts, and asks what next. A proposal becomes a done-condition only when you say so; under `Decisions: take recommendations`, the lead first decides the undecided items it may decide, and a hygiene slice built from open bug follow-ups counts as runnable work.

**Milestones.** Every follow-up gets a home when it is written: bugs in the slice's own work are fixed in that slice, other bugs by the next slice that touches the file or a hygiene slice before the milestone closes, nits the verifier finds in the slice's own diff are fixed or dropped rather than written down, deferrals name their target, and anything that needs you goes to human-checks. A milestone is a group of done-conditions the spec names, or every fifth slice. At each milestone end under `until blocked`, the lead runs `/bosun-triage` (which also finds worktrees and local branches whose work is merged and that are clean and idle, and removes them when the triage is applied), a hygiene slice for the open bugs, and a `/bosun-ci` audit. More than five open bugs makes the next slice a hygiene slice. Triage also keeps the spec's "Recurring verify failures" lesson (at most ten kinds of defect verification has caught in two or more slices), which the implementer checks the diff against before every verify, and it moves finished slice briefs and old slice-log entries, verbatim, to an archive file when they push the spec past one sitting.

**Records ride along.** Every PR pays a full CI cycle, so during a run a change that touches only records (the spec, docs, design boards: a decision, an approval, a polished board) gets no PR of its own. It goes on the branch of the slice in flight or the next one, and only when no slice follows do the run's records get one PR at the end. With lanes, the hub sends decisions to the lane that needs them and opens one records PR per milestone end and at the run's end.

## Decisions

`Decisions: take recommendations` in the spec (no line means `ask`) lets the lead act on its own recommendations instead of stopping: it decides open questions that come up mid-run, undecided items the spec's outcome or decisions point to, and a two-FAIL disagreement on one verify finding, records each in the spec's decisions as "(build mode, <date>)" with a line of why, and keeps going. A third FAIL on the same finding still stops the run. It never decides credentials, accounts, or sign-ins; prices, fees, or live spend; production data or anything sent to real people; legal, naming, or trademark questions; new-design approval, or approval of a departure that changes an approved design, under `Design approval: me`; or anything the spec lists as yours. Work that needs one of those is parked as a human-check or an undecided question with the lead's recommendation, and the run takes other work.

## Design

Every slice that adds or changes a screen runs one loop: load the design skill the project names and its locked design rules, read each screen's approved board and the design system and take values from the design tool rather than from images, mock up any screen without a board first (in the design tool the project names, or a design canvas when it names none, with a copy in the repo), get the mockup approved, build every state and motion the board shows, record any departure from the board (one forced by the platform or data that leaves what the user sees or does unchanged is approved by its record; one that changes the design needs your approval, or a fresh agent's under `critique`, before the first verify), check it at 390, 768, 1024, 1280, and 1440 wide (or the project's widths) in its empty, loading, error, hover, and focus states and its motion, and have a fresh agent compare the screenshots with board images exported in that slice; any difference that is not an approved departure blocks the done-condition, and the verifier checks the same images and the locked rules. The brief's `Design:` line carries the skill, the rules file, each screen's board and its approved departures, so a builder working on the tenth screen sees them as clearly as on the first. `Design approval: me` (the default for a project with UI) means you approve each mockup, and a new direction or interaction pattern always waits for you; `Design approval: critique` means a fresh agent critiques the mockup and the board is revised with an "After critique" note. A new direction starts from several fresh options, not variations on an older mockup.

## Other sessions

You can run more than one session on a project, but Bosun does not coordinate them. The core rules keep them from damaging each other: every session that writes code uses its own worktree and branch, never applies an unapproved or unmerged migration to a database another session uses, never resets or stops another session's stack or server, and never stops processes by name.

## Why each piece exists

Bosun's rules were first built from Anthropic's Fable 5.1 guidance, cited below, and now run on Opus 5.5. Where Anthropic's [Opus 5.5 prompting guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5) differs, this section says so.

Sources: [Overview](https://platform.claude.com/docs/en/models/fable-5-1/overview), [What's new](https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1), [Migration guide](https://platform.claude.com/docs/en/models/fable-5-1/migration-guide), [Prompting Claude Fable 5.1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1), [Effort](https://platform.claude.com/docs/en/build-with-claude/effort), [Refusals and fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback), [Claude Code effort controls](https://code.claude.com/docs/en/model-config).

**Effort is the primary control.** Bosun's default is `high`. The Fable 5.1 guide says start at `high`, step down to `medium` or `low` where quality holds, and step up to `xhigh` or `max` only where measured. The Opus 5.5 guide defaults to `medium` and reports it matching Opus 5 at `high` on agentic coding in fewer steps and tokens; Bosun keeps `high` until a project measures a lower level on its own slices. At `xhigh` and `max` it may draft a long deliverable in thinking and again in the reply. Claude cannot change effort inside a session, and the effort doc says to hold it constant within a conversation, so effort is chosen at launch and the brief states the level it assumes.

**Sizing.** The guide says Fable 5.1 "can execute very long tasks without much guidance on methodology, especially when the goal is clear," and pairs `xhigh` with runs over thirty minutes. The harness sizes work as outcomes with done-conditions, not step lists, and drains ambiguity once, in the spec, at the one planned stop.

**Finish the whole task.** The guide's autonomous-operation and "Delivering work" blocks are already injected by Claude Code on Fable 5.1, along with the progress-update line and the per-turn batching nudge, so the harness does not repeat them.

**Scope and tests.** The guide's block on keeping changes and tests to what the task asks for is in the core rules verbatim; the guide reports it cuts unrequested additions with no measurable change in task success.

**Targeted edits.** Fable 5.1 rewrites whole files more than Fable 5 did. The guide's one-sentence fix is in the core rules verbatim.

**Delegation.** The guide says letting the lead keep working while subagents run lowers time to completion at similar quality and cost. `bosun-scout` runs in the background; the core rules tell the lead to keep working.

**Safeguard false positives.** The guide names three triggers: compile-check phrasing, lesser-known languages without context, base64 in tool output. The core rules carry the phrasing and a recovery step: rephrase once, then record the blocked step in the spec and move on.

**Verification.** `/bosun-verify` runs a fresh-context, read-only verifier at the selected effort (default `high`, the documented starting point), so the judgment is independent of the session that did the work. Two FAILs on the same finding stop the loop and go to the user, unless `Decisions: take recommendations` lets the lead decide it; a third FAIL stops it either way. A slice gets at most three verify runs in all, whether or not the findings repeat. A FAIL needs an unmet done-condition, a failing check, or a release-blocking defect shown to be reachable through input the app actually accepts; other reachable defects are follow-ups, and nits stay out of the follow-ups. A check the verifier could not run, for example on a loaded machine, leaves its done-conditions not verified rather than passed.

**Runtime verification.** This is the one rule that does not come from the Fable 5.1 model guide, which says nothing about browsers. It comes from Anthropic's guidance for running Fable in Claude Code: the [Claude Code best practices](https://code.claude.com/docs/en/best-practices) ("Give Claude a check it can run: tests, a build, a screenshot to compare"; "Always provide verification (tests, scripts, screenshots). If you can't verify it, don't ship it"; verification by a second-opinion subagent; show evidence, including screenshots, rather than asserting success), and Anthropic's [long-running agents article](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (the coding agent "needed explicit prompting to use browser automation tools and do all testing as a human would", and a browser "dramatically improved performance"). The model guide says finish the task and keep tests to what the change warrants; the product guidance says a check for visible behavior is a browser. Both roles get one because the implementer's check is the loop that makes the work correct and the verifier's is the independent gate; self-review measurably favors its own output, so the overlap is the point, and it stays cheap because the verifier re-checks named done-conditions only.

**Lessons.** The prompting guide says Fable 5.1 performs notably better when it can write learnings somewhere for future reference, even a plain markdown file, and gives the format: one lesson per entry with a one-line summary, corrections and confirmed approaches alike with why they mattered, update rather than duplicate, delete what turns out wrong, and skip what the repo or history already records. The harness keeps them as a section of the spec, because every point where the harness already forces a spec read (session start, compaction, the brief) then covers them for free. The section splits into its own file only when it stops being readable in one sitting, by the same rule as the rest of the spec. A correction that a check could catch becomes that check instead: when you correct an agent's work, the fixing slice adds a lint rule, hook, test or CI check as a done-condition, and `/bosun-triage` proposes one for each new "Recurring verify failures" line, so only what no check can express is left as text.

**Continuity.** The guide's compaction instruction lists six things a summary must preserve. Claude Code does not expose custom compaction instructions, so the harness keeps expectations in the spec, fires a "re-read the spec" reminder from the SessionStart hook when compaction happens, and uses the checkpoint only for transient mid-slice state.

## Lanes

Under `Run policy: until blocked`, a long run can use lanes: separate Claude Code sessions that the lead (the hub) starts, each in its own worktree, each running its own Bosun loop on one area of the spec with its own slice cap. Once lanes start, the hub stops building. It becomes the session you plan and decide in: it keeps the spec, reviews screens with you, runs milestone triage and the CI audit, watches the default branch, and hands every code change to a lane, including shared-file changes, red-branch fixes, hygiene slices and CI-audit fixes.

The hub picks one of three shapes per run: one session as before when the run is short (fewer than five slices) or you won't be steering it; the hub plus two lanes when there are two independent areas of at least three slices each; otherwise the hub plus one lane, which takes all the work. At most three sessions run. It proposes the shape in its first slice report and at each milestone end, and starts lanes only after you say yes, once per run; until then it works as one session. Lanes need isolated tests: when migrations or end-to-end runs share a local stack, the first step after your yes is a setup slice that gives each lane its own stack and ports through a command the spec names on a `Stack isolation:` line. Each lane slice branches from the latest default branch and gets its own PR, so nothing stacks; spec conflicts are resolved by keeping both sides. Lanes run under the spec's `Decisions:` setting and send anything that needs you to the hub, which batches it, so you hear from one session. With nothing to plan, the hub pauses until a lane or you wake it. The hub starts lanes itself where the host can start sessions (the Claude Code desktop app); elsewhere it prints the lane prompts for you to start by hand. The procedure is in `/bosun-brief` ("Lanes") and the rules in the core rules ("Lanes"). A lane never ends its turn saying it is waiting on CI unless something will wake it when its PR merges, fails, conflicts or sits green and unqueued, and lanes and unwatched sessions check screens with headless Playwright only, never with a tool that waits on an approval prompt, recording a check as blocked when the stack or app will not start. When two areas need the same new page or component, the hub names the one slice that builds it. The hub judges lanes by commits and PR state rather than a "running" flag. A lane reports once each of its PRs has merged or closed, or cannot merge on its own, and once its PRs have merged or closed the hub archives the lane's session and confirms its stack is gone. Lane stacks start only the services tests need and are removed when the lane ends. Every session checks how loaded the machine is before heavy work, stops what it no longer needs, and retries an environment failure once before reporting it with the machine's state. `/bosun-triage` reports leftover stacks and servers, and stops none of them.

## Not covered on purpose

- Parallel builder agents inside one slice. Parallel sessions on one project are covered by "Lanes"; inside a slice, the docs credit the model's gains to long single-context runs.
- API-side migration concerns (beta headers, append-only message arrays, `tool_choice`, `input_transformations`, fallback middleware). Claude Code manages the conversation prefix itself. If you call the Messages API directly, read the migration guide's "Preserved thinking" section first.

## Status

Version 0.30.0. The [spec](SPEC.md) records implemented slices, verification evidence, and outstanding human checks. Static validation and browser smoke checks are recorded there, along with verified development slices. Full end-to-end checks of host hook behavior remain partially unverified. Do not interpret the version number as a guarantee that every host/model combination has been exercised.

There is no controlled performance benchmark establishing cost, speed, or quality improvements. Those depend on the project, model access and verification workload.

## Safety and local data

Bosun delegates through your installed tools and their permissions. The lead can edit project files. Review the rules and SessionStart hooks before enabling them.

Specs and checkpoints can contain project information. Review them before sharing or committing them. Do not include credentials or customer records in a public example or issue. Continuous runs can commit, push, open pull requests, and arm auto-merge on them under the documented run policy; start with one slice.

## Contributing and license

See [CONTRIBUTING.md](CONTRIBUTING.md) for checks and issue guidance. Bosun is available under the [MIT License](LICENSE). Provider products and dependencies retain their own terms.
