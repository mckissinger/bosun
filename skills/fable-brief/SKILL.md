---
name: fable-brief
description: Start substantial coding work on Claude Fable 5.1. On a project with no spec, it creates SPEC.md from the request and whatever structures the user supplies, then stops for review. On a project with a spec, it briefs the next slice (outcome, checkable done-conditions, out-of-scope, assumptions, checks, branch), runs it to completion, verifies, and updates the spec. Use at the start of any task beyond a few tool calls (features, multi-file changes, refactors, migrations, debugging), or when the user says "brief this", "start the project", "next slice", or "run this end to end".
argument-hint: "<task, or a paste / path of the structures you already have>"
---

# Fable brief

Fable 5.1 runs long tasks well when the goal is clear and stops to ask when it is not. This skill makes the goal clear once, in the spec, so runs need no mid-task input.

## Find the spec

Look for `SPEC.md` at the repo root, then under the repo's docs convention. If none exists, follow "No spec yet". Otherwise follow "Spec exists".

## Find the provider mode

A line `Provider mode: codex` anywhere in the spec puts the slice in codex mode; anything else (including no line) is fable mode. In codex mode, steps 3 and 6 of "Spec exists" change as described in "Codex mode" at the end of this skill; everything else is the same.

## No spec yet: create it and stop

1. Gather. Read the request and everything the user supplied: pasted structures, document paths, existing code. Batch the reads. If the directory has no git repository, initialize one. If the repo has a docs convention, the spec goes there; otherwise `SPEC.md` at the root. Say which path you chose.
2. Write the spec. It must contain, findably: the outcome; the user's decisions in their own words; every done-condition you can state so that a read-only verifier could check it with git diff, file reads, and the repo's checks (anything only a person can confirm is marked human-check); an undecided list holding everything you could not settle, stated as questions, not guesses; an out-of-scope list; an empty current-slice section; and an empty lessons section. If the user asked for codex mode, add a `Provider mode: codex` line under the first heading (see the core rules); otherwise leave the line out. Choose the layout for this project. Keep it reviewable in one sitting.
3. Stop. End the turn asking the user to review the spec, answer or edit the undecided items they can, and say go. Do not build yet. This is the one planned stop in the workflow.

## Spec exists: brief a slice and run

1. Read the spec, including its lessons. Take the done-conditions the user named, or the next unstarted ones that form a coherent slice. Undecided items are out of scope for this slice.
2. Gather what the slice depends on: the files involved, the test setup, the exact check commands and any setup they need, and the branch state. Batch the reads. Hand side questions to `fable-scout` in the background and keep working.
3. Write the slice brief into the spec's current-slice section and in your reply:

```
Outcome: <one sentence>
Done-conditions: <numbered; each checkable by the verifier's tools, or marked human-check>
Out of scope: <what a careful engineer might touch but must not>
Assumptions: <each ambiguity and the reading chosen, with why>
Effort assumed: <the session's level; you cannot change it>
Checks: <exact commands and any setup they need>
Branch: <name>
```

   For a small task, one line each for outcome, done-condition, and check is the whole brief. In codex mode, add the two lines from "Codex mode" below.

4. Branch. Start from the default branch. If the previous slice's branch is unmerged, stack on it and record that in the spec. Never work on the default branch.
5. Decide whether to stop. End the turn only if a decision that only the user can make blocks the slice and any assumption would make the work useless or unsafe. Otherwise state the assumptions and continue in the same turn.
6. Execute. Work through the done-conditions and update each one's status in the spec as it lands. Follow the scope and edit rules in the global CLAUDE.md. Do not end the turn to announce a next step; do the step. In codex mode, replace this step with "Codex mode" below.
7. Verify. Run `/fable-verify` and act on its verdict. After two FAILs on the same finding, stop and report both positions.
8. Record lessons. Before reporting, add to the spec's lessons section anything this slice taught that a fresh session would need and the repo does not record, following the lessons rules in the core rules. Correct or delete entries this slice proved wrong. Often there is nothing to add.
9. Report. Outcome first, then each done-condition with its evidence, then follow-ups you noticed but did not do, then anything left out and why. If undecided items remain, you may add draft done-conditions for the next one to the spec, clearly marked as drafts for the user. If you are stopping mid-slice, run `/fable-checkpoint`.

## Codex mode

Fable briefs, keeps the spec, commits, and verifies; a Codex model implements. The routing table and the `ultra` ban are in the core rules.

Brief (step 3): add to the brief template

```
Task class: <small | routine | feature | hard, with the one-line reason>
Route: <model> / <effort>   (from the table, or the spec's own Route: override if the current-slice section has one)
Worker network: <yes | no>  (yes only if the slice needs installs or other network access)
```

Execute (step 6):

1. Write the worker prompt to `~/.claude/fable/workers/<slug>/<slice>/prompt.md`, where `<slug>` is the checkpoint slug (cwd with the leading slash removed and every `/` or space replaced by `-`) and `<slice>` is a short name for this slice. The worker has no memory of this session, so the file must contain: the slice brief verbatim; the spec's decisions and out-of-scope lists; the "While working" rules from the core rules (scope, tests, targeted edits); the exact check commands and any setup they need; and these instructions: do not commit, do not edit the spec, run the checks before finishing, and end with a short report naming every file changed and every check run with its result.
2. Run the worker in the background and keep working on anything that does not touch the worktree (drafting the report, reading the spec) until the exit notification arrives. Do not poll.

   ```bash
   "<plugin root>/scripts/codex-worker.sh" --model <model> --effort <effort> --cwd "<worktree>" --prompt-file "<prompt.md>" --out-dir "<same dir as prompt.md>" [--network]
   ```

   `<plugin root>` is the base directory this skill was loaded from, two levels up from this file. The script refuses `ultra` and unknown models, preflights `codex --version` and `codex login status`, and writes `events.jsonl`, `last-message.md`, and `usage.json` into the out dir. A non-zero exit before the worker started (exit 2 or 3) is a stop: report the message; never implement the slice yourself instead.
3. When it exits, read `last-message.md`, `usage.json`, and `git diff` in the worktree. Update each done-condition's status in the spec from what the diff and the worker's report show, not from the report alone. If the worker committed anything, note it as a finding for the report and continue.
4. Verify as in step 7. On FAIL, do not fix the findings yourself: write a follow-up prompt file (the findings verbatim, the original brief, the same instructions) and run the script again with the same route. Two FAILs on the same finding stop the loop as usual.
5. Commit the worker's changes yourself, once verified, with the usual message and trailer.
6. In the report and in the spec's slice log, record: slice name, task class, route, first-verify verdict, and the `usage.json` numbers (wall seconds and token counts).

## Long deliverables at xhigh or max

If the session runs at `xhigh` or `max` and a step produces a long deliverable (a large file, a long document), keep this in mind before writing it, with the real limit filled in (`CLAUDE_CODE_MAX_OUTPUT_TOKENS` if set, otherwise the model's 128,000 output cap):

> Everything produced in one reply, including any reasoning or drafting it does before the reply, counts toward a single limit of about [max_tokens] tokens. If that limit is reached before the reply is finished, the person receives a cut-off response and has to start over. Composing an entire output or deliverable in full as reasoning and then again as a reply would double the length of the turn without improving the result, so don't do that. Instead, spend extra effort on understanding the request, checking the inputs the answer depends on, settling the structure and other difficult decisions, and otherwise use the reasoning space to reason and the output space to write an output.
