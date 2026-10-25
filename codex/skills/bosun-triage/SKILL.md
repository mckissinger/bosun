---
name: bosun-triage
description: Review a project's spec against its code and history and clean up its bookkeeping. Finds done-conditions whose status is wrong, follow-ups that are resolved, stale, duplicated, or deferred, decisions that never became done-conditions, and open human-checks, and keeps live content ahead of finished work. Use when the spec has piled up follow-ups, feels out of date, or the user asks to "triage the spec", "clean up follow-ups", or "what's actually left". Produces a report; changes the spec only after the user approves, except at a milestone end under `Decisions: take recommendations`, where it applies the evidence-backed corrections itself.
---

# Bosun triage (Codex)

Bring the spec back in line with what the code and history show, so the next session reads an accurate list of what is done, what is left, and what is waiting on the user. Triage changes the spec's bookkeeping, never code.

## When to run

When the user asks, and at each milestone end under `Run policy: until blocked` (core rules, "Follow-ups and milestones"). First check for an active slice: a current-slice status of `in progress`, done-conditions marked implemented and awaiting verify (a plain `done` does not count), or a checkpoint for the project (`~/.claude/bosun/checkpoints/<slug>.md` in Claude Code, `~/.codex/bosun/checkpoints/<slug>.md` in Codex, with the slug `bosun-checkpoint` uses). If you find one, report it with its date and the date of the last commit that touched the spec, and ask the user whether that work is still active. Stop if it is, because the running slice owns the spec until it finishes. If the user says it is not, proceed and report the stale status or checkpoint as a finding; never delete a checkpoint yourself.

## Read the spec as it is

Specs differ between projects. Work from meaning, not from fixed headings: find the outcome, decisions, done-conditions and their statuses, follow-ups (a section, a ledger inside the done-conditions, or scattered "follow-up" notes), deferrals, human-checks, the slice log, lessons, and any history file the spec points to. Note the spec's own conventions, such as numbered sections and the status words it uses, and keep them.

Batch the reads: the spec, any history file, `git log` since the oldest open item, and the files each item names. Hand independent groups of items to `bosun_scout` in the background while you work through others.

## Review

Every conclusion cites evidence: a commit, a file and line, or a command and its output. When evidence is missing or ambiguous, say "unclear" and why; never resolve an item on a guess. An unclear item stays as it is, untagged if it was untagged, until the user decides.

1. **Done-condition statuses.** Find conditions marked `todo` or `in progress` that a commit already delivered; conditions marked done or verified whose cited file, line, or check no longer shows what it claimed; and conditions that are stale because the work moved elsewhere. Do not mark anything verified: verification belongs to `$bosun-verify`. Report a delivered condition as "delivered, needs verify": the correction sets it to the spec's word for done but not yet verified (`done` in Bosun's own status words), and the report lists it for `$bosun-verify`.
2. **Follow-ups.** Check each one against the current code and history, and classify it:
   - **resolved**, with the commit or file and line that resolved it;
   - **still valid**, tagged `bug`, `drift` (docs, comments, or spec text out of step with the code), or `nit`;
   - **deferral**, a user decision to postpone, with its revisit trigger quoted or marked missing;
   - **obsolete**, because the code or feature it refers to is gone.

   Keep an existing tag unless the evidence contradicts it. Merge duplicates, keeping the earliest slice and date. Group still-valid items that touch the same files or behavior into draft slices, each written as a draft done-condition.
3. **Missed items.** Find decisions in the user's words that no done-condition covers, and follow-ups named in PR descriptions, verify reports, or the slice log that never reached the follow-ups.
4. **Waiting on the user.** List open human-checks oldest first, each with the exact step the user must take; conditions marked done but not verified, for `$bosun-verify`; and deferrals whose revisit trigger has now happened.
5. **Spec health.** Report the spec's length and whether live content (outcome, decisions, current slice, open done-conditions, human-checks, follow-ups, undecided and out-of-scope items, lessons) comes before finished work. Never condense, summarize, or reword the spec's text. Propose a reorder only as a pure move: live content first, and every finished slice under one history heading at the bottom. Do not propose a reorder when the spec cross-references its own numbered sections (for example "§4 Y"), since moving sections breaks those references. If finished work already lives in a separate history file, keep that arrangement.

## Report

Deliver, in this order:

1. **Summary:** counts by category (statuses to fix, follow-ups resolved, still valid by tag, deferrals, obsolete, duplicates, missed items, human-checks open) and the spec's length.
2. **Proposed removals:** each resolved, obsolete, or duplicate follow-up with its evidence. This is the batch the user approves or edits.
3. **Status corrections**, with evidence.
4. **Still valid**, by tag, and the draft slices built from them.
5. **Missed items** and **waiting on the user**.
6. **Spec health**, with the proposed reorder as a list of section moves, or the reason none is proposed.

End by asking the user which parts to apply. Do not change the spec before they answer, except as "Milestone end" below says.

## Milestone end

When triage runs at a milestone end under `Decisions: take recommendations`, the lead applies it itself instead of asking: the proposed removals and the status corrections, each with its evidence, and the draft slices built from open bugs, promoted to hygiene done-conditions. Unclear items stay as they are, everything else stays a draft for the user, and no decision is reworded. The result is a bookkeeping commit on its own branch and PR, made as "Apply on approval" describes. Under `Decisions: ask`, triage reports and waits as above, at a milestone end too.

At a milestone end under `until blocked`, the run's own last slice is finished, not active, so the active-slice check in "When to run" asks about other work only. When earlier slices' PRs are still unmerged, branch from the latest slice's branch instead of the default branch, so the bookkeeping is built on the spec the run left, and say so in the PR.

## Apply on approval

Apply only what the user approved (or what "Milestone end" applies), on a new branch from the default branch, in two separate commits:

1. **Bookkeeping:** remove the approved batch of follow-ups; correct the approved statuses; add tags to untagged follow-ups that stay, except items reported as unclear; add missed follow-ups; add draft slices clearly marked as drafts. Never promote a draft to a done-condition: the user does that, apart from the hygiene done-conditions "Milestone end" allows. Never change a decision's wording.
2. **Reorder**, when approved: move sections and nothing else. Existing headings keep their text and level. Prove it before committing by comparing the full sorted list of non-blank lines before and after the move, duplicates included (a plain sort and diff, never a unique sort); the lists must match exactly except for exactly one added line, the history heading. If they differ in any other way, undo the move and report the difference.

Open a PR for the branch as the user's git instructions require. Report what changed and what was left as it was.

## Boundaries

Triage never edits code, tests, or configuration, never runs `$bosun-brief` or implements a follow-up, and never marks a done-condition verified. It does not decide what is worth doing: draft slices are proposals (apart from hygiene slices under "Milestone end"), and deferrals stay deferred until the user says otherwise.
