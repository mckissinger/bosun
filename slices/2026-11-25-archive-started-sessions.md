# Archive started sessions (2026-11-25)

Status: in progress
Mode: opus (Opus 5.5 leads and implements).

## Decisions

See the SPEC.md 2026-11-25 entry "Archive every started session". Michael: "Maybe we just start with option two." He chose the Bosun rule over the app's archive-inactive setting.

## Brief

Outcome: A session that starts other sessions archives each one once its work is done, whether it was a lane or a one-off task. The desktop app can then remove its worktree, and idle sessions and worktrees stop piling up.

Size: about 30 changed lines of rule text and docs.

Done-conditions:
A1. **The rule.** `rules/core.md` gains "Sessions a session starts", after "Other sessions".
- **Who archives:** any session that starts others with the host's start-session tool archives each one it started. This covers lanes, one-off task sessions and plan or design sessions.
- **When:** the started session is not running, every PR it opened has merged or closed, and it waits on no verify, decision or answer. Its last report asks nothing of the user or of its starter.
- **Before archiving:** the starter reads that session's last report and PR state, and confirms its stack is gone, reporting rather than stopping a running one.
- **How:** with the host's archive tool, never deleting.
- **Exceptions:** a session with uncommitted worktree changes is reported, not archived. A session the user started is never archived.
- **Checked:** wherever open PRs are checked ("Merge flow"), and on each report.
- "Lane end" points to this rule.

A2. **The brief.** `skills/bosun-brief/SKILL.md`'s hub bullet archives the hub's non-lane sessions the same way, checked whenever the hub checks its open PRs.

A3. **Records.**
- The README lanes paragraph matches.
- Version 0.37.0 in both manifests and the README version line.
- A SPEC.md decision entry.

A4. **Checks pass:** `bash -n scripts/*.sh`; JSON parses for both manifests and `hooks/hooks.json`; `python3 -m py_compile scripts/*.py`; `python3 scripts/ci-conformance.py --help`.

Out of scope:
- the app's auto-archive settings;
- triage's worktree rules;
- archiving sessions the user started;
- stopping stacks.

Assumptions: archiving through the desktop app removes the session's worktree, as the app's own setting describes ("a worktree with uncommitted changes stays on disk").

Decisions: ask (Bosun's spec has no `Decisions:` line).
Verifier effort: high (no override at any scope).
Checks: as A4. Pre-verify gate: A4's commands.
Branch: archive-started-sessions
