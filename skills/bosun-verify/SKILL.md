---
name: bosun-verify
description: Independently verify a finished slice in a fresh, read-only context before reporting it done — checks the diff against the spec's done-conditions, runs the project's checks, hunts for bugs, and records verified status in the spec. Use after completing a slice, before opening a PR, or when the user asks "is this actually done", "verify", or "double-check".
argument-hint: "[slice name or done-conditions] [--effort low|medium|high|xhigh|max]"
---

# Bosun verify

The session that wrote the code is the wrong judge of it. This skill hands the judgment to a read-only agent at the resolved verifier effort (default `high`) with no memory of this session: `bosun-verifier-mobile` when the brief says `Surface: ios`, otherwise `bosun-verifier`.

## Effort selection

Resolve the provider mode first: no line means `fable`. Only `fable`, `fable-opus`, and `opus` exist; for a removed value (`codex`, `fable-crew`, `astra-crew`, `astra`, removed in 0.18.0) say to choose one of the three with `/bosun-mode`, and reject it and any other unknown value before writes or spawn. In `opus`, use Opus 5.5 for the fresh verifier, including mobile verification; in Fable modes use Fable 5.1.

Resolve the effort before each launch: explicit `--effort <level>` for this invocation; otherwise `Verifier effort:` in the current-slice section; otherwise the top-level `Verifier effort:` beside the provider mode; otherwise `high`. Do not read settings from historical slices, logs, or quoted examples. Accept only `low`, `medium`, `high`, `xhigh`, `max`; missing flag values, unknown flags, duplicate conflicting values at the selected scope, or an invalid selected value stop verification before any writes or spawn. A one-run override never changes the spec default or current-slice setting. `/bosun-mode --verifier-effort <level>` changes the project default.

Run `python3 "<plugin root>/scripts/configure-claude-agents.py" --project "<project root>" --mode <resolved mode> --verifier-effort <resolved effort>` before spawning. Resolve the plugin root from this skill's location. This regenerates **both** project-local verifier definitions with real `effort` frontmatter and the selected model (`claude-opus-5-5` in `opus`, `claude-fable-5-1` in all Fable modes); it also refreshes the scout model and does not change the worker. Always regenerate on the next invocation, so a one-run override does not become a default. Stop on setup errors. Use the local `bosun-verifier` or `bosun-verifier-mobile`, never the plugin-scoped `bosun:...` definition (which would ignore the generated effort). Confirm the local agent is loaded at the requested effort; if the agents directory is new to the running session, restart Claude Code first. A conflicting model environment override or an unavailable agent/model is a blocker, not a reason to silently use another verifier. No lead-session effort change is needed.

Carry the resolved effort through FAIL retries unless the user explicitly changes it, including a one-run `--effort` override. Record each attempt's effective effort in its verdict and in the slice log; never label a prompt-only request as an applied effort setting.

## Steps

1. Assemble a self-contained prompt. The verifier cannot see this conversation, so include:
   - The spec path and which slice or done-conditions to judge. If there is no spec, the done-conditions verbatim from the user's arguments or reconstructed from the request; say which.
   - The out-of-scope list.
   - The base to diff against (branch or commit).
   - The exact check commands and any setup they need.
   - The implementer's check results: for each check run after the last edit, the command and exit code, the working-tree fingerprint it ran on, and the fingerprint command, run in bash with the spec's repo-relative path filled in, which writes nothing and leaves out spec edits: `cd "$(git rev-parse --show-toplevel)" && { git rev-parse HEAD; git diff HEAD --binary --no-ext-diff --no-textconv -- . ':(exclude)<spec path>'; git ls-files -z -o --exclude-standard -- . ':(exclude)<spec path>' | while IFS= read -r -d '' f; do printf '%s\n' "$f"; git hash-object -- "$f"; done; } | git hash-object --stdin`. In fable-opus mode, compute it when the worker reports, before any lead edit outside the spec. Say whether a required CI check runs the full end-to-end suite before merge, and, on a re-verify, which files the fix changed and which checks were rerun for them.
   - Anything the verifier would otherwise misjudge: intentional deviations and their reasons, environment quirks, known pre-existing failures with evidence that they predate the change.
   - When any done-condition names a route or web screen: the implementer's `Evidence:` list (route, viewport when named, what was checked, screenshot path) and the app's launch command. The verifier re-checks only those done-conditions in Playwright, at the named viewport width when one is specified.
   - When a done-condition adds or changes a screen and names a board: the board path, the widths to check (390, 768, 1024, 1280, and 1440 pixels, or the widths the project names), and the states to check (empty, loading, error, hover, and focus, and the board's motion, including exits and reduced motion). The verifier compares its screenshots with the board and reports each difference as a finding.
   - When the brief says `Surface: ios`: the device name, build and install commands, bundle id, and the implementer's evidence lines (screen, device, what was checked, screenshot path).
   - In a lane (core rules, "Lanes"): the lane's stack command and number, to be used for every migration, end-to-end test, seed or data-resetting suite the verifier runs, and the rule that every screenshot and output path is absolute and inside the lane's worktree.
   - The implementer's test and CI statements: each existing test changed, skipped, or deleted and the done-condition that requires it, and, when a CI workflow changed, whether it adds or removes CI time. Where the lead implemented, the lead states these; where a worker did, copy them from its report.
   - The resolved verifier model and effort.
   - In fable-opus mode: the worker is `bosun-worker-opus` (claude-opus-5-5/high). Return FAIL findings to that worker with the original brief; Fable never implements the fixes.
2. When the brief says `Surface: ios`, launch the `bosun-verifier-mobile` agent with that prompt; otherwise launch `bosun-verifier`. While it runs, do not idle: draft the report, continue unrelated remaining work, or, under `Run policy: until blocked`, stage the next slice's brief as `/bosun-brief` ("Staged briefs") describes. Do not edit files the verifier is reading.
3. Relay the verdict faithfully. Do not soften a FAIL.
   - FAIL: in fable or opus mode the lead fixes each in-scope finding; in fable-opus return it to the same implementation worker. The fix reruns only the checks it could change (core rules, Tests and CI), and the re-verify prompt carries their results on the new fingerprint. Then run this skill again at the same resolved verifier effort. After two FAILs on the same finding, stop and report both positions to the user; under `Decisions: take recommendations`, the lead decides it instead (core rules, "Decisions") and stops at a third FAIL on the same finding. Out-of-scope findings go in the report as follow-ups.
   - PASS WITH FOLLOW-UPS: report the follow-ups; fix a bug or security issue in the slice's own work in this slice (core rules, "Follow-ups and milestones"), then run this skill again on the fix before committing, and give every other follow-up the home that section names.
   - PASS: report the verdict and the evidence lines. Screenshot paths the verifier reports are evidence; keep them in the report.
4. Record the verifier model and effective effort with the verdict and in the slice log. For each done-condition the verifier confirmed, mark it verified in the spec with a pointer to the evidence (commit, command, or file:line). Human-check conditions stay unverified and are listed for the user in the report.

Never let the verifier fix things, and never verify by re-reading your own work in this context; that is what the skill exists to avoid.
