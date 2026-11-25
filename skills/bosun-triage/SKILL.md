---
name: bosun-triage
description: Review a project's spec against its code and history and clean up its bookkeeping and its merged worktrees and branches. Finds done-conditions whose status is wrong, follow-ups that are resolved, stale, duplicated, or deferred, decisions that never became done-conditions, and open human-checks, and keeps live content ahead of finished work. Use when the spec has piled up follow-ups, feels out of date, or the user asks to "triage the spec", "clean up follow-ups", or "what's actually left". Produces a report; changes the spec only after the user approves, except at a milestone end under `Decisions: take recommendations`, where it applies the evidence-backed corrections itself.
---

# Bosun triage

Bring the spec back in line with what the code and history show, so the next session reads an accurate list of what is done, what is left, and what is waiting on the user. Triage changes the spec's bookkeeping, never code.

## When to run

When the user asks, and at each milestone end under `Run policy: until blocked` (core rules, "Follow-ups and milestones"). Where the project runs the weekly checks triage (`bosun-ci`, "Weekly checks triage (opt-in)"), a cloud scheduled task runs steps 7 and 8 only, each week; it changes only the lesson and draft done-conditions, on its own branch, so it skips the active-slice check below. First check for an active slice in the checkout triage works in: a slice record on its branch that is not yet on the default branch (core rules, "Slice records"; records on other branches, such as running lanes', are other sessions' work and touch the spec only as "Slice records" allows, so they do not stop triage) or an older spec's current-slice section, with a status of `in progress`, done-conditions marked implemented and awaiting verify (a plain `done` does not count), a current slice whose done-conditions, apart from human-checks, are not all verified and whose PR has not merged (a slice paused between implementing and verify looks like this), or a checkpoint for the project (`~/.claude/bosun/checkpoints/<slug>.md`, with the slug `bosun-checkpoint` uses). If you find one, report it with its date and the date of the last commit that touched the spec, and ask the user whether that work is still active. Stop if it is, because that slice is still writing the spec and its record. If the user says it is not, proceed and report the stale status or checkpoint as a finding; never delete a checkpoint yourself.

## Read the spec as it is

Specs differ between projects. Work from meaning, not from fixed headings: find the outcome, decisions, done-conditions and their statuses, follow-ups (a section, the Follow-ups sections of slice records under `slices/`, a ledger inside the done-conditions, or scattered "follow-up" notes), deferrals, human-checks, the slice log (the records' `Log:` lines and any older entries in the spec), lessons, and any history file the spec points to. Note the spec's own conventions, such as numbered sections and the status words it uses, and keep them.

Batch the reads: the spec, the slice records, any history file, `git log` since the oldest open item, and the files each item names. Hand independent groups of items to `bosun-scout` in the background while you work through others.

## Review

Every conclusion cites evidence: a commit, a file and line, or a command and its output. When evidence is missing or ambiguous, say "unclear" and why; never resolve an item on a guess. An unclear item stays as it is, untagged if it was untagged, until the user decides.

1. **Done-condition statuses.** Find conditions marked `todo` or `in progress` that a commit already delivered; conditions marked done or verified whose cited file, line, or check no longer shows what it claimed; and conditions that are stale because the work moved elsewhere. Do not mark anything verified: verification belongs to `/bosun-verify`. Report a delivered condition as "delivered, needs verify": the correction sets it to the spec's word for done but not yet verified (`done` in Bosun's own status words), and the report lists it for `/bosun-verify`.
2. **Follow-ups.** Check each one against the current code and history, and classify it:
   - **resolved**, with the commit or file and line that resolved it;
   - **still valid**, tagged `bug`, `drift` (docs, comments, or spec text out of step with the code), or `nit`;
   - **deferral**, a user decision to postpone, with its revisit trigger quoted or marked missing;
   - **obsolete**, because the code or feature it refers to is gone.

   Keep an existing tag unless the evidence contradicts it. Merge duplicates, keeping the earliest slice and date. Group still-valid items that touch the same files or behavior into draft slices, each written as a draft done-condition.
3. **Missed items.** Find decisions in the user's words that no done-condition covers, and follow-ups named in PR descriptions, verify reports, or the slice log that never reached the open follow-ups, leaving out nits, which are never written down (core rules, "Finishing").
4. **Waiting on the user.** List open human-checks oldest first, each with the exact step the user must take; conditions marked done but not verified, for `/bosun-verify`; and deferrals whose revisit trigger has now happened.
5. **Spec health.** Report the spec's length and whether live content (outcome, decisions, the pointers to slice records or an older current-slice section, open done-conditions, human-checks, follow-ups, undecided and out-of-scope items, lessons) comes before finished work. Never condense, summarize, or reword the spec's text. Propose a reorder only as a pure move: live content first, and every finished slice under one history heading at the bottom. Do not propose a reorder when the spec cross-references its own numbered sections (for example "§4 Y"), since moving sections breaks those references. If finished work already lives in a separate history file, keep that arrangement.
6. **Archive.** When finished work keeps the spec past one sitting, propose moving it, verbatim, to an archive file next to the spec (`SPEC-archive.md` beside `SPEC.md`, or the project's existing history file): the briefs of merged slices, and slice-log entries from before the latest milestone. Decisions, lessons, open items and anything a live item cross-references by number stay. Where the moved text was, one pointer line names the archive. A merged slice's brief still sitting in an older spec's current-slice section is a status correction: it moves under history first. Slice records are already their slices' history and are not archived.
7. **Recurring verify failures.** Read the blocking-finding kinds across the whole slice log (the records' `Log:` lines and the spec's older entries, archived ones included), and the FAIL findings each slice record's verify section holds (its verdict lines and findings, the main source since `Log:` lines are short), for the slices since the last triage or the last four weeks, whichever is longer. Group the findings by kind of defect and count the slices each kind hit. A kind seen in two or more slices gets a line in the spec's "Recurring verify failures" lesson, with one short example; a kind no blocking finding has shown in the last two milestones (two months, in the weekly checks triage) leaves it. Keep the entry to ten lines, merging near-duplicates, and create it empty if the spec lacks it. For each line it adds, name a candidate check (a lint rule, hook, test or CI check) that would catch that kind of defect, as core's "Corrections become checks" says, as a draft done-condition for the user, with whether the repository already has such a check (search for it) and a rough cost (small, medium or large). A kind an existing check would have caught had it run gets no new check: name the check, since the pre-verify gate covers it. Kinds no check can express are listed without one.
8. **Checks due for review.** List the checks added under core's "Corrections become checks" (each names its finding kind and date in a comment beside it) that are more than two months old, each with its file, kind and date, for the user to keep or retire. Triage never removes one.

## Report

Deliver, in this order:

1. **Summary:** counts by category (statuses to fix, follow-ups resolved, still valid by tag, deferrals, obsolete, duplicates, missed items, human-checks open) and the spec's length.
2. **Proposed removals:** each resolved, obsolete, or duplicate follow-up with its evidence. This is the batch the user approves or edits.
3. **Status corrections**, with evidence.
4. **Still valid**, by tag, and the draft slices built from them.
5. **Missed items** and **waiting on the user**.
6. **Spec health**, with the proposed reorder as a list of section moves, or the reason none is proposed, and the proposed archive moves.
7. **Recurring verify failures:** the lesson's lines to add, keep and drop, each with the slices that showed it, and for each added line its candidate check as a draft done-condition, with whether one exists and its cost.
8. **Checks due for review**, for the user to keep or retire.
9. **Leftover stacks and servers**, as that section says, for the user or the owning session to act on.

End by asking the user which parts to apply. Do not change the spec before they answer, except as "Milestone end" below says.

## Git cleanup

Triage also reports the repo's leftover worktrees and local branches. Run `git fetch --prune` and `git worktree prune` (they only refresh remote-tracking refs and drop records of worktrees whose directory is already gone; no checkout or local branch changes), then read `git worktree list --porcelain`. A worktree is removable only when all of these hold:

- it is not the main checkout or the one this session runs in, and it is not locked;
- it is not under `.claude/worktrees/`, since the Claude desktop app cleans up the worktrees it creates;
- it has a branch checked out, not a detached HEAD, and that branch is not the default branch;
- its work is merged: `gh pr list --state merged --head <branch> --base <default> --json headRefOid` shows a PR merged into the default branch whose head commit is the branch tip. Ancestry of `origin/<default>` alone is not enough, since a branch with no commits of its own passes it; a branch merged without a PR is reported, not removed;
- `git -C "<path>" status --porcelain --ignored` shows no uncommitted or untracked files, and no ignored files other than dependency and build output (such as `node_modules`, `.next`, `dist`, or caches); a `.env` file or local data keeps it, because `git worktree remove` deletes ignored files without asking;
- no process has its working directory inside it (`lsof -a -d cwd -Fn` lists none under the path, compared with symlinks resolved, as `pwd -P` prints it).

A local branch with no worktree is removable when it is not the default branch, not the branch this session is on, and its work is merged by the same merged-PR test. Remove a worktree with `git worktree remove "<path>"`, never with `--force`, then delete its branch. Delete a branch with `git branch -D`, which the merged-PR test makes safe (`git branch -d` refuses squash-merged branches). Never delete a remote branch, and never remove anything that fails a test; when a command refuses, leave that item and report why.

The report lists each removable worktree and branch with the evidence for it, and every other worktree with the reason it stays. Under `Decisions: ask`, removal waits for the user's approval like the rest of the report. At a milestone end under `Decisions: take recommendations`, the lead removes them itself, as "Milestone end" says. Cleanup changes no file in the repo, so it is never part of a commit.

## Leftover stacks and servers

Triage also reports what this project has left running or stored on the machine: its containers and volumes (`docker ps -a` and `docker volume ls`, matched by the stack's configured project id, exactly or with a lane suffix; anything else that resembles it is listed as unclear), with their state and age, and dev servers listening from a worktree that is gone or merged. For each, say whether the spec's `Stack isolation:` command accounts for it. Report only: stacks and volumes may hold data or belong to another running session, so triage stops and deletes none of them, at a milestone end or otherwise. The user or the owning session does that.

## Milestone end

When triage runs at a milestone end under `Decisions: take recommendations`, the lead applies it itself instead of asking: the proposed removals and the status corrections, each with its evidence, and the draft slices built from open bugs, promoted to hygiene done-conditions, the "Recurring verify failures" update, the archive moves, and the removable worktrees and branches "Git cleanup" found. Unclear items stay as they are, everything else stays a draft for the user, and no decision is reworded. The result is the commits "Apply on approval" describes, made on the branch of the hygiene slice that follows, or of the run's next slice, as the core rules' "Records ride along" says; only when no slice follows do they go in the end-of-run records PR. While lanes run, the hub instead commits them to its records branch and opens that branch's PR at this milestone end (core rules, "Lanes"). Under `Decisions: ask`, triage reports and waits as above, at a milestone end too.

At a milestone end under `until blocked`, the run's own last slice is finished, not active, so the active-slice check in "When to run" asks about other work only. Triage builds on the spec every slice of the run left, so it waits until the run's open PRs have merged, as the core rules' "Merge flow" waits: only for PRs that merge on their own. When one cannot, the run stops and names it. Then it works on the branch the following hygiene or next slice will use, cut from the latest default branch, or on the hub's records branch while lanes run.

## Apply on approval

Apply only what the user approved (or what "Milestone end" applies), on a new branch from the default branch (or the branch "Milestone end" names), in separate commits:

1. **Bookkeeping:** remove the approved batch of follow-ups from the file that holds each one (the spec or a slice record); correct the approved statuses; add tags to untagged follow-ups that stay, except items reported as unclear; add missed follow-ups; add draft slices clearly marked as drafts; apply the "Recurring verify failures" update. Never promote a draft to a done-condition: the user does that, apart from the hygiene done-conditions "Milestone end" allows. Never change a decision's wording.
2. **Reorder**, when approved: move sections and nothing else. Existing headings keep their text and level. Prove it before committing by comparing the full sorted list of non-blank lines before and after the move, duplicates included (a plain sort and diff, never a unique sort); the lists must match exactly except for exactly one added line, the history heading. If they differ in any other way, undo the move and report the difference.
3. **Archive**, when approved: move the approved text to the archive file and nothing else, leaving one pointer line where each block was. Prove it the same way, comparing the sorted non-blank lines of the spec and archive together before and after; they must match except for the added pointer lines and, for a new archive file, its one heading.

Run any approved git cleanup as "Git cleanup" says; it is not part of any commit.

Outside a run, open a PR for the branch as the user's git instructions require. During a run, open none: the slice's PR, the hub's records PR or, when no slice follows, the end-of-run records PR carries the commits (core rules, "Records ride along"). Report what changed and what was left as it was.

## Boundaries

Triage never edits code, tests, or configuration, removes worktrees and branches only as "Git cleanup" says, stops or deletes no stack, volume or server, never runs `/bosun-brief` or implements a follow-up, and never marks a done-condition verified. It does not decide what is worth doing: draft slices are proposals (apart from hygiene slices under "Milestone end"), and deferrals stay deferred until the user says otherwise.
