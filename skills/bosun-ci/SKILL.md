---
name: bosun-ci
description: Audit or improve GitHub Actions CI performance and reliability using workflow files and run evidence. Use for slow CI, wasted runner time, flaky checks, CI optimization requests, turning on a merge queue, or setting up a migrations workflow. Audit requests produce findings; improvement requests implement a focused change through Bosun and verify coverage and measured results.
---

# Bosun CI

Shorten time to trustworthy CI results while preserving coverage. V1 supports GitHub Actions. For another provider, explain that limit and offer a provider-specific follow-up; do not rewrite its configuration as GitHub Actions.

## Select the outcome

- **Audit CI**, review, or recommendations: read-only investigation and a ranked report. Do not edit the spec or workflows, launch runs, or invoke the implementation flow. A spec is useful context but not required for an audit.
- **Speed up CI**, optimize, or fix an identified CI bottleneck: investigate, then implement a focused improvement through `/bosun-brief` and verify through `/bosun-verify`. Honor existing authorization; do not insert another approval step when implementation is already requested. The brief's provider-mode, spec, routing, and run-policy rules still apply.
- **Turn on a merge queue** or **set up migrations**: when the user asks by name, follow that section below, through `/bosun-brief` and `/bosun-verify` for its code.
- If the request does not establish whether to edit, default to audit. Keep deployment changes and repository protection changes, including turning on a merge queue and the migrations flow below, outside a CI performance request unless separately requested. A move to Blacksmith runners is always a recommendation under "Runner standard"; implement it only when the user asked for the migration.

## Establish the baseline

Read `.github/workflows/`, referenced reusable workflows and local actions, package/build configuration, and the actual check commands. Inspect remote reusable workflows at the referenced revision when accessible. Map triggers, matrix variants, `needs` dependencies, conditions, required checks, permissions, and shared artifacts before proposing removals or skipped work. If protection settings or referenced code are inaccessible, state what is unknown.

Read the default branch's merge setup with `gh api` (branch protection or rulesets: required checks, whether branches must be up to date before merging, and whether a merge queue is on). Requiring up-to-date branches without a merge queue is a finding, because each merge leaves the other open PRs behind and auto-merge does not update them (core rules, "Merge flow"); recommend a merge queue where GitHub offers one, and otherwise turning the requirement off with CI on pushes to the default branch. Under a merge queue, a required workflow without a `merge_group` trigger never reports, so queued PRs hang, and a job that reads a PR number (such as a changed-files gate on `pulls/{n}/files`) with no `merge_group` fallback that runs everything fails or skips in the queue: report either as a blocking finding. The one exception is a check that only makes sense on a PR's diff and reports success in the queue, as "Turning on a merge queue" describes. A repository in a personal account, or a private organization repository without GitHub Enterprise Cloud, cannot have a queue: say so, and leave any move or plan change to the user.

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

## Turning on a merge queue

Do this when the user asked for it, one repository at a time. A queue earns its cost where PRs pile up, or where affected-only tests need a required full run before merge. Each queued PR runs the full required checks on top of the entries ahead of it, so a repository with little PR traffic can wait.

1. **Workflows first, in an ordinary PR.** Every required check's workflow triggers on `merge_group`, and any job that reads a PR number or diff gets a fallback that runs everything. A required check that only makes sense on a PR's diff, such as a security review, reports success on `merge_group`, because a PR enters the queue only after its own required checks pass; state that in the coverage justification.
2. **Merge that PR,** then confirm the trigger is on the default branch. Turning the queue on before this leaves queued PRs waiting on a check that never arrives.
3. **Turn the queue on.** Create a ruleset for the default branch with a `merge_queue` rule (`POST repos/{owner}/{repo}/rulesets`, repository admin), or have an admin tick Require merge queue in classic branch protection. A ruleset's queue works alongside classic protection that holds the required checks. Starting values, to adjust from measured runs (a classic setup may offer fewer of them, which step 4's read-back shows):
   - merge method: the one the project merges with, such as `MERGE` for merge commits (the queue sets it, and `gh pr merge --auto --merge` only notes that);
   - grouping: all entries must pass (`ALLGREEN`);
   - minimum group 1, maximum group 5, wait 5 minutes;
   - build concurrency 2 where each entry's full suite is expensive, raised only after measuring;
   - check timeout above the full run's slowest recent time, with room for retries.
4. **Prove it with one low-risk PR.** Confirm a `merge_group` run reports every required check, the PR merges, and the configuration reads back through GraphQL (`mergeQueue(branch:) { configuration { ... } }`, which reports times in seconds where the ruleset takes minutes). Record the real settings where the project keeps its CI notes, read back rather than remembered.

To undo it, remove the rule or untick the setting; the `merge_group` trigger is harmless on its own. If a path gate relies on the queue's full run, restore full runs on PRs first, or selection misses land on the default branch.

## Choose a change

Rank opportunities by evidence, expected elapsed-time or runner-minute benefit, implementation effort, and coverage risk. Look at the critical path first: a gate job that other jobs `needs` delays every job waiting behind it, so a few seconds there can shorten elapsed time more than larger savings elsewhere. Setup often outweighs test execution; when the baseline shows that, cut setup before adding parallelism. Explain the tradeoff if parallelism reduces elapsed time but increases compute. Do not promise a percentage from workflow inspection alone.

Investigate only candidates supported by the bottleneck, for example:

- Dependency/build caches: confirm hit rates, invalidation inputs, and restore/save overhead, and compare restore time with a fresh filtered install; a cache keyed on a frequently changing lockfile can be slower than reinstalling. Preserve correctness on a cold cache; caches must not be the only way required outputs arrive.
- Repeated builds: build once and pass revision-matched artifacts to consumers where environments and configurations are compatible.
- Identical-input reruns: skip a task whose inputs match a run that already passed, through a task or remote cache keyed on those inputs, so a rebase or re-verify reruns only what changed. It is safe only for hermetic tasks: the key must cover every input the task reads, including environment variables and tool versions. Leave uncached any task that reaches live services, reads the clock, or has shown flakes, since its result can change with identical inputs and cached passes hide the reruns that flake evidence depends on.
- Gate jobs: a shallow or sparse fetch for change detection, no checkout in jobs that do not read the tree, and cache writes or housekeeping moved to a job nothing waits on.
- Repeated setup: a base image for stable system dependencies (which also removes downloads that can hang), installs filtered to the package a job needs rather than the whole workspace, and a generated schema snapshot instead of replaying every migration.
- Playwright's OS packages: `playwright install --with-deps` goes through the runner's apt mirror, which can crawl and can fail a required check for reasons unrelated to the code. On Blacksmith, point apt at `archive.ubuntu.com` before any apt install, in `/etc/apt/apt-mirrors.txt` and `ubuntu.sources` (editing `sources.list` alone does nothing). Where it is still slow, cache the `.deb` files: remove apt's `docker-clean` config, copy the cache into `/var/cache/apt/archives` before installing, and save it from one shard only when new files appeared. Mark the cache steps `continue-on-error`, so a cache problem never fails a shard and a cold cache behaves as before.
- Small checks: batch lint, format, typecheck, and audit into one or two jobs that run them concurrently, grouped by cost, keeping per-task output so a failure still names its script.
- Tooling: a native typechecker where the project's TypeScript supports it (`tsgo`), and lint rules that do not need type information unless they must.
- Job ordering: remove unnecessary `needs` dependencies.
- Test sharding, only after per-shard setup is short: multiply setup time by the shard count before adding shards, balance with observed timings, and split oversized test files, since runners such as Vitest balance by file rather than by test duration. Judge a balancing or runner-size change on a real run against recent medians rather than its prediction, keep it only for a clear gain, and record what was tried and not adopted, with its numbers, in the spec so it is not tried again.
- Test isolation: letting test files share a module registry (Vitest `isolate: false`) through an explicit per-file opt-in with teardown for shared state, leaving files with fake timers or tangled shared state in an isolated project. Highest reward and highest correctness risk; never enable it globally.
- Superseded PR runs: scope cancellation to the same PR/workflow where safe; keep release/deployment semantics intact.
- Duplicate triggers, broad matrices, and change-based selection (affected-only tests): justify what becomes conditional and how all affected components and supported environments retain coverage, with a full run for shared or configuration changes and on a schedule. When PRs merge automatically on green, a scheduled or post-merge full run finds a selection miss only after it lands, so anything the PR run skips must still run in a required check before merge, such as the full suite in a merge queue. On the PR run itself, keep end-to-end tests full or path-gated, since the import graph cannot select them. A path gate that stays honest: a script maps changed files to a scope, where documentation and unit tests run no end-to-end tests (the check still reports success, so a required check never hangs), a changed spec runs that spec, a change inside a closed area runs that area's specs, and anything else runs the full suite, including shared code, configuration, dependencies, migrations, test helpers, the workflow and the script itself. A test fails when a mapped area gains an outside importer or a spec naming one of its routes is missing from its list, so the map cannot quietly go stale. The queue and pushes to the default branch run the full suite, and the run summary says which scope ran and why.
- Flaky checks: address an evidenced cause rather than increasing retries or turning failures into successes.
- Flake quarantine, with the user's approval (core rules, "Tests and CI"): a flaky end-to-end test keeps running without blocking while it is fixed. Each quarantined test carries a tag and an entry with its owner, reason, date added, and an expiry at most 14 days out. Blocking runs exclude the tag, and a non-blocking step still runs those tests. A test in a required check fails on an expired or over-long entry, a missing owner or reason, or tags and entries that do not match, counting tags the way the test runner matches them. That test reads today's date on purpose, an exception to the no-wall-clock rule for new tests; say so in the verify prompt. An expired entry therefore blocks PRs until someone fixes the test or renews it with a new reason. Keep the list short, since the extra step adds time to every shard.
- Nightly flake hunt: a scheduled run on the default branch, in its own workflow so it is not read as the default branch's CI, repeats every test (Playwright's `--repeat-each=2`), quarantined ones included, gates nothing, and posts a table of flaky and failed tests to one standing issue. It says when shard reports are missing, so a broken night does not look clean, and it gives flake candidates the rate evidence a fix needs.

Prefer a small coherent change with a measurable hypothesis. If the evidence shows no worthwhile improvement, report that and stop. Put other candidates in the report; during implementation, record deferred candidates in the spec's follow-ups.

## Migrations deploy (opt-in)

Set this up when the user asks, as its own slice, since it deploys. A workflow applies committed migrations after CI passes on the default branch, on the commit CI tested. The project's spec records its production mode, in the user's words.

Every setup has these guards:

- **Trigger.** The triggering run's event is `push` and its branch is the default branch. A branch-name check alone matches a fork's branch of the same name, and a CI workflow that also runs on a schedule would otherwise fire it. A hand start runs only from the default branch. CI must therefore also run on `push` to the default branch, even under a merge queue, or this workflow silently never fires.
- **Environments.** Each database has its own GitHub Environment holding its secret, with deployment branches limited to the default branch. Mask secrets in anything the job prints.
- **Order.** Where a project has a sandbox, it updates first and production runs only after it succeeds. A failed sandbox stops production.
- **One at a time.** One push per database, never cancelled half-way (`concurrency` with `cancel-in-progress: false`).
- **Dry runs.** A dry run lists pending migrations in the job summary, and a second one after pushing confirms nothing is left. A database ahead of the default branch is a green no-op with a warning that names the versions, and production does not run while sandbox is ahead. Any other dry-run error fails red.
- **Holds.** A migration that must not ship before a date refuses the whole push, because applying the others around it is an order nobody checked.
- **App and migration order.** The app may deploy on merge while the migration waits for CI, and for approval where that applies, so decide per change. Where the migration needs the app, merge the app first. Where the app needs the migration, plan for the gap, or have the user apply the migration before merging, sandbox first.

Production takes one of two modes:

- **Approval.** Recommended once a project has real users or money. Production's environment has a required reviewer with admin bypass off, runs only when sandbox just took migrations, or with a single database when its own dry run finds pending migrations, or when started by hand, and refuses to push if the environment has no required reviewer. Approving is the user's. A session never approves it, even when its `gh` login is the reviewer, so this rests on the rule rather than a technical block.
- **Automatic.** Only by the user's explicit choice, typically before launch or with no real data, where a bad migration is cheap to undo. Production updates after CI with no approval, and the guards above still apply.

## Implement through Bosun

For improvement requests, give `/bosun-brief` the selected outcome, baseline evidence, affected workflow/checks, expected benefit, and coverage invariants. Add these CI-specific done-conditions to the slice, scaled to the change:

- Required checks and supported test environments still execute for applicable events, and check names consumed by repository rules remain valid.
- Every removed or conditional check has an explicit coverage justification. Path selection accounts for shared dependencies, lockfiles, workflow changes, and merge-queue events when used. Check both matching and nonmatching changes; a skipped workflow must not leave a required check pending indefinitely.
- Shards/matrices collectively retain the intended tests. Required failures still make CI fail: inspect `continue-on-error`, shell exit propagation, conditions, and any aggregate gate's handling of failed, cancelled, or unexpectedly skipped jobs.
- Changed caches/artifacts preserve compatibility, invalidation, and trust boundaries. Do not broaden token permissions or expose secrets to make an optimization work.
- The before/after comparison uses a stated method and evidence, or explicitly remains unmeasured pending hosted runs.
- An optimization that constrains how code or tests are written (an isolation opt-in, batched check jobs, what belongs in the base image, filtered installs) is recorded where the project's agents read it: its CLAUDE.md or AGENTS.md, or the spec's lessons. Otherwise later agents write code that quietly falls off the fast path.

Use the repo's existing checks and suitable workflow validation tools when available. A YAML parse is only a syntax check, not proof that GitHub will schedule jobs correctly. Exercise relevant event/condition cases and cold-cache behavior when the change depends on them. Bound experiments to the comparison needed; do not repeatedly rerun until a favorable result appears. Respect the request's scope for pushes and workflow dispatches, including any release side effects.

## Verify and report

Provide `/bosun-verify` with the diff base, baseline and candidate run URLs/attempts, exact validation commands, coverage mapping, and any unavailable evidence. Its independent review checks both preserved behavior and the claimed improvement. Keep correctness status separate from performance status: local checks passing cannot establish hosted speedup.

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
