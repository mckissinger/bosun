---
name: fable-brief
description: Start substantial coding work on Claude Fable 5.1. On a project with no spec, it creates SPEC.md from the request and whatever structures the user supplies, then stops for review. On a project with a spec, it briefs the next slice (outcome, checkable done-conditions, out-of-scope, assumptions, checks, branch), runs it to completion, verifies, and updates the spec. Use at the start of any task beyond a few tool calls (features, multi-file changes, refactors, migrations, debugging), or when the user says "brief this", "start the project", "next slice", or "run this end to end".
argument-hint: "<task, or a paste / path of the structures you already have>"
---

# Fable brief

Fable 5.1 runs long tasks well when the goal is clear and stops to ask when it is not. This skill makes the goal clear once, in the spec, so runs need no mid-task input.

## Find the spec

Look for `SPEC.md` at the repo root, then under the repo's docs convention. If none exists, follow "No spec yet". Otherwise follow "Spec exists".

## No spec yet: create it and stop

1. Gather. Read the request and everything the user supplied: pasted structures, document paths, existing code. Batch the reads. If the directory has no git repository, initialize one. If the repo has a docs convention, the spec goes there; otherwise `SPEC.md` at the root. Say which path you chose.
2. Write the spec. It must contain, findably: the outcome; the user's decisions in their own words; every done-condition you can state so that a read-only verifier could check it with git diff, file reads, and the repo's checks (anything only a person can confirm is marked human-check); an undecided list holding everything you could not settle, stated as questions, not guesses; an out-of-scope list; an empty current-slice section; and an empty lessons section. Choose the layout for this project. Keep it reviewable in one sitting.
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

   For a small task, one line each for outcome, done-condition, and check is the whole brief.

4. Branch. Start from the default branch. If the previous slice's branch is unmerged, stack on it and record that in the spec. Never work on the default branch.
5. Decide whether to stop. End the turn only if a decision that only the user can make blocks the slice and any assumption would make the work useless or unsafe. Otherwise state the assumptions and continue in the same turn.
6. Execute. Work through the done-conditions and update each one's status in the spec as it lands. Follow the scope and edit rules in the global CLAUDE.md. Do not end the turn to announce a next step; do the step.
7. Verify. Run `/fable-verify` and act on its verdict. After two FAILs on the same finding, stop and report both positions.
8. Record lessons. Before reporting, add to the spec's lessons section anything this slice taught that a fresh session would need and the repo does not record, following the lessons rules in the core rules. Correct or delete entries this slice proved wrong. Often there is nothing to add.
9. Report. Outcome first, then each done-condition with its evidence, then follow-ups you noticed but did not do, then anything left out and why. If undecided items remain, you may add draft done-conditions for the next one to the spec, clearly marked as drafts for the user. If you are stopping mid-slice, run `/fable-checkpoint`.

## Long deliverables at xhigh or max

If the session runs at `xhigh` or `max` and a step produces a long deliverable (a large file, a long document), keep this in mind before writing it, with the real limit filled in (`CLAUDE_CODE_MAX_OUTPUT_TOKENS` if set, otherwise the model's 128,000 output cap):

> Everything produced in one reply, including any reasoning or drafting it does before the reply, counts toward a single limit of about [max_tokens] tokens. If that limit is reached before the reply is finished, the person receives a cut-off response and has to start over. Composing an entire output or deliverable in full as reasoning and then again as a reply would double the length of the turn without improving the result, so don't do that. Instead, spend extra effort on understanding the request, checking the inputs the answer depends on, settling the structure and other difficult decisions, and otherwise use the reasoning space to reason and the output space to write an output.
