---
name: fable-verify
description: Independently verify a finished slice in a fresh, read-only context before reporting it done — checks the diff against the spec's done-conditions, runs the project's checks, hunts for bugs, and records verified status in the spec. Use after completing a slice, before opening a PR, or when the user asks "is this actually done", "verify", or "double-check".
argument-hint: "[slice name or done-conditions, if the spec does not identify them]"
---

# Fable verify

The session that wrote the code is the wrong judge of it. This skill hands the judgment to `fable-verifier`, a read-only agent at `high` effort with no memory of this session.

## Steps

1. Assemble a self-contained prompt. The verifier cannot see this conversation, so include:
   - The spec path and which slice or done-conditions to judge. If there is no spec, the done-conditions verbatim from the user's arguments or reconstructed from the request; say which.
   - The out-of-scope list.
   - The base to diff against (branch or commit).
   - The exact check commands and any setup they need.
   - Anything the verifier would otherwise misjudge: intentional deviations and their reasons, environment quirks, known pre-existing failures with evidence that they predate the change.
   - In fable-crew mode: the worker model and effort that produced the diff. FAIL findings then go back to the worker through `scripts/codex-worker.sh` (see `/fable-brief`, "Fable-crew mode"), not to Fable.
2. Launch the `fable-verifier` agent with that prompt. While it runs, do not idle: draft the report, continue unrelated remaining work, or, under `Run policy: until blocked`, stage the next slice's brief as `/fable-brief` ("Staged briefs") describes. Do not edit files the verifier is reading.
3. Relay the verdict faithfully. Do not soften a FAIL.
   - FAIL: fix each in-scope finding, then run this skill again. After two FAILs on the same finding, stop and report both positions to the user. Out-of-scope findings go in the report as follow-ups.
   - PASS WITH FOLLOW-UPS: report the follow-ups; do not fix them unless the user asks.
   - PASS: report the verdict and the evidence lines.
4. Record. For each done-condition the verifier confirmed, mark it verified in the spec with a pointer to the evidence (commit, command, or file:line). Human-check conditions stay unverified and are listed for the user in the report.

Never let the verifier fix things, and never verify by re-reading your own work in this context; that is what the skill exists to avoid.
