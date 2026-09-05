---
name: bosun-checkpoint
description: Save transient session state when stopping mid-slice so the next Claude Code session resumes exactly where this one stopped. The spec holds the durable expectations; the checkpoint holds what the spec does not — position within the current step, problems and how they were handled, options tried and set aside, and details that are hard to reconstruct. Use before stopping mid-task, when the user says "checkpoint", "save state", "hand off", or "we'll continue later".
---

# Bosun checkpoint

The spec is the durable record and must already be current: done-condition statuses, decisions, and the current slice. Update it first if it is not. The checkpoint holds only what the spec does not.

Write to `~/.claude/bosun/checkpoints/<slug>.md`, where `<slug>` is the current working directory with the leading slash removed and every `/` or space replaced by `-`. The SessionStart hook computes the same slug and prints the file at the start of the next session in this directory. Create the directory if it does not exist and overwrite any existing file.

Preserve, under these headings:

1. **Spec and slice** — the spec path and which slice is in progress.
2. **Exactly where things stand** — which done-condition you were on, what is half-done in the working tree, branch name, last commit, which checks currently pass or fail.
3. **Problems and resolutions** — difficulties that came up and how they were handled or resolved.
4. **Options considered** — approaches raised, tried, or set aside, and why.
5. **Anything said this session that is not yet in the spec** — asks, decisions, constraints, preferences, in the user's words. Move these into the spec if you can; list them here if you cannot.
6. **Next actions** — in the order to do them. If a staged brief exists under `~/.claude/bosun/workers/<slug>/`, name its path and whether it has been re-validated.
7. **Hard-to-reconstruct details** — names, numbers, paths, commands, exact wording, links, kept exactly.

Be complete on these even at the cost of length; keep everything else concise. Condense your own reasoning to what it concluded or produced.

After writing, tell the user the path and that the next session in this directory will load it automatically. If the slice is finished rather than paused, delete the file instead of writing one.
