---
name: fable-brief
description: Start substantial coding work on GPT-6 Astra in Codex. On a project with no spec, it creates SPEC.md from the request and whatever structures the user supplies, then stops for review. On a project with a spec, it briefs the next slice (outcome, checkable done-conditions, out-of-scope, assumptions, checks, branch), runs it to completion (itself in astra mode, through a worker subagent in astra-crew), verifies, and updates the spec. Use at the start of any task beyond a few tool calls (features, multi-file changes, refactors, migrations, debugging), or when the user says "brief this", "start the project", "next slice", or "run this end to end".
---

# Fable brief (Codex)

Astra runs long tasks well when the goal is clear and stops to ask when it is not. This skill makes the goal clear once, in the spec, so runs need no mid-task input.

## Find the spec

Look for `SPEC.md` at the repo root, then under the repo's docs convention. If none exists, follow "No spec yet". Otherwise follow "Spec exists".

## Find the provider mode

A line `Provider mode: <mode>` anywhere in the spec names one of four modes (table in the core rules). `astra` is astra mode: you implement each slice yourself. `astra-crew` is astra-crew mode: steps 3 and 6 of "Spec exists" change as described in "Astra-crew mode" at the end of this skill; everything else is the same. `fable`, `fable-crew`, the old value `codex`, or no line at all means the project belongs to Claude Code: report that, name the mode, say to open the project in Claude Code with the harness's Claude plugin (or run `$fable-mode astra-crew` here to move it), and stop without briefing or running anything.

## Find the run policy

A line `Run policy: until blocked` or `Run policy: until blocked, max N slices` anywhere in the spec makes this a continuous run: after each slice verifies, the next one starts in the same turn, as described in "Until blocked" below. Anything else (including no line) is `one slice`: brief, run, verify, report, stop. `until blocked` without a `max` means `max 3 slices`.

## No spec yet: create it and stop

1. Gather. Read the request and everything the user supplied: pasted structures, document paths, existing code. Batch the reads. If the directory has no git repository, initialize one. If the repo has a docs convention, the spec goes there; otherwise `SPEC.md` at the root. Say which path you chose.
2. Write the spec. It must contain, findably: the outcome; the user's decisions in their own words; every done-condition you can state so that a read-only verifier could check it with git diff, file reads, and the repo's checks (anything only a person can confirm is marked human-check); an undecided list holding everything you could not settle, stated as questions, not guesses; an out-of-scope list; an empty current-slice section; an empty follow-ups section; and an empty lessons section. Add a `Provider mode: astra` or `Provider mode: astra-crew` line under the first heading, whichever the user asked for (astra-crew if they did not say). If the user asked for continuous runs, add `Run policy: until blocked, max N slices` next to it; otherwise leave that line out. Choose the layout for this project. Keep it reviewable in one sitting.
3. Stop. End the turn asking the user to review the spec, answer or edit the undecided items they can, and say go. Do not build yet. This is the one planned stop in the workflow.

## Spec exists: brief a slice and run

1. Read the spec, including its lessons. If no runnable done-condition remains (status `todo` or `in progress`, not `human-check`, nothing it needs on the undecided list), follow "Exhausted roadmap" below and stop. Otherwise take the done-conditions the user named, or the next unstarted ones that form a coherent slice. Undecided items are out of scope for this slice. If a staged brief exists for this slice (see "Staged briefs"), re-validate it as described there instead of writing a new one.
2. Gather what the slice depends on: the files involved, the test setup, the exact check commands and any setup they need, and the branch state. Batch the reads. Hand side questions to the `fable_scout` agent with a self-contained prompt and keep working while it runs.
3. Write the slice brief into the spec's current-slice section and in your reply:

```
Outcome: <one sentence>
Done-conditions: <numbered; each checkable by the verifier's tools, or marked human-check>
Out of scope: <what a careful engineer might touch but must not>
Assumptions: <each ambiguity and the reading chosen, with why>
Effort assumed: <the session's level from the app's picker; you cannot change it>
Checks: <exact commands and any setup they need>
Branch: <name>
```

   For a small task, one line each for outcome, done-condition, and check is the whole brief. In astra-crew mode, add the lines from "Astra-crew mode" below.

4. Branch. Start from the default branch. If the previous slice's branch is unmerged, stack on it and record that in the spec. Never work on the default branch.
5. Decide whether to stop. End the turn only if a decision that only the user can make blocks the slice and any assumption would make the work useless or unsafe. Otherwise state the assumptions and continue in the same turn.
6. Execute. Work through the done-conditions and update each one's status in the spec as it lands. Follow the scope and edit rules in the core rules. Do not end the turn to announce a next step; do the step. In astra-crew mode, replace this step with "Astra-crew mode" below.
7. Verify. Run `$fable-verify` and act on its verdict. After two FAILs on the same finding, stop and report both positions.
8. Record lessons. Before reporting, add to the spec's lessons section anything this slice taught that a fresh session would need and the repo does not record, following the lessons rules in the core rules. Correct or delete entries this slice proved wrong. Often there is nothing to add.
9. Report. Outcome first, then each done-condition with its evidence, then follow-ups you noticed but did not do, then anything left out and why. Append each follow-up to the spec's follow-ups section, one line with the slice name and date. If undecided items remain, you may add draft done-conditions for the next one to the spec, clearly marked as drafts for the user. If you are stopping mid-slice, run `$fable-checkpoint`. Under `until blocked`, do not end the turn here; continue with "Until blocked".

## Until blocked

Under `Run policy: until blocked`, after step 9 of a slice that verified PASS or PASS WITH FOLLOW-UPS: commit, push the branch, open a PR for it with `gh pr create` (summary, verification, follow-ups; never merge), then go back to step 1 for the next slice in the same turn. Each slice gets its own branch, stacked on the previous one while that is unmerged (step 4), and its own PR. Keep a count of slices started in this run, including the first.

Stop, and say in the report which condition stopped the run, at the first of:

- no runnable done-condition remains ("Exhausted roadmap");
- the next runnable done-condition depends on an undecided item;
- a verify produced two FAILs on the same finding (step 7);
- the count has reached `max N`.

## Exhausted roadmap

When no runnable done-condition remains, at the start or between slices, under either policy, do not invent work. Report, in this order: that the roadmap is exhausted; every open human-check condition; every undecided item, as the question the spec records; and candidate next slices drawn from the spec's follow-ups section, each written as a draft done-condition and marked as a proposal. End the turn asking what next. Never promote a proposal into a done-condition yourself; the user says which, if any, become work.

## Staged briefs

Staging (astra-crew mode, `until blocked`, count below `max N`): while the worker runs, identify the next slice from the spec. If none of its done-conditions depend on what the running slice creates or changes (files it adds or rewrites, interfaces it defines, behavior that must land first), scout that slice's dependencies, reading only, and write a staged brief in the step 3 template to `~/.codex/fable/workers/<slug>/<next-slice>/brief.md`, with a first line `Based on: <sha>` naming the worktree's HEAD at staging time. If the next slice does depend on the running one, scout only and write what you learned to `notes.md` in that directory. Either way, never write to the worktree while the worker runs, and do not put the staged brief into the spec's current-slice section yet. Only the brief is staged; the worker prompt is written later from the final brief, because it must contain that brief verbatim.

Re-validating: when a staged brief's slice comes up, compare its `Based on:` sha with the worktree's HEAD. If they differ, re-read the spec and `git diff <sha>..HEAD`, check every file path, line reference, and assumption in the brief against what landed, and fold in any follow-ups from the previous slice's verify that fall inside this slice's done-conditions. Only then write the brief into the spec's current-slice section and continue from step 4; the worker prompt is generated from this final brief. If the previous slice's verify FAILed, the staged brief waits for the fix loop. If that loop stopped the run, leave the staged brief on disk and name its path in the report.

## Astra-crew mode

You brief, keep the spec, commit, and verify; a Sol or Luna worker subagent implements. The routing table and the `ultra` ban are in the core rules. If the worker agents are not installed (`~/.codex/agents/fable-worker-*.toml`), run `$fable-mode astra-crew` first.

Brief (step 3): add to the brief template

```
Task class: <small | routine | feature | hard, with the one-line reason>
Route: <fable_worker_small | fable_worker_routine | fable_worker_feature | fable_worker_hard>   (from the table, or the spec's own Route: override if the current-slice section has one)
```

Execute (step 6):

1. Write the worker prompt to `~/.codex/fable/workers/<slug>/<slice>/prompt.md`, where `<slug>` is the checkpoint slug (cwd with the leading slash removed and every `/` or space replaced by `-`) and `<slice>` is a short name for this slice. The worker has no memory of this session, so the file must contain: the slice brief verbatim; the spec's decisions and out-of-scope lists; the "While working" rules from the core rules (scope, tests, targeted edits); the exact check commands and any setup they need; the worktree path; and these instructions: do not commit, do not edit the spec, run the checks before finishing, and end with a short report naming every file changed and every check run with its result.
2. Delegate: spawn the worker agent named by the `Route:` line with the prompt file's contents as its task, in this worktree, and wait for it. Do not implement the slice yourself while it runs. Keep working on anything that does not touch the worktree (drafting the report, reading the spec, staging the next brief as "Staged briefs" describes under `until blocked`).
3. When the worker finishes, read its report and `git diff` in the worktree. Update each done-condition's status in the spec from what the diff and the report show, not from the report alone. If the worker committed anything, note it as a finding for the report and continue.
4. Verify as in step 7. On FAIL, do not fix the findings yourself: write a follow-up prompt file (the findings verbatim, the original brief, the same instructions) and spawn the same worker agent again with it. Two FAILs on the same finding stop the loop as usual.
5. Commit the worker's changes yourself, once verified, with the usual message.
6. In the report and in the spec's slice log, record: slice name, task class, route, and first-verify verdict. There is no usage file; the app's usage view is the cost record.
