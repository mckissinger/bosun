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

A line `Provider mode: <mode>` anywhere in the spec names one of three modes (table in the core rules). `fable` (also no line) is fable mode. `fable-opus` uses a native Opus 5.5 worker as described in "Fable-opus mode" below. `opus` is described next. The values `codex`, `fable-crew`, `astra-crew` and `astra` were removed in 0.18.0: if the spec names one, report the value, say it was removed with the Codex plugin, say to choose `fable`, `fable-opus` or `opus` with `/bosun-mode`, and stop without briefing or running anything.

## Opus lead and session model

`opus` runs in Claude Code with Opus 5.5 in every role. Apply the ordinary fable-mode flow with Opus as the lead: brief, implement directly, keep the spec, commit, and fix FAIL findings yourself. Do not use the fable-opus worker flow or stage concurrent implementation. Use the project-local `bosun-scout` and both verifier variants configured on Opus by `/bosun-mode opus`; verification remains a fresh read-only context.

Before briefing or running, confirm the actual session model: `claude-opus-5-5` for `opus`, Fable 5.1 for `fable` and `fable-opus`. A spec line does not switch the session model. If mismatched, select the required model with `/model` or relaunch with `claude --model <model>` and confirm before continuing. Configure local agents with `/bosun-mode <mode>` when absent or stale after switching modes; confirm the local scout and verifier model settings are loaded (restart Claude Code when needed). Never silently fall back to plugin-scoped or differently modeled agents. Unknown provider modes are errors.

## Find the run policy

A line `Run policy: until blocked` or `Run policy: until blocked, max N slices` anywhere in the spec makes this a continuous run: after each slice verifies, the next one starts in the same turn, as described in "Until blocked" below. Anything else (including no line) is `one slice`: brief, run, verify, report, stop. `until blocked` without a `max` means `max 10 slices`.

## Find the decisions and design settings

A line `Decisions: take recommendations` anywhere in the spec lets the lead decide open questions itself and keep running; anything else (including no line) is `ask`. A line `Design approval: me` or `Design approval: critique` sets who approves a new screen's mockup; a project with UI and no line is `me`. The core rules' "Decisions" and "Design" sections hold what each value allows.

## No spec yet: create it and stop

1. Gather. Read the request and everything the user supplied: pasted structures, document paths, existing code. Batch the reads. If the directory has no git repository, initialize one. If the repo has a docs convention, the spec goes there; otherwise `SPEC.md` at the root. Say which path you chose.
2. Write the spec. It must contain, findably: the outcome; the user's decisions in their own words; every done-condition you can state so that a read-only verifier could check it with git diff, file reads, and the repo's checks (anything only a person can confirm is marked human-check); an undecided list holding everything you could not settle, stated as questions, not guesses; an out-of-scope list; an empty current-slice section; an empty follow-ups section; and an empty lessons section. If the user asked for a mode other than fable, add a `Provider mode: <fable-opus|opus>` line under the first heading (see the core rules); otherwise leave the line out. If the user asked for continuous runs, add `Run policy: until blocked, max N slices` next to it; otherwise leave that line out too. Choose the layout for this project. Keep it reviewable in one sitting.
3. Stop. End the turn asking the user to review the spec, answer or edit the undecided items they can, and say go. Do not build yet. This is the one planned stop in the workflow.

## Spec exists: brief a slice and run

1. Read the spec, including its lessons. Under `Decisions: take recommendations`, first decide each undecided item the core rules' "Decisions" section lets you decide (one the spec's outcome or decisions point to, and not on the never-decide list), record it as that section says, and move it out of the undecided list; then judge what is runnable. If no runnable done-condition remains (status `todo` or `in progress`, not `human-check`, nothing it needs on the undecided list), follow "Exhausted roadmap" below and stop. Otherwise take the done-conditions the user named, or the next unstarted ones that form a coherent slice. Undecided items are out of scope for this slice. If a staged brief exists for this slice (see "Staged briefs"), re-validate it as described there instead of writing a new one.
2. Gather what the slice depends on: the files involved, the test setup, the exact check commands and any setup they need, and the branch state. Batch the reads. Hand side questions to `bosun-scout` in the background and keep working.
3. Write the slice brief into the spec's current-slice section and in your reply:

```
Outcome: <one sentence>
Done-conditions: <numbered; each checkable by the verifier's tools, or marked human-check>
Surface: ios  (include only when a done-condition names a native screen)
Out of scope: <what a careful engineer might touch but must not>
Assumptions: <each ambiguity and the reading chosen, with why>
Decisions: <ask | take recommendations, and its source: the spec line, or the default>
Design approval: <me | critique, and its source: the spec line, or the default; include only when a done-condition adds or changes a screen>
Effort assumed: <the session's level; you cannot change it>
Verifier effort: <current-slice override, project default, or high; independent of lead/worker>
Checks: <exact commands and any setup they need; end-to-end checks name the targeted specs, not the full suite, and say whether a required CI check runs the full end-to-end suite>
Branch: <name>
```

   For a small task, one line each for outcome, done-condition, and check is the whole brief. In fable-opus mode, add the line from "Fable-opus mode" below. Resolve verifier effort as `/bosun-verify` specifies; the brief records the effective value and its source. Do not carry a previous slice's override into a new slice.

4. Branch. Start from the latest default branch (`git fetch` first). If this slice depends on an unmerged slice, build it only after that slice merges: under `until blocked`, take independent work meanwhile or wait, as the core rules' "Merge flow" says; under `one slice`, do not start it, and report which PR it waits for. While another slice's PR is open, work in a new worktree for this slice. Never stack on an unmerged branch, and never work on the default branch.
5. Decide whether to stop. Under `Decisions: ask`, end the turn only if a decision that only the user can make blocks the slice and any assumption would make the work useless or unsafe. Under `Decisions: take recommendations`, decide open questions yourself and record each as the core rules' "Decisions" section says; when part of the slice needs a decision on that section's never-decide list, park it there and take the other runnable work, ending the turn only when no runnable work is left. Otherwise state the assumptions and continue in the same turn.
6. Execute. Work through the done-conditions and update each one's status in the spec as it lands. Follow the scope, edit, and Tests and CI rules in the core rules. If a done-condition names a route or web screen, run the app and check it with the browser tool this session has (the desktop browser pane, or Playwright MCP) before marking it done; a route-or-screen done-condition may name a viewport width, and its evidence line must then carry the viewport so the verifier can re-check it in Playwright at that width. Record the route, the viewport when named, what was checked, and a screenshot path if one was taken. If a done-condition names a native screen, set `Surface: ios`, check it before marking it done with the simulator tool this session has or with `xcrun simctl` from the shell when it has none, and record the evidence line as: screen, device, what was checked, screenshot path. If a done-condition adds or changes a screen, run the core rules' "Design" loop for it under the brief's `Design approval:` value, and put its screenshot paths in the evidence lines. Do not end the turn to announce a next step; do the step. In fable-opus mode, replace this step with "Fable-opus mode" below.
7. Verify. Run `/bosun-verify` and act on its verdict. After two FAILs on the same finding, stop and report both positions; under `Decisions: take recommendations`, decide it instead as the core rules' "Decisions" section says (record the decision, take the fix you recommend, verify again), and stop at a third FAIL on the same finding.
8. Record lessons. Before reporting, add to the spec's lessons section anything this slice taught that a fresh session would need and the repo does not record, following the lessons rules in the core rules. Correct or delete entries this slice proved wrong. Often there is nothing to add.
9. Report. Outcome first, then each done-condition with its evidence, then an `Evidence:` list of the route-or-screen checks (route or screen, viewport or device when applicable, what was checked, screenshot path), then follow-ups you noticed but did not do, then anything left out and why. Append a line to the spec's slice log: date, slice name, mode, first-verify verdict, and how many done-conditions named a route or screen against how many the verifier confirmed in its browser or simulator. Append each follow-up to the spec's follow-ups section, one line with the slice name, the date, and its tag (`bug`, `drift`, `nit`, or `deferral`). If undecided items remain, you may add draft done-conditions for the next one to the spec, clearly marked as drafts for the user. If you are stopping mid-slice, run `/bosun-checkpoint`. Under `until blocked`, do not end the turn here; continue with "Until blocked".

## Until blocked

Under `Run policy: until blocked`, after step 9 of a slice that verified PASS or PASS WITH FOLLOW-UPS: commit, push the branch, open a PR for it with `gh pr create` (summary, verification, follow-ups), arm auto-merge as the core rules' "Run policy" section says (`gh pr merge <n> --auto --merge`; `gh pr merge <n> --merge` only when GitHub refuses because every required check is already green; never past a red or missing required check; leave the PR open and say so when the repo has no required checks or disallows auto-merge, or when the spec or the user's instructions say merging is the user's), then go back to step 1 for the next slice in the same turn. Do not idle on the PR's CI (wait only where the core rules' "Merge flow" says), and do not end the turn to ask whether to continue or to announce the next slice; only the stop list below ends the run. Each slice gets its own branch from the latest default branch (step 4) and its own PR. Before starting each slice, after each verify, and while waiting, check the run's open PRs and the default branch's latest CI run, and act on them as the core rules' "Merge flow" says: fix a red or conflicting PR (verifying a code fix) before going on, fix a red default branch first, and, where the repo requires up-to-date branches without a merge queue, update the oldest behind PR. A slice built while another of the run's PRs is open writes its brief as its own subsection under the current-slice section. Keep a count of slices started in this run, including the first.

At each milestone end (core rules, "Follow-ups and milestones": a group of done-conditions the spec names as one, or every fifth slice when it names none), run `/bosun-triage` (which also finds merged, clean, idle worktrees and branches and removes them when applied; see its "Git cleanup"), then a hygiene slice with its own PR for the open bugs, then a `/bosun-ci` audit against recent runs whose findings become follow-ups and whose fixes run as their own slice. When more than five bugs are open, make the next slice a hygiene slice.

Stop, and say in the report which condition stopped the run, at the first of:

- no runnable done-condition remains ("Exhausted roadmap");
- every remaining runnable item needs a decision the lead may not make (core rules, "Decisions");
- a verify produced two FAILs on the same finding, or three under `Decisions: take recommendations` (step 7);
- every remaining runnable slice waits on an unmerged PR that cannot merge on its own (core rules, "Merge flow");
- the count has reached `max N`.

## Exhausted roadmap

When no runnable done-condition remains, at the start or between slices, under either policy, do not invent work. Under `Decisions: take recommendations`, this applies only after step 1 has decided the undecided items it may decide. Report, in this order: that the roadmap is exhausted; every open human-check condition; every undecided item, as the question the spec records; and candidate next slices drawn from the spec's follow-ups section, each written as a draft done-condition and marked as a proposal. End the turn asking what next. Never promote a proposal into a done-condition yourself; the user says which, if any, become work. The one exception: under `Decisions: take recommendations`, a hygiene slice built from open bug follow-ups is runnable work, so promote those bugs to done-conditions and run it before reporting the roadmap exhausted. New features are still never invented.

## Staged briefs

Staging (fable-opus mode, `until blocked`, count below `max N`): while the worker runs, identify the next slice from the spec. If none of its done-conditions depend on what the running slice creates or changes (files it adds or rewrites, interfaces it defines, behavior that must land first), scout that slice's dependencies, reading only, and write a staged brief in the step 3 template to `~/.claude/bosun/workers/<slug>/<next-slice>/brief.md`, with a first line `Based on: <sha>` naming the default branch's HEAD at staging time. If the next slice does depend on the running one, scout only and write what you learned to `notes.md` in that directory. Either way, never write to the worktree while the worker runs, and do not put the staged brief into the spec's current-slice section yet. Only the brief is staged; the worker prompt is written later from the final brief, because it must contain that brief verbatim.

Re-validating: when a staged brief's slice comes up, compare its `Based on:` sha with the latest default branch's HEAD. If they differ, re-read the spec and `git diff <sha>..origin/<default>`, check every file path, line reference, and assumption in the brief against what landed, and fold in any follow-ups from the previous slice's verify that fall inside this slice's done-conditions. Only then write the brief into the spec's current-slice section and continue from step 4; in fable-opus mode the worker prompt is generated from this final brief. If the previous slice's verify FAILed, the staged brief waits for the fix loop. If that loop stopped the run, leave the staged brief on disk and name its path in the report.

## Fable-opus mode

Fable briefs, keeps the spec, commits, and verifies; the project-local `bosun-worker-opus` implements as a native Claude Code subagent on `claude-opus-5-5` at `high`. Add `Route: bosun-worker-opus / claude-opus-5-5 / high` to the brief. Reject any other existing Route override rather than silently reinterpreting it.

Before the first slice, run `/bosun-mode fable-opus` if the project-local agent definitions are absent. Confirm the worker and both verifiers are loaded; a new `.claude/agents/` directory needs a Claude Code restart. Do not continue with plugin-scoped substitutes: they ignore the MCP frontmatter. If model access or the required tools are missing, stop and report the limitation, without falling back to Fable implementation.

Execute (step 6):

1. Write a self-contained worker prompt at `~/.claude/bosun/workers/<slug>/<slice>/prompt.md` (same slug as checkpoints): the final brief verbatim, decisions and out-of-scope list, exact worktree path, the core rules' "While working" scope/test/targeted-edit rules, the core rules' "Design" section and the brief's `Design approval:` value when the slice adds or changes a screen, check commands and setup. Include the app launch command and viewport when web checks are named; for `Surface: ios`, include device, build/install commands, bundle id, and the screen evidence format. Instruct the worker not to commit, edit the spec, or delegate, to preserve others' edits, run the checks, and report changed files, results and evidence.
2. Delegate that prompt to the local `bosun-worker-opus` in the slice's worktree. Do not fork the lead's conversation or spawn parallel implementers. While it runs, do no worktree writes; drafting the report or staging an independent next brief as described above is allowed. A failed or incomplete worker response is not completion.
3. Read the worker's report and the worktree diff before updating spec statuses. For native screens, Fable also checks the named screen as in step 6 of "Spec exists". Record evidence and any model/tool limitations. Do not mark a condition complete from the report alone.
4. Run `/bosun-verify` on Fable at the resolved verifier effort, independent of the worker's high effort. On FAIL, send the verbatim findings, original brief, and the same constraints back to `bosun-worker-opus`; Fable does not implement the fixes. Re-verify at the same effort unless the user changes it. Two FAILs on the same finding stop the loop, or three under `Decisions: take recommendations` (step 7).
5. Once verified, Fable commits. Record route, verifier effort for each attempt, first-verify verdict, and named/confirmed route-or-screen counts in the report and slice log. Use host usage information if available and never invent token counts.

## Long deliverables at xhigh or max

If the session runs at `xhigh` or `max` and a step produces a long deliverable (a large file, a long document), keep this in mind before writing it, with the real limit filled in (`CLAUDE_CODE_MAX_OUTPUT_TOKENS` if set, otherwise the model's 128,000 output cap):

> Everything produced in one reply, including any reasoning or drafting it does before the reply, counts toward a single limit of about [max_tokens] tokens. If that limit is reached before the reply is finished, the person receives a cut-off response and has to start over. Composing an entire output or deliverable in full as reasoning and then again as a reply would double the length of the turn without improving the result, so don't do that. Instead, spend extra effort on understanding the request, checking the inputs the answer depends on, settling the structure and other difficult decisions, and otherwise use the reasoning space to reason and the output space to write an output.
