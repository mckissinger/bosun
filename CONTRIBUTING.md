# Contributing to Bosun

Open an issue describing the host, Bosun version, provider mode, expected behavior, observed behavior, and a minimal reproduction. Redact tokens, account identifiers, private paths, and project content. Do not attach full worker logs without reviewing them.

For changes, keep fixes scoped and preserve outstanding human checks in SPEC.md. Describe verification and its limits in the pull request.

## Local checks

Run from the repository root:

```bash
bash -n scripts/*.sh
claude plugin validate .
git diff --check
python3 scripts/configure-claude-agents.py --project "$PWD" --mode opus --dry-run
```

The agent-setup dry run validates and prints its targets without writing. Validate the JSON manifests with a parser. Installation discovery does not establish that every model, hook, browser check, or complete coding workflow works. Report live smoke checks separately, with host/version and mode.

Do not include private operational data or credentials in issues, fixtures, commits, or pull requests. For a suspected credential exposure, contact the repository owner privately rather than publishing the value in an issue.
