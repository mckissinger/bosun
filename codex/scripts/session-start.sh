#!/bin/bash
# SessionStart hook for the Fable harness Codex plugin.
#   Emits additionalContext JSON: the core rules unless ~/.codex/AGENTS.md already carries them,
#   the project's spec path with its provider mode and run policy, and any checkpoint.
#   On compaction, tells the model to re-read the spec.
plugin_root="${PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
input="$(cat 2>/dev/null)"
source_kind="$(printf '%s' "$input" | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("source","startup"))
except Exception: print("startup")' 2>/dev/null)"
dir="$(printf '%s' "$input" | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("cwd",""))
except Exception: print("")' 2>/dev/null)"
dir="${dir:-${CODEX_PROJECT_DIR:-$PWD}}"

spec=""
for candidate in "$dir/SPEC.md" "$dir/docs/SPEC.md" "$dir/docs/spec.md" "$dir/spec/SPEC.md"; do
  if [ -f "$candidate" ]; then spec="$candidate"; break; fi
done

out=""
if [ "$source_kind" = "compact" ]; then
  if [ -n "$spec" ]; then
    out="Context was just compacted. Before continuing, re-read the spec at $spec and pick up the current slice from it."
  else
    out="Context was just compacted. No spec file was found in $dir; if a task is in progress, restate its done-conditions before continuing."
  fi
else
  if ! grep -qs '^# Astra agentic development' "$HOME/.codex/AGENTS.md"; then
    out="$(cat "$plugin_root/rules/astra.md")"$'\n\n'
  fi
  if [ -n "$spec" ]; then
    mode="$(grep -m1 '^Provider mode:' "$spec" 2>/dev/null | sed 's/^Provider mode:[[:space:]]*//')"
    policy="$(grep -m1 '^Run policy:' "$spec" 2>/dev/null | sed 's/^Run policy:[[:space:]]*//')"
    detail=""
    [ -n "$mode" ] && detail="provider mode: $mode"
    if [ -n "$policy" ]; then
      [ -n "$detail" ] && detail="$detail, "
      detail="${detail}run policy: $policy"
    fi
    if [ -n "$detail" ]; then
      out="${out}Fable spec for this project: $spec ($detail). Read it before starting substantial work."
    else
      out="${out}Fable spec for this project: $spec. Read it before starting substantial work."
    fi
  fi
  slug="$(printf '%s' "$dir" | sed 's#^/##; s#[/ ]#-#g')"
  file="$HOME/.codex/fable/checkpoints/$slug.md"
  if [ -f "$file" ]; then
    out="${out}"$'\n'"A Fable checkpoint exists for this project ($file, written $(date -r "$file" '+%Y-%m-%d %H:%M')). Read the spec, then this checkpoint, then continue from where it stops. Overwrite it with \$fable-checkpoint when you stop; delete it when the slice is finished."$'\n\n'"$(cat "$file")"
  fi
fi

OUT="$out" python3 - <<'PY'
import json, os
text = os.environ.get("OUT", "")
if text.strip():
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}))
PY
exit 0
