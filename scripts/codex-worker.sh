#!/bin/bash
# Run one implementation slice on an OpenAI Codex model through the user's own
# `codex exec` CLI. Owns every flag so the model never has to retype them.
#
#   codex-worker.sh --model <gpt-5.6-sol|gpt-5.6-luna> --effort <low|medium|high|xhigh|max>
#                   --cwd <worktree> --prompt-file <file> --out-dir <dir> [--network] [--dry-run]
#
# Writes into --out-dir:
#   events.jsonl      every `codex exec --json` event
#   last-message.md   the worker's final message
#   usage.json        model, effort, wall seconds, exit code, summed token usage
#
# --dry-run prints the exact argv and exits 0 without checking codex or spawning.
# Real runs preflight `codex --version` and `codex login status` and exit
# non-zero with the reason on failure; there is no fallback to another provider.
set -euo pipefail

model="" effort="" cwd="" prompt_file="" out_dir="" network=0 dry_run=0
while [ $# -gt 0 ]; do
  case "$1" in
    --model) model="$2"; shift 2 ;;
    --effort) effort="$2"; shift 2 ;;
    --cwd) cwd="$2"; shift 2 ;;
    --prompt-file) prompt_file="$2"; shift 2 ;;
    --out-dir) out_dir="$2"; shift 2 ;;
    --network) network=1; shift ;;
    --dry-run) dry_run=1; shift ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "codex-worker: unknown argument: $1" >&2; exit 2 ;;
  esac
done

for pair in "model:$model" "effort:$effort" "cwd:$cwd" "prompt-file:$prompt_file" "out-dir:$out_dir"; do
  if [ -z "${pair#*:}" ]; then echo "codex-worker: --${pair%%:*} is required" >&2; exit 2; fi
done

case "$model" in
  gpt-5.6-sol|gpt-5.6-luna) ;;
  *) echo "codex-worker: model '$model' is not in the routing table (gpt-5.6-sol, gpt-5.6-luna)" >&2; exit 2 ;;
esac
case "$effort" in
  ultra) echo "codex-worker: effort 'ultra' is banned: it auto-delegates, which fights the single-context slice design" >&2; exit 2 ;;
  low|medium|high|xhigh|max) ;;
  *) echo "codex-worker: effort '$effort' is not one of low, medium, high, xhigh, max" >&2; exit 2 ;;
esac

argv=(codex exec --json
  -m "$model"
  -c "model_reasoning_effort=\"$effort\""
  -C "$cwd"
  --approve-for-me   # implies the workspace-write sandbox; codex rejects an explicit -s alongside it
  --skip-git-repo-check
  --ephemeral
  -o "$out_dir/last-message.md")
if [ "$network" = 1 ]; then argv+=(-c "sandbox_workspace_write.network_access=true"); fi
argv+=(-)  # prompt is read from stdin

if [ "$dry_run" = 1 ]; then
  printf '%q ' "${argv[@]}"; printf '< %q\n' "$prompt_file"
  exit 0
fi

if [ ! -f "$prompt_file" ]; then echo "codex-worker: prompt file not found: $prompt_file" >&2; exit 2; fi
if [ ! -d "$cwd" ]; then echo "codex-worker: cwd not found: $cwd" >&2; exit 2; fi

# Preflight. No fallback: a missing or logged-out codex stops the slice.
if ! command -v codex >/dev/null 2>&1; then echo "codex-worker: codex CLI not on PATH" >&2; exit 3; fi
if ! codex --version >/dev/null 2>&1; then echo "codex-worker: codex --version failed" >&2; exit 3; fi
login="$(codex login status 2>&1 || true)"
case "$login" in
  *"Logged in"*) ;;
  *) echo "codex-worker: codex is not logged in: $login" >&2; exit 3 ;;
esac

mkdir -p "$out_dir"
start=$(date +%s)
set +e
"${argv[@]}" < "$prompt_file" > "$out_dir/events.jsonl"
code=$?
set -e
end=$(date +%s)

MODEL="$model" EFFORT="$effort" SECONDS_="$((end - start))" CODE="$code" OUT="$out_dir" python3 - <<'EOF'
import json, os
out = os.environ["OUT"]
tot = {"input_tokens": 0, "cached_input_tokens": 0, "cache_write_input_tokens": 0, "output_tokens": 0, "reasoning_output_tokens": 0}
seen = False
try:
    with open(os.path.join(out, "events.jsonl")) as f:
        for line in f:
            try: e = json.loads(line)
            except ValueError: continue
            if e.get("type") == "turn.completed" and isinstance(e.get("usage"), dict):
                seen = True
                for k in tot:
                    v = e["usage"].get(k)
                    if isinstance(v, (int, float)): tot[k] += int(v)
except FileNotFoundError:
    pass
usage = {"model": os.environ["MODEL"], "effort": os.environ["EFFORT"], "wall_seconds": int(os.environ["SECONDS_"]),
         "exit_code": int(os.environ["CODE"]), "usage": tot if seen else None}
with open(os.path.join(out, "usage.json"), "w") as f:
    json.dump(usage, f, indent=2); f.write("\n")
print(json.dumps(usage))
EOF

if [ ! -f "$out_dir/last-message.md" ]; then echo "codex-worker: no last message was written (exit $code)" >&2; fi
exit "$code"
