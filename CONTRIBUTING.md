# Contributing to Bosun

Open an issue describing the host, Bosun version, provider mode, expected behavior, observed behavior, and a minimal reproduction. Redact tokens, account identifiers, private paths, and project content. Do not attach full worker logs without reviewing them.

For changes, keep Claude Code and Codex behavior aligned where the shared contract applies. Explain intentional host differences. Keep fixes scoped and preserve outstanding human checks in SPEC.md. Describe verification and its limits in the pull request.

## Local checks

Run from the repository root:

```bash
find scripts codex/scripts -name '*.sh' -exec bash -n {} \;
claude plugin validate .
git diff --check
bash scripts/codex-worker.sh --model gpt-5.6-sol --effort high --cwd "$PWD" --prompt-file /tmp/bosun-example-prompt.md --out-dir /tmp/bosun-example-output --dry-run
```

The worker dry run prints arguments without launching a model or requiring those example paths to exist. Validate JSON manifests and Codex agent TOML with a parser (Python 3.11+ provides json and tomllib). Installation discovery does not establish that every model, hook, browser check, or complete coding workflow works. Report live smoke checks separately, with host/version and mode.

Do not include private operational data or credentials in issues, fixtures, commits, or pull requests. For a suspected credential exposure, contact the repository owner privately rather than publishing the value in an issue.
