#!/bin/bash
# SessionStart hook for Bosun.
#   startup/resume/clear: load the core rules if they are not already in ~/.claude/CLAUDE.md,
#                         point at the project's spec (with its provider mode and run policy), and print any checkpoint.
#   compact: tell the model to re-read the spec before continuing.
dir="${CLAUDE_PROJECT_DIR:-$PWD}"
plugin_root="$(cd "$(dirname "$0")/.." && pwd)"
source_kind="$(python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("source","startup"))
except Exception: print("startup")' 2>/dev/null)"

spec=""
for candidate in "$dir/SPEC.md" "$dir/docs/SPEC.md" "$dir/docs/spec.md" "$dir/spec/SPEC.md"; do
  if [ -f "$candidate" ]; then spec="$candidate"; break; fi
done

if [ "$source_kind" = "compact" ]; then
  if [ -n "$spec" ]; then
    echo "Context was just compacted. Before continuing, re-read the spec at $spec and pick up the current slice from it."
  else
    echo "Context was just compacted. No spec file was found in $dir; if a task is in progress, restate its done-conditions before continuing."
  fi
  exit 0
fi

# Core rules: printed here unless the user has appended them to ~/.claude/CLAUDE.md (see README).
if ! grep -qs '^# Fable 5.1 agentic development' "$HOME/.claude/CLAUDE.md"; then
  cat "$plugin_root/rules/fable.md"
  echo
fi

slug="$(printf '%s' "$dir" | sed 's#^/##; s#[/ ]#-#g')"
file="$HOME/.claude/bosun/checkpoints/$slug.md"
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
    echo "Bosun spec for this project: $spec ($detail). Read it before starting substantial work."
  else
    echo "Bosun spec for this project: $spec. Read it before starting substantial work."
  fi
fi
if [ -f "$file" ]; then
  echo "A Bosun checkpoint exists for this project ($file, written $(date -r "$file" '+%Y-%m-%d %H:%M')). Read the spec, then this checkpoint, then continue from where it stops. Overwrite it with /bosun-checkpoint when you stop; delete it when the slice is finished."
  echo
  cat "$file"
fi
exit 0
