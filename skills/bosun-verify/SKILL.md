---
name: bosun-verify
description: Independently verify a finished slice in a fresh, read-only context before reporting it done — checks the diff against the spec's done-conditions, runs the project's checks, hunts for bugs, and records verified status in the spec. Use after completing a slice, before opening a PR, or when the user asks "is this actually done", "verify", or "double-check".
argument-hint: "[slice name or done-conditions] [--effort low|medium|high|xhigh|max]"
---

# Bosun verify

The session that wrote the code is the wrong judge of it. This skill hands the judgment to a read-only agent at the resolved verifier effort (default `high`) with no memory of this session: `bosun-verifier-mobile` when the brief says `Surface: ios`, otherwise `bosun-verifier`.

## Effort selection (Claude modes)

Resolve the provider mode first: no line means `fable`, `codex` means `fable-crew`. Only `fable`, `fable-crew`, `fable-opus`, and `opus` run here; redirect Astra modes to Codex and reject unknown values before writes or spawn. In `opus`, use Opus 5.5 for the fresh verifier, including mobile verification; in Fable modes use Fable 5.1.

Resolve the effort before each launch: explicit `--effort <level>` for this invocation; otherwise `Verifier effort:` in the current-slice section; otherwise the top-level `Verifier effort:` beside the provider mode; otherwise `high`. Do not read settings from historical slices, logs, or quoted examples. Accept only `low`, `medium`, `high`, `xhigh`, `max`; missing flag values, unknown flags, duplicate conflicting values at the selected scope, or an invalid selected value stop verification before any writes or spawn. A one-run override never changes the spec default or current-slice setting. `/bosun-mode --verifier-effort <level>` changes the project default.

Run `python3 "<plugin root>/scripts/configure-claude-agents.py" --project "<project root>" --mode <resolved Claude mode> --verifier-effort <resolved effort>` before spawning. Resolve the plugin root from this skill's location. This regenerates **both** project-local verifier definitions with real `effort` frontmatter and the selected model (`claude-opus-5-5` in `opus`, `claude-fable-5-1` in all Fable modes); it also refreshes the scout model and does not change the worker. Always regenerate on the next invocation, so a one-run override does not become a default. Stop on setup errors. Use the local `bosun-verifier` or `bosun-verifier-mobile`, never the plugin-scoped `bosun:...` definition (which would ignore the generated effort). Confirm the local agent is loaded at the requested effort; if the agents directory is new to the running session, restart Claude Code first. A conflicting model environment override or an unavailable agent/model is a blocker, not a reason to silently use another verifier. No lead-session effort change is needed.

Carry the resolved effort through FAIL retries unless the user explicitly changes it, including a one-run `--effort` override. Record each attempt's effective effort in its verdict and in the slice log; never label a prompt-only request as an applied effort setting. This setting is Claude-only; Codex verification continues to use its shipped agent effort.

## Steps

1. Assemble a self-contained prompt. The verifier cannot see this conversation, so include:
   - The spec path and which slice or done-conditions to judge. If there is no spec, the done-conditions verbatim from the user's arguments or reconstructed from the request; say which.
   - The out-of-scope list.
   - The base to diff against (branch or commit).
   - The exact check commands and any setup they need.
   - Anything the verifier would otherwise misjudge: intentional deviations and their reasons, environment quirks, known pre-existing failures with evidence that they predate the change.
   - When any done-condition names a route or web screen: the implementer's `Evidence:` list (route, viewport when named, what was checked, screenshot path) and the app's launch command. The verifier re-checks only those done-conditions in Playwright, at the named viewport width when one is specified.
   - When the brief says `Surface: ios`: the device name, build and install commands, bundle id, and the implementer's evidence lines (screen, device, what was checked, screenshot path).
   - The implementer's test and CI statements: each existing test changed, skipped, or deleted and the done-condition that requires it, and, when a CI workflow changed, whether it adds or removes CI time. Where the lead implemented, the lead states these; where a worker did, copy them from its report.
   - The resolved verifier model and effort.
   - In fable-opus mode: the worker is `bosun-worker-opus` (claude-opus-5-5/high). Return FAIL findings to that worker with the original brief; Fable never implements the fixes.
   - In fable-crew mode: the worker model and effort that produced the diff. FAIL findings then go back to the worker through `scripts/codex-worker.sh` (see `/bosun-brief`, "Fable-crew mode"), not to Fable.
2. When the brief says `Surface: ios`, launch the `bosun-verifier-mobile` agent with that prompt; otherwise launch `bosun-verifier`. While it runs, do not idle: draft the report, continue unrelated remaining work, or, under `Run policy: until blocked`, stage the next slice's brief as `/bosun-brief` ("Staged briefs") describes. Do not edit files the verifier is reading.
3. Relay the verdict faithfully. Do not soften a FAIL.
   - FAIL: in fable or opus mode the lead fixes each in-scope finding; in fable-crew or fable-opus return it to the same implementation worker. Then run this skill again at the same resolved verifier effort. After two FAILs on the same finding, stop and report both positions to the user. Out-of-scope findings go in the report as follow-ups.
   - PASS WITH FOLLOW-UPS: report the follow-ups; do not fix them unless the user asks.
   - PASS: report the verdict and the evidence lines. Screenshot paths the verifier reports are evidence; keep them in the report.
4. Record the verifier model and effective effort with the verdict and in the slice log. For each done-condition the verifier confirmed, mark it verified in the spec with a pointer to the evidence (commit, command, or file:line). Human-check conditions stay unverified and are listed for the user in the report.

Never let the verifier fix things, and never verify by re-reading your own work in this context; that is what the skill exists to avoid.
