---
name: bosun-ci
description: Audit or improve GitHub Actions CI performance and reliability using workflow files and run evidence. Use for slow CI, wasted runner time, flaky checks, or CI optimization requests. Audit requests produce findings; improvement requests implement a focused change through Bosun and verify coverage and measured results.
---

# Bosun CI (Codex)

Shorten time to trustworthy CI results while preserving coverage. V1 supports GitHub Actions. For another provider, explain that limit and offer a provider-specific follow-up; do not rewrite its configuration as GitHub Actions.

## Select the outcome

- **Audit CI**, review, or recommendations: read-only investigation and a ranked report. Do not edit the spec or workflows, launch runs, or invoke the implementation flow. A spec is useful context but not required for an audit.
- **Speed up CI**, optimize, or fix an identified CI bottleneck: investigate, then implement a focused improvement through `$bosun-brief` and verify through `$bosun-verify`. Honor existing authorization; do not insert another approval step when implementation is already requested. The brief's provider-mode, spec, routing, and run-policy rules still apply.
- If the request does not establish whether to edit, default to audit. Keep deployment changes and repository protection changes outside a CI performance request unless separately requested. A move to Blacksmith runners is always a recommendation under "Runner standard"; implement it only when the user asked for the migration.

## Establish the baseline

Read `.github/workflows/`, referenced reusable workflows and local actions, package/build configuration, and the actual check commands. Inspect remote reusable workflows at the referenced revision when accessible. Map triggers, matrix variants, `needs` dependencies, conditions, required checks, permissions, and shared artifacts before proposing removals or skipped work. If protection settings or referenced code are inaccessible, state what is unknown.

Use available authenticated GitHub tooling or the user's exported run data. With `gh`, useful read-only entry points are `gh run list`, `gh run view <run-id>`, and the Actions jobs API for job/step timestamps. Consult current official GitHub documentation for API fields, workflow syntax, and action versions before changing them. Paginate job listings so large matrices are not silently truncated; identify run attempts when examining reruns. Never print credentials or indiscriminately dump logs that may contain secrets.

Choose a bounded sample of recent, comparable completed runs; aim for several observations rather than treating one fast run as typical. Record workflow, commit, event, branch, runner type, matrix, run attempt, conclusion, and run URL. Separate successful runs from failed, cancelled, and rerun attempts. Missing access or history still permits a static audit; mark its findings as hypotheses and performance as unmeasured.

Separate these quantities where the data supports them:

- **Elapsed time:** event/run creation to the required CI checks completing. State the exact interval measured and any omitted scheduling delay. With multiple required workflows, use their combined completion boundary, not only the fastest workflow.
- **Queue and execution:** distinguish runner waiting from dependency waiting and work on a runner. If timestamps cannot separate them, report the combined delay without attributing a cause.
- **Runner minutes:** sum job execution durations, including matrix jobs and retries. This is compute use, not a dollar-cost estimate; pricing and runner multipliers need separate evidence.
- **Step time:** setup/install, build, tests, artifact/cache transfer, and other dominant work. Follow the dependency chain that actually determines completion; parallel job durations do not add up to elapsed time.
- **Reliability:** identify repeat failures and retries with evidence. A failure that passes on rerun is a flake candidate, not proof; check for code and environment changes.

Record sample size, typical duration (median when meaningful), spread, and warm/cold/unknown cache state. Do not infer a cache hit from a fast install alone. Use tail percentiles only when the sample supports them.

## Runner standard

Blacksmith runners are the standard for GitHub Actions. A job on a GitHub-hosted runner is a finding: recommend its Blacksmith equivalent (for example, `ubuntu-latest` becomes a 2 vCPU Ubuntu Blacksmith runner) and size each job from its measured duration and resource use, with small checks on 2 vCPU and builds and heavy test shards on 4 to 8. Confirm runner labels, sizes, and cache actions against Blacksmith's current documentation before writing them; use its co-located cache actions where its migration tooling adds them. Blacksmith works only for repositories in a GitHub organization whose Default runner group includes the repository; for a personal repository, say that instead of recommending it.

Faster runners can introduce new failure modes. After a migration, compare checkout duration with the baseline and look for hung or retried checkouts. Linear saw checkout slow down and occasionally hang after leaving GitHub-hosted runners, from the network between the new runners and GitHub, and fixed it with retry-with-backoff, low-speed git timeouts, and cached git mirrors.

## Choose a change

Rank opportunities by evidence, expected elapsed-time or runner-minute benefit, implementation effort, and coverage risk. Look at the critical path first: a gate job that other jobs `needs` delays every job waiting behind it, so a few seconds there can shorten elapsed time more than larger savings elsewhere. Setup often outweighs test execution; when the baseline shows that, cut setup before adding parallelism. Explain the tradeoff if parallelism reduces elapsed time but increases compute. Do not promise a percentage from workflow inspection alone.

Investigate only candidates supported by the bottleneck, for example:

- Dependency/build caches: confirm hit rates, invalidation inputs, and restore/save overhead, and compare restore time with a fresh filtered install; a cache keyed on a frequently changing lockfile can be slower than reinstalling. Preserve correctness on a cold cache; caches must not be the only way required outputs arrive.
- Repeated builds: build once and pass revision-matched artifacts to consumers where environments and configurations are compatible.
- Gate jobs: a shallow or sparse fetch for change detection, no checkout in jobs that do not read the tree, and cache writes or housekeeping moved to a job nothing waits on.
- Repeated setup: a base image for stable system dependencies (which also removes downloads that can hang), installs filtered to the package a job needs rather than the whole workspace, and a generated schema snapshot instead of replaying every migration.
- Small checks: batch lint, format, typecheck, and audit into one or two jobs that run them concurrently, grouped by cost, keeping per-task output so a failure still names its script.
- Tooling: a native typechecker where the project's TypeScript supports it (`tsgo`), and lint rules that do not need type information unless they must.
- Job ordering: remove unnecessary `needs` dependencies.
- Test sharding, only after per-shard setup is short: multiply setup time by the shard count before adding shards, balance with observed timings, and split oversized test files, since runners such as Vitest balance by file rather than by test duration.
- Test isolation: letting test files share a module registry (Vitest `isolate: false`) through an explicit per-file opt-in with teardown for shared state, leaving files with fake timers or tangled shared state in an isolated project. Highest reward and highest correctness risk; never enable it globally.
- Superseded PR runs: scope cancellation to the same PR/workflow where safe; keep release/deployment semantics intact.
- Duplicate triggers, broad matrices, and change-based selection (affected-only tests): justify what becomes conditional and how all affected components and supported environments retain coverage, with a full run for shared or configuration changes and on a schedule.
- Flaky checks: address an evidenced cause rather than increasing retries or turning failures into successes.

Prefer a small coherent change with a measurable hypothesis. If the evidence shows no worthwhile improvement, report that and stop. Put other candidates in the report; during implementation, record deferred candidates in the spec's follow-ups.

## Implement through Bosun

For improvement requests, give `$bosun-brief` the selected outcome, baseline evidence, affected workflow/checks, expected benefit, and coverage invariants. Add these CI-specific done-conditions to the slice, scaled to the change:

- Required checks and supported test environments still execute for applicable events, and check names consumed by repository rules remain valid.
- Every removed or conditional check has an explicit coverage justification. Path selection accounts for shared dependencies, lockfiles, workflow changes, and merge-queue events when used. Check both matching and nonmatching changes; a skipped workflow must not leave a required check pending indefinitely.
- Shards/matrices collectively retain the intended tests. Required failures still make CI fail: inspect `continue-on-error`, shell exit propagation, conditions, and any aggregate gate's handling of failed, cancelled, or unexpectedly skipped jobs.
- Changed caches/artifacts preserve compatibility, invalidation, and trust boundaries. Do not broaden token permissions or expose secrets to make an optimization work.
- The before/after comparison uses a stated method and evidence, or explicitly remains unmeasured pending hosted runs.
- An optimization that constrains how code or tests are written (an isolation opt-in, batched check jobs, what belongs in the base image, filtered installs) is recorded where the project's agents read it: its CLAUDE.md or AGENTS.md, or the spec's lessons. Otherwise later agents write code that quietly falls off the fast path.

Use the repo's existing checks and suitable workflow validation tools when available. A YAML parse is only a syntax check, not proof that GitHub will schedule jobs correctly. Exercise relevant event/condition cases and cold-cache behavior when the change depends on them. Bound experiments to the comparison needed; do not repeatedly rerun until a favorable result appears. Respect the request's scope for pushes and workflow dispatches, including any release side effects.

## Verify and report

Provide `$bosun-verify` with the diff base, baseline and candidate run URLs/attempts, exact validation commands, coverage mapping, and any unavailable evidence. Its independent review checks both preserved behavior and the claimed improvement. Keep correctness status separate from performance status: local checks passing cannot establish hosted speedup.

Compare runs with the same workflow scope, runner class, event, matrix, and equivalent workload; ideally use the same source workload apart from the CI change. Separate warm and cold caches and disclose unavoidable differences. Report sample counts and variation; if evidence is sparse or confounded, say so. Do not exclude failures or retries from the reliability/compute accounting to improve the result.

Deliver:

1. Main bottleneck and evidence.
2. Ranked recommendations for an audit, or the implemented change and coverage justification for an improvement.
3. Before/after elapsed time, runner minutes, and reliability observations where available; label each result measured, estimated, or unmeasured.
4. Validation evidence, limitations, and deferred work. In implementation mode, record durable findings in the existing spec and slice log; keep measurement-dependent conditions pending until evidence exists.

## References

Use current official documentation as needed; avoid embedding action versions or API schemas in this skill:

- [GitHub Actions workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [Actions workflow jobs API](https://docs.github.com/en/rest/actions/workflow-jobs)
- [Dependency caching](https://docs.github.com/en/actions/concepts/workflows-and-actions/dependency-caching)
- [Workflow concurrency](https://docs.github.com/en/actions/concepts/workflows-and-actions/concurrency)
- [Blacksmith quickstart](https://docs.blacksmith.sh/introduction/quickstart)
- [Linear: AI coding has made CI a bottleneck, so we reworked ours to keep up](https://linear.app/now/ci-bottleneck-reworked) (the source of the gate, setup, batching, sharding, isolation, and checkout lessons above)
