# Archive no-PR sessions (2026-11-25)

Status: verified 2026-11-25 (first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS)
Mode: opus (Opus 5.5 leads and implements).

## Decisions

These are the two `bug` follow-ups from archive-started-sessions (2026-11-25), fixed in the next slice as that record says, under Michael's "Maybe we just start with option two".

## Brief

Outcome: A started session that never committed, such as a plan, design or read-only session, is archived once its work is done instead of always being reported. A detached-HEAD worktree with commits on no branch is reported instead of archived.

Size: about 10 changed lines.

Done-conditions:
N1. `verified 2026-11-25 bosun-verifier (claude-opus-5-5, high then medium delta), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS; HEAD 1f59fcd` `rules/core.md` "Sessions a session starts", worktree test bullet:
- A branch whose tip is already on the default branch counts as safe, which covers a session with no commits.
- A branch whose tip is a merged or open PR's head still counts as safe.
- Any other branch tip is reported.
- A detached HEAD whose commit is on no branch is reported.
N2. `verified 2026-11-25 bosun-verifier (claude-opus-5-5, high then medium delta), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS; HEAD 1f59fcd` The copies match: the README lanes paragraph, and the brief's lane bullet ("commits that no PR or the default branch holds").
N3. `verified 2026-11-25 bosun-verifier (claude-opus-5-5, high then medium delta), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS; HEAD 1f59fcd` The two bug follow-ups are removed from `slices/2026-11-25-archive-started-sessions.md`. Version 0.37.1 in both manifests and the README version line.
N4. `verified 2026-11-25 bosun-verifier (claude-opus-5-5, high then medium delta), first PASS WITH FOLLOW-UPS, second PASS WITH FOLLOW-UPS; HEAD 1f59fcd` Checks pass:
- `bash -n scripts/*.sh`;
- JSON parses for both manifests and `hooks/hooks.json`;
- `python3 -m py_compile scripts/*.py`;
- `python3 scripts/ci-conformance.py --help`.

Out of scope: the F8 deferral (a gone session's own sessions); triage's "Git cleanup".

Decisions: ask (Bosun's spec has no `Decisions:` line).
Verifier effort: high (no override at any scope).
Checks: as N4. Pre-verify gate: N4's commands.
Branch: archive-no-pr-sessions

## Verify runs

Run 1 (2026-11-25, bosun-verifier claude-opus-5-5/high, HEAD 3934cce, fingerprint ec048bf7): PASS WITH FOLLOW-UPS. N1–N4 met.
- 1: "already on the default branch" named no ref, and a stale local `main` would report no-commit sessions again. Fixed: `origin/<default branch>` after a `git fetch`.
- 2: the brief and README copies were looser than the rule ("no PR", "holds"). Fixed: both now say "a HEAD that is neither on the default branch nor a merged or open PR's head commit".
- 3: a detached HEAD at an unmerged branch tip passed. Fixed: one test now covers HEAD on a branch or detached.
- Nit: the bullet is split into a test sentence and a note.

Run 2 (2026-11-25, bosun-verifier claude-opus-5-5/medium delta, HEAD 1f59fcd, fingerprint c2c6d23d): PASS WITH FOLLOW-UPS. Items 1–3 are resolved. Afterwards, as wording with no verify run:
- 4: the fetch and `origin/` clause was added to the brief and README copies.
- 5: the note became "commits made after its last PR merged".
- The README nit (commits given as an example of a HEAD) was fixed.

Log: 2026-11-25, archive-no-pr-sessions, first verify PASS WITH FOLLOW-UPS (no blocking finding), verifier claude-opus-5-5 high then medium delta; routes or screens named: 0 of 0.
