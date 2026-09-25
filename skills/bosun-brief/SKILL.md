---
name: bosun-brief
description: Start substantial coding work on Claude Fable 5.1 or Opus 5.5. On a project with no spec, it creates SPEC.md from the request and whatever structures the user supplies, then stops for review. On a project with a spec, it briefs the next slice (outcome, checkable done-conditions, out-of-scope, assumptions, checks, branch), runs it to completion, verifies, and updates the spec. Use at the start of any task beyond a few tool calls (features, multi-file changes, refactors, migrations, debugging), or when the user says "brief this", "start the project", "next slice", or "run this end to end".
argument-hint: "<task, or a paste / path of the structures you already have>"
---

# Bosun brief

The lead runs long tasks well when the goal is clear and stops to ask when it is not. This skill makes the goal clear once, in the spec, so runs need no mid-task input.

## Find the spec

Look for `SPEC.md` at the repo root, then under the repo's docs convention. If none exists, follow "No spec yet". Otherwise follow "Spec exists".

## Find the provider mode

A line `Provider mode: <mode>` anywhere in the spec names one of six modes (table in the core rules). `fable` (also no line) is fable mode. `fable-crew` (or the old value `codex`) is fable-crew mode: steps 3 and 6 of "Spec exists" change as described in "Fable-crew mode" at the end of this skill; everything else is the same. `fable-opus` uses a native Opus 5.5 worker as described in "Fable-opus mode" below. `astra-crew` and `astra` run in Codex, not here: report that the spec is in an Astra mode, name the mode, say to open the project in Codex with the harness's Codex plugin, and stop without briefing or running anything.

## Opus lead and session model

`opus` runs in Claude Code with Opus 5.5 in every role. Apply the ordinary fable-mode flow with Opus as the lead: brief, implement directly, keep the spec, commit, and fix FAIL findings yourself. Do not use the fable-opus worker flow or stage concurrent implementation. Use the project-local `bosun-scout` and both verifier variants configured on Opus by `/bosun-mode opus`; verification remains a fresh read-only context.

Before briefing or running any Claude mode, confirm the actual session model: `claude-opus-5-5` for `opus`, Fable 5.1 for the three Fable modes. A spec line does not switch the session model. If mismatched, select the required model with `/model` or relaunch with `claude --model <model>` and confirm before continuing. Configure local agents with `/bosun-mode <mode>` when absent or stale after switching modes; confirm the local scout and verifier model settings are loaded (restart Claude Code when needed). Never silently fall back to plugin-scoped or differently modeled agents. Unknown provider modes are errors.

## Find the run policy

A line `Run policy: until blocked` or `Run policy: until blocked, max N slices` anywhere in the spec makes this a continuous run: after each slice verifies, the next one starts in the same turn, as described in "Until blocked" below. Anything else (including no line) is `one slice`: brief, run, verify, report, stop. `until blocked` without a `max` means `max 3 slices`.

## No spec yet: create it and stop

1. Gather. Read the request and everything the user supplied: pasted structures, document paths, existing code. Batch the reads. If the directory has no git repository, initialize one. If the repo has a docs convention, the spec goes there; otherwise `SPEC.md` at the root. Say which path you chose.
2. Write the spec. It must contain, findably: the outcome; the user's decisions in their own words; every done-condition you can state so that a read-only verifier could check it with git diff, file reads, and the repo's checks (anything only a person can confirm is marked human-check); an undecided list holding everything you could not settle, stated as questions, not guesses; an out-of-scope list; an empty current-slice section; an empty follow-ups section; and an empty lessons section. If the user asked for a mode other than fable, add a `Provider mode: <fable-crew|fable-opus|opus|astra-crew|astra>` line under the first heading (see the core rules); otherwise leave the line out. If the user asked for continuous runs, add `Run policy: until blocked, max N slices` next to it; otherwise leave that line out too. Choose the layout for this project. Keep it reviewable in one sitting.
3. Stop. End the turn asking the user to review the spec, answer or edit the undecided items they can, and say go. Do not build yet. This is the one planned stop in the workflow.

## Spec exists: brief a slice and run

1. Read the spec, including its lessons. If no runnable done-condition remains (status `todo` or `in progress`, not `human-check`, nothing it needs on the undecided list), follow "Exhausted roadmap" below and stop. Otherwise take the done-conditions the user named, or the next unstarted ones that form a coherent slice. Undecided items are out of scope for this slice. If a staged brief exists for this slice (see "Staged briefs"), re-validate it as described there instead of writing a new one.
2. Gather what the slice depends on: the files involved, the test setup, the exact check commands and any setup they need, and the branch state. Batch the reads. Hand side questions to `bosun-scout` in the background and keep working.
3. Write the slice brief into the spec's current-slice section and in your reply:

```
Outcome: <one sentence>
Done-conditions: <numbered; each checkable by the verifier's tools, or marked human-check>
Surface: ios  (include only when a done-condition names a native screen)
Out of scope: <what a careful engineer might touch but must not>
Assumptions: <each ambiguity and the reading chosen, with why>
Effort assumed: <the session's level; you cannot change it>
Verifier effort: <current-slice override, project default, or high; independent of lead/worker>
Checks: <exact commands and any setup they need>
Branch: <name>
```

   For a small task, one line each for outcome, done-condition, and check is the whole brief. In fable-crew or fable-opus mode, add the lines from the matching section below. Resolve verifier effort as `/bosun-verify` specifies; the brief records the effective value and its source. Do not carry a previous slice's override into a new slice.

4. Branch. Start from the default branch. If the previous slice's branch is unmerged, stack on it and record that in the spec. Never work on the default branch.
5. Decide whether to stop. End the turn only if a decision that only the user can make blocks the slice and any assumption would make the work useless or unsafe. Otherwise state the assumptions and continue in the same turn.
6. Execute. Work through the done-conditions and update each one's status in the spec as it lands. Follow the scope and edit rules in the global CLAUDE.md. If a done-condition names a route or web screen, run the app and check it with the browser tool this session has (the desktop browser pane, or Playwright MCP) before marking it done; a route-or-screen done-condition may name a viewport width, and its evidence line must then carry the viewport so the verifier can re-check it in Playwright at that width. Record the route, the viewport when named, what was checked, and a screenshot path if one was taken. If a done-condition names a native screen, set `Surface: ios`, check it before marking it done with the simulator tool this session has or with `xcrun simctl` from the shell when it has none, and record the evidence line as: screen, device, what was checked, screenshot path. Do not end the turn to announce a next step; do the step. In fable-crew or fable-opus mode, replace this step with the matching section below.
7. Verify. Run `/bosun-verify` and act on its verdict. After two FAILs on the same finding, stop and report both positions.
8. Record lessons. Before reporting, add to the spec's lessons section anything this slice taught that a fresh session would need and the repo does not record, following the lessons rules in the core rules. Correct or delete entries this slice proved wrong. Often there is nothing to add.
9. Report. Outcome first, then each done-condition with its evidence, then an `Evidence:` list of the route-or-screen checks (route or screen, viewport or device when applicable, what was checked, screenshot path), then follow-ups you noticed but did not do, then anything left out and why. Append a line to the spec's slice log: date, slice name, mode, first-verify verdict, and how many done-conditions named a route or screen against how many the verifier confirmed in its browser or simulator. Append each follow-up to the spec's follow-ups section, one line with the slice name and date. If undecided items remain, you may add draft done-conditions for the next one to the spec, clearly marked as drafts for the user. If you are stopping mid-slice, run `/bosun-checkpoint`. Under `until blocked`, do not end the turn here; continue with "Until blocked".

## Until blocked

Under `Run policy: until blocked`, after step 9 of a slice that verified PASS or PASS WITH FOLLOW-UPS: commit, push the branch, open a PR for it with `gh pr create` (summary, verification, follow-ups; never merge), then go back to step 1 for the next slice in the same turn. Each slice gets its own branch, stacked on the previous one while that is unmerged (step 4), and its own PR. Keep a count of slices started in this run, including the first.

Stop, and say in the report which condition stopped the run, at the first of:

- no runnable done-condition remains ("Exhausted roadmap");
- the next runnable done-condition depends on an undecided item;
- a verify produced two FAILs on the same finding (step 7);
- the codex preflight failed (fable-crew mode);
- the count has reached `max N`.

## Exhausted roadmap

When no runnable done-condition remains, at the start or between slices, under either policy, do not invent work. Report, in this order: that the roadmap is exhausted; every open human-check condition; every undecided item, as the question the spec records; and candidate next slices drawn from the spec's follow-ups section, each written as a draft done-condition and marked as a proposal. End the turn asking what next. Never promote a proposal into a done-condition yourself; the user says which, if any, become work.

## Staged briefs

Staging (fable-crew or fable-opus mode, `until blocked`, count below `max N`): while the worker runs, identify the next slice from the spec. If none of its done-conditions depend on what the running slice creates or changes (files it adds or rewrites, interfaces it defines, behavior that must land first), scout that slice's dependencies, reading only, and write a staged brief in the step 3 template to `~/.claude/bosun/workers/<slug>/<next-slice>/brief.md`, with a first line `Based on: <sha>` naming the worktree's HEAD at staging time. If the next slice does depend on the running one, scout only and write what you learned to `notes.md` in that directory. Either way, never write to the worktree while the worker runs, and do not put the staged brief into the spec's current-slice section yet. Only the brief is staged; the worker prompt is written later from the final brief, because it must contain that brief verbatim.

Re-validating: when a staged brief's slice comes up, compare its `Based on:` sha with the worktree's HEAD. If they differ, re-read the spec and `git diff <sha>..HEAD`, check every file path, line reference, and assumption in the brief against what landed, and fold in any follow-ups from the previous slice's verify that fall inside this slice's done-conditions. Only then write the brief into the spec's current-slice section and continue from step 4; in fable-crew or fable-opus mode the worker prompt is generated from this final brief. If the previous slice's verify FAILed, the staged brief waits for the fix loop. If that loop stopped the run, leave the staged brief on disk and name its path in the report.

## Fable-crew mode

Fable briefs, keeps the spec, commits, and verifies; a Codex model implements. The routing table and the `ultra` ban are in the core rules.

Brief (step 3): add to the brief template

```
Task class: <small | routine | feature | hard, with the one-line reason>
Route: <model> / <effort>   (from the table, or the spec's own Route: override if the current-slice section has one)
Worker network: <yes | no>  (yes only if the slice needs installs or other network access)
Worker browser: <yes | no>  (yes when any done-condition names a route or screen)
Worker simulator: <yes | no>  (yes when `Surface: ios`)
```

Execute (step 6):

1. Write the worker prompt to `~/.claude/bosun/workers/<slug>/<slice>/prompt.md`, where `<slug>` is the checkpoint slug (cwd with the leading slash removed and every `/` or space replaced by `-`) and `<slice>` is a short name for this slice. The worker has no memory of this session, so the file must contain: the slice brief verbatim; the spec's decisions and out-of-scope lists; the "While working" rules from the core rules (scope, tests, targeted edits, the route-or-screen browser check with its evidence line when `Worker browser: yes`, and the native-screen simulator check with its screen, device, what-was-checked, and screenshot-path evidence line when `Worker simulator: yes`); the exact check commands, the app's launch command when the browser is needed, the device name, build and install commands, and bundle id when the simulator is needed, and any setup they need; and these instructions: do not commit, do not edit the spec, run the checks before finishing, and end with a short report naming every file changed and every check run with its result.
2. Run the worker in the background and keep working on anything that does not touch the worktree (drafting the report, reading the spec) until the exit notification arrives. Do not poll. Under `until blocked` with the count below `max N`, use this time to stage the next slice's brief as "Staged briefs" describes: `brief.md` with `Based on: <sha>` when the next slice is independent of this one, `notes.md` only when it is not.

   ```bash
   "<plugin root>/scripts/codex-worker.sh" --model <model> --effort <effort> --cwd "<worktree>" --prompt-file "<prompt.md>" --out-dir "<same dir as prompt.md>" [--network] [--browser] [--simulator]
   ```

   `<plugin root>` is the base directory this skill was loaded from, two levels up from this file. Pass `--browser` when the brief says `Worker browser: yes`; it binds the Playwright MCP server to the worker. Pass `--simulator` when the brief says `Worker simulator: yes`; it binds the mobile MCP server to the worker. The script refuses `ultra` and unknown models, preflights `codex --version` and `codex login status`, and writes `events.jsonl`, `last-message.md`, and `usage.json` into the out dir. A non-zero exit before the worker started (exit 2 or 3) is a stop: report the message; never implement the slice yourself instead.
3. When it exits, read `last-message.md`, `usage.json`, and `git diff` in the worktree. When the brief says `Surface: ios`, Fable also checks the named native screen with the simulator tool this session has, or `xcrun simctl` from the shell when it has none, before marking it done. Update each done-condition's status in the spec from what the diff, the worker's report, and that simulator check show, not from the report alone. If the worker committed anything, note it as a finding for the report and continue.
4. Verify as in step 7. On FAIL, do not fix the findings yourself: write a follow-up prompt file (the findings verbatim, the original brief, the same instructions) and run the script again with the same route. Two FAILs on the same finding stop the loop as usual.
5. Commit the worker's changes yourself, once verified, with the usual message and trailer.
6. In the report and in the spec's slice log, record: slice name, task class, route, first-verify verdict, the `usage.json` numbers (wall seconds and token counts), and how many done-conditions named a route or screen against how many the verifier confirmed in its browser or simulator.

## Fable-opus mode

Fable briefs, keeps the spec, commits, and verifies; the project-local `bosun-worker-opus` implements as a native Claude Code subagent on `claude-opus-5-5` at `high`. No Codex worker script or task-class model routing is involved. Add `Route: bosun-worker-opus / claude-opus-5-5 / high` to the brief. Reject an incompatible existing Route override rather than silently interpreting a Sol/Luna or Codex-agent route.

Before the first slice, run `/bosun-mode fable-opus` if the project-local agent definitions are absent. Confirm the worker and both verifiers are loaded; a new `.claude/agents/` directory needs a Claude Code restart. Do not continue with plugin-scoped substitutes: they ignore the MCP frontmatter. If model access or the required tools are missing, stop and report the limitation, without falling back to Fable implementation.

Execute (step 6):

1. Write a self-contained worker prompt at `~/.claude/bosun/workers/<slug>/<slice>/prompt.md` (same slug as checkpoints): the final brief verbatim, decisions and out-of-scope list, exact worktree path, the core rules' "While working" scope/test/targeted-edit rules, check commands and setup. Include the app launch command and viewport when web checks are named; for `Surface: ios`, include device, build/install commands, bundle id, and the screen evidence format. Instruct the worker not to commit, edit the spec, or delegate, to preserve others' edits, run the checks, and report changed files, results and evidence.
2. Delegate that prompt to the local `bosun-worker-opus` in the current worktree. Do not fork the lead's conversation or spawn parallel implementers. While it runs, do no worktree writes; drafting the report or staging an independent next brief as described above is allowed. A failed or incomplete worker response is not completion.
3. Read the worker's report and the worktree diff before updating spec statuses. For native screens, Fable also checks the named screen as in step 6 of "Spec exists". Record evidence and any model/tool limitations. Do not mark a condition complete from the report alone.
4. Run `/bosun-verify` on Fable at the resolved verifier effort, independent of the worker's high effort. On FAIL, send the verbatim findings, original brief, and the same constraints back to `bosun-worker-opus`; Fable does not implement the fixes. Re-verify at the same effort unless the user changes it. Two FAILs on the same finding stop the loop.
5. Once verified, Fable commits. Record route, verifier effort for each attempt, first-verify verdict, and named/confirmed route-or-screen counts in the report and slice log. Native subagents do not produce the Codex worker's `usage.json`; use host usage information if available and never invent token counts.

## Long deliverables at xhigh or max

If the session runs at `xhigh` or `max` and a step produces a long deliverable (a large file, a long document), keep this in mind before writing it, with the real limit filled in (`CLAUDE_CODE_MAX_OUTPUT_TOKENS` if set, otherwise the model's 128,000 output cap):

> Everything produced in one reply, including any reasoning or drafting it does before the reply, counts toward a single limit of about [max_tokens] tokens. If that limit is reached before the reply is finished, the person receives a cut-off response and has to start over. Composing an entire output or deliverable in full as reasoning and then again as a reply would double the length of the turn without improving the result, so don't do that. Instead, spend extra effort on understanding the request, checking the inputs the answer depends on, settling the structure and other difficult decisions, and otherwise use the reasoning space to reason and the output space to write an output.
