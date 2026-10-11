---
name: bosun-preflight
description: Audit a feature-complete app for production readiness before launch, across security, abuse and cost guardrails, reliability, legal and data, product polish, operations, and native mobile. Use when an app is nearly done, before a launch or beta, or when the user asks "is this ready for production", "preflight", or "harden this app". Audit requests produce a ranked, evidence-backed punch list; fix requests implement chosen findings through Bosun and verify them.
---

# Bosun preflight (Codex)

Find what would hurt users, the owner, or the bill once real people use the app, and prove each finding with evidence. The audit covers the whole app as it stands, not a diff.

## Select the outcome

- **Audit** (the default), readiness review, or "is this ready": read-only investigation and a ranked report. Do not edit code, configuration, hosted settings, or workflows, and do not invoke the implementation flow. The one write allowed is the Production preflight record in the project's existing spec (see "Report"); with no spec, the report is the record.
- **Fix** chosen findings, "fix the blockers", or "harden it": implement them through `$bosun-brief` and verify through `$bosun-verify`, as "Fix mode" describes. Honor existing authorization; do not insert another approval step when the user already asked for the fixes. The brief's provider-mode, spec, routing, and run-policy rules still apply.

If the request does not say whether to edit, audit. Settings that live only in a provider's dashboard (spend caps, backups, domain records, store listings) are never changed here; they go in the report as manual steps for the user.

## Establish scope

- **Launch target:** public launch, private beta, or internal use. If the user does not say, assume a public launch and state that in the report. The target changes severity (see "Severity"), not which areas are checked.
- **Surfaces:** web app, API, background jobs, inbound webhooks, email and SMS, and native mobile apps. Check every surface the repo contains.
- **Stack:** detect it from the repo, not from memory: package manifests and lockfiles, framework config, database migrations and policies, deployment config, mobile build config, and the provider SDKs in use (payments, email, SMS, AI, jobs, analytics, error tracking). Name the stack in the report.
- **Prior knowledge:** read the spec, including its lessons and decisions, and any lessons store the user's instructions name. A lesson about a past defect in this stack is a check to run here.

Batch the reads. Independent areas can go to `bosun_scout` in the background while you work through others.

## Evidence and safety

- Every finding cites evidence: a file and line, a command and its output, or a browser observation with the URL and what was seen. A suspicion you could not confirm goes under "Unknown", with the check that would settle it, never under findings.
- Use the tools the project already has: its typecheck, lint, and tests that touch no live provider (read the test configuration first; a suite that would call real payment, email, SMS, or AI services is skipped and listed under "Unknown"); its dependency audit (`npm audit`, `pnpm audit`, or the equivalent); provider advisors when a provider offers them (for example the Supabase security and performance advisors); and a browser on a local production build or a preview deployment. Check cookies and page source on a production build, since development servers differ in exactly those places. Check response headers on a preview deployment or in the host's header configuration (for example `vercel.json` or a `_headers` file), because hosts add some headers at the edge that a local build never sends.
- Never read or print a secret value. Do not open `.env` files that hold values or print environment variables; take variable names from example files such as `.env.example`, or from tooling that lists names only.
- Make no calls that cost money, send email or SMS, or change production data. Do not load-test or probe production; probes run against local or preview environments. A plain unauthenticated request for a public production page, to read its headers, is allowed, and so is reading a hosted provider's settings or advisors where the session has access.
- Before running any flow that writes, confirm from variable names, configuration, or the service hosts the build calls that it talks to local or preview services, not production. If that cannot be confirmed, do not run write flows; list them under "Unknown".
- If a hosted setting cannot be read (backups, spend caps, branch protection), list it under "Unknown" with where the user can check it.

## Severity

- **Blocker:** must be fixed before the launch target. Data exposed to the wrong user, an authentication or authorization bypass, spend an outsider can drive without limit, data loss with no recovery path, a legal requirement for the target audience, or a store-policy violation that will be rejected.
- **Should fix:** likely to hurt within the first weeks of real use: missing error tracking, no timeouts, broken empty or error states, missing rate limits on cheaper endpoints.
- **Later:** worth doing, with low near-term risk.

A private beta or internal launch may lower reliability, product polish, and operations findings by one level; say which. It never lowers an access-control or data-exposure, abuse and cost, store-policy, or legal finding, or data loss with no recovery path: those hurt beta users as much as anyone, and a legal requirement is already judged against the launch audience.

## Areas and checks

Check each area that applies. These are the minimum; follow the evidence further when something looks wrong.

### Access control and data exposure

- Every table or collection holding user data has row-level access rules, and tests prove both the allowed case and the denied case, including another tenant's or another user's rows.
- Privileged keys (service role, secret API keys) are used only in server code. Client-exposed build-time variables (`NEXT_PUBLIC_*`, `EXPO_PUBLIC_*`, `VITE_*`) carry no secrets, since they are inlined into the shipped bundle.
- Database functions that run with elevated privileges are not reachable through an auto-generated API (for example a `SECURITY DEFINER` function in Supabase's exposed `public` schema becomes a callable RPC).
- Authentication and authorization decisions are made on the server from verified tokens, never from client-editable session contents such as a decoded cookie's claims or factor list.
- Gate pages (login, access code, consent, paywall) ship no protected data before the check passes. Check the page source and serialized component props, not only what is visible.
- Redirect targets are validated after URL normalization, so inputs like `/.//evil.com` or `/%2e//evil.com` cannot become an off-site redirect.
- Session cookies carry `HttpOnly`, `Secure`, and `SameSite`, read from the real `Set-Cookie` headers of a production build; some auth libraries leave `HttpOnly` off unless it is set explicitly. Where the library's browser client reads the cookie by design, report a missing `HttpOnly` as a tradeoff (session theft through any script injection) with the library's supported option, not as a flag to add, since adding it can break browser sign-in.
- Inbound webhooks verify the provider's signature, reject stale or replayed deliveries, and handle the same delivery twice without double effects.
- Input is validated where it enters the system; file uploads limit type and size and are readable only by their owners.
- Security headers are present on a production response (content security policy, HSTS, frame protection).
- The dependency audit has no exploitable critical or high vulnerability in shipped code.

### Abuse and cost guardrails

- Rate limits on sign-in, sign-up, password reset, one-time codes, and every endpoint that spends money: AI calls, SMS, email, uploads, and expensive queries.
- Per-user quotas on metered features, and provider-side spend caps or alerts (listed as a manual step when only the dashboard can set them).
- Outbound messages cannot be sent to arbitrary recipients an outsider supplies (SMS pumping, email relay).
- AI endpoints bound input size and output tokens; agents with tools cannot be steered by user-supplied content into actions the user could not take directly.
- Sign-up has bot protection when the app grants anything valuable at sign-up.

### Reliability

- Error tracking is wired on server and client, with alerts reaching someone.
- Outbound calls, AI calls included, have explicit timeouts sized to the slowest normal call; retries distinguish a temporary rate limit from an exhausted quota, which is not retried.
- Webhook and job handlers are idempotent, and jobs retry with a limit.
- Work started after a durable commit (enqueueing a job, sending a notification) cannot fail the request that already committed.
- Reads that can match more rows than a provider's response cap paginate instead of silently returning a truncated result.
- Backups or point-in-time recovery are enabled, and a restore path is known.
- Pending migrations are safe on production-sized data (locks, backfills, destructive changes).
- A health or uptime check covers the primary route.

### Legal and data

- Privacy policy and terms are reachable from the app; cookie consent exists where the audience's region requires it.
- Users can delete their account and data, and export it where required.
- Email has working unsubscribe for non-transactional mail and sender authentication (SPF, DKIM, DMARC) on the sending domain.
- Payments: receipts, refund handling, tax settings, and no test keys or test prices in production configuration.
- Third-party processors that receive user data are named in the privacy policy.

### Product polish

- Primary flows have empty, loading, and error states, and the app has real not-found and server-error pages.
- No placeholder text, test data, debug banners, or development-only routes ship.
- Transactional email templates are finished and render.
- Metadata: page titles and descriptions, social preview image, favicon, sitemap, and robots rules, with non-production environments not indexed.
- Basic accessibility on primary flows: labeled inputs, keyboard access, readable contrast.
- Primary routes load acceptably on a production build (Core Web Vitals or the framework's equivalent).

### Operations

- Production configuration is complete and separate from development: every required variable name is present for production, and no localhost or test endpoints remain.
- Preview and staging environments are protected or hold no real data.
- There is a rollback path for a bad deploy and for a bad migration.
- Someone can look up a user's problem without database console access.
- Logs carry no secrets or unnecessary personal data.

### Native mobile

- Store policy, checked against the current App Store Review Guidelines and Google Play policies: in-app account deletion when the app lets users create accounts, plus a web link for deletion requests on Google Play; an equivalent privacy-focused sign-in option when the app offers third-party sign-in on iOS (Sign in with Apple satisfies it); a privacy manifest and accurate App Store privacy labels; an accurate Google Play Data safety form; and purpose strings for every permission.
- Release builds use production endpoints and contain no development menus or debug flags; over-the-air update channels keep development and production apart.
- Tokens live in secure storage, and deep links validate their parameters before acting.
- Crash reporting is wired for release builds.

## Report

Deliver, in this order:

1. **Verdict:** Ready, Ready with should-fixes, or Not ready, with the launch target, the commit audited, and the count of findings by severity. Any open blocker makes it Not ready. So does an "Unknown" in a check that could hide a blocker (access rules, backups, spend exposure); say the verdict is pending that check. Ready means no open blockers and no should-fixes.
2. **Findings**, blockers first: severity, area, one-line finding, evidence, a fix sketch, and rough effort.
3. **Unknown:** what could not be checked and how the user can check it.
4. **Manual steps:** dashboard-only settings for the user.
5. **Checked and passed:** one line per area, so an area with no findings is not mistaken for an area not checked.

When the project has a spec, add or replace a section headed exactly "Production preflight" (match that heading only, so an unrelated section is never overwritten): the date, commit, launch target, verdict, and one line per open blocker and should-fix. Later preflights replace it; fixes update it. A launch step can read this section.

## Fix mode

Take the findings the user chose, or every blocker when they say "fix the blockers". Group related findings into coherent slices and give `$bosun-brief` each slice's findings with their evidence. Every fix gets a done-condition that proves it, not only that code changed:

- An access-control fix adds a test of the denied case: the other user's row, the forged claim, the normalized redirect, the protected string absent from the page source.
- A guardrail fix shows the limit tripping in a test.
- A cookie or metadata fix is checked on a production build in the browser, and a header fix on a preview deployment or in the host's header configuration (as in "Evidence and safety"), each as a route done-condition the verifier can re-check.
- A reliability fix has a test of the failure path: the timeout, the duplicate delivery, the failed post-commit step.

Verify each slice through `$bosun-verify`. After the fixes land, re-run the checks behind each fixed finding and update the Production preflight record.

## Boundaries

This is a readiness audit, not a penetration test, and it does not replace a diff-scoped security review (such as Claude Code's `/security-review`), which still belongs on each change. It does not deploy, provision production, or change hosted settings; the project's own launch tooling does that, after this audit. It does not repeat `$bosun-ci`: CI performance and reliability belong there.
