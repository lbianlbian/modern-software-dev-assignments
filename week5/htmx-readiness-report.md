# Agent Readiness Report: htmx

**Level:** 2/5  
**Overall Score:** 25%  
**Generated:** 2026-11-01 04:15:40 UTC  
**Commit:** `fa978b2`  
**Branch:** master  

## Summary

| Metric | Value |
|--------|-------|
| Total Criteria | 84 |
| Passed | 13 |
| Failed | 56 |
| Skipped | 15 |

## Pass Rate by Category

| Category | Pass Rate |
|----------|-----------|
| Style & Validation | 14% |
| Build System | 33% |
| Testing | 45% |
| Documentation | 43% |
| Development Environment | 0% |
| Debugging & Observability | 5% |
| Security | 25% |
| Task Discovery | 25% |
| Product & Experimentation | 0% |

## Style & Validation

| Criterion | Score | Status | Rationale |
|-----------|-------|--------|-----------|
| Pre-commit Hooks | 0/2 | 🔴 Failed | Neither application has Husky, lint-staged, pre-commit, Lefthook, or checked-in quality-check hooks. |
| Strict Typing | 0/2 | 🔴 Failed | The library's checkJs command does not enable --strict and no strict tsconfig exists. The website has no strict type-check configuration. |
| Naming Consistency | 0/2 | 🔴 Failed | No naming-convention enforcement or explicit contributor naming rules were found. The root ESLint configuration disables camelcase. |
| Cyclomatic Complexity | 0/2 | 🔴 Failed | Neither application configures complexity thresholds, a complexity analyzer, or a maintainability quality gate. |
| Large File Detection | 0/1 | 🔴 Failed | No file-size hook, CI size gate, Git LFS configuration, or max-lines rule was found. |
| Dead Code Detection | 0/2 | 🔴 Failed | No dead-code detector or unused-module rule is configured for either application. The library explicitly disables no-unused-vars. |
| Duplicate Code Detection | 0/2 | 🔴 Failed | No duplicate-code analyzer, jscpd, CPD, or equivalent CI check covers either application. |
| Technical Debt Tracking | 0/1 | 🔴 Failed | No TODO/FIXME enforcement, debt scanner, quality platform, or documented technical-debt tracking process was found. |
| Linter Configuration | 1/2 | 🔴 Failed | The root application's package.json configures ESLint Standard and Mocha rules. Lint targets do not cover www templates or application-owned site scripts. |
| Type Checker | 1/2 | 🔴 Failed | The library runs tsc --checkJs --noEmit through types-check and npm test in CI. The website has no configured type-check target. |
| Code Formatter | 1/2 | 🔴 Failed | npm run format uses ESLint --fix on library source, tests, and build scripts. Website-owned source is outside its target paths. |
| Code Modularization Enforcement | N/A | Skipped | Module-boundary tooling is not meaningful for the single-file core library and small static-theme/demo implementation. |
| N+1 Query Detection | N/A | Skipped | Neither application uses a database or ORM. |

## Build System

| Criterion | Score | Status | Rationale |
|-----------|-------|--------|-----------|
| Build Command Documentation | 0/1 | 🔴 Failed | README.md documents installation and serving tests, but not npm run dist. The Zola build command appears in netlify.toml, not README.md or AGENTS.md. |
| Automated PR Review Generation | 0/1 | 🔴 Failed | The 10 most recent PRs contain no automated review content. Local CI only runs checks; no review-comment generator is configured. |
| Fast CI Feedback | 0/1 | 🔴 Failed | Of 20 merged PRs, 18 have completed checks. Earliest-start to latest-completion spans average 303.23 minutes, exceeding 10 minutes because of a multi-day rerun on #4127; 17/18 spans are under 10 mi... |
| Build Performance Tracking | 0/1 | 🔴 Failed | Local CI has no deliberate build caching, build-performance metrics, or optimization tracking. Setup-node's runtime tool cache is not a project build cache. |
| Deployment Frequency | 0/1 | 🔴 Failed | Checked 30 releases and 50 workflow runs. Releases are not multiple times weekly; sampled workflows are Node CI and CodeQL, not deployment runs. Netlify cadence is not established. |
| Feature Flag Infrastructure | 0/1 | 🔴 Failed | No release feature-flag platform or lifecycle is configured. htmx.config options are library behavior settings, not a release-gating system. |
| Release Notes Automation | 0/1 | 🔴 Failed | No changelog or release-note generator is configured. The inspected v2.0.10 GitHub release body only says to see CHANGELOG.md. |
| Monorepo Tooling | 0/1 | 🔴 Failed | Two independently deployed units exist, but there is no workspace, multi-project orchestrator, or explicit monorepo boundary tooling. |
| Heavy Dependency Detection | 0/2 | 🔴 Failed | No configured bundle analyzer, size budget, or dependency-size CI gate covers either application. README Bundlephobia badges display size but do not configure such analysis. |
| Unused Dependencies Detection | 0/2 | 🔴 Failed | No depcheck, knip, dependency-analysis command, or equivalent unused-dependency check is configured. |
| Dependencies Pinned | 1/1 | 🟢 Passed | Committed package-lock.json v3 pins npm resolutions and integrity hashes. netlify.toml fixes ZOLA_VERSION to 0.19.1. |
| VCS CLI Tools | 1/1 | 🟢 Passed | GitHub CLI is installed; gh auth status succeeded with an active authenticated account. |
| Agentic Development | 1/1 | 🟢 Passed | The last 100 commits include explicit Claude co-authorship on merged code and documentation changes, including PR #3772. |
| Single Command Setup | 1/1 | 🟢 Passed | Root README documents npm install, npx serve, and the browser test URL. www/README.md documents installing Zola and running cd www; zola serve. |
| Release Automation | 1/1 | 🟢 Passed | netlify.toml configures the www deployment base, zola build, published output, and deploy-preview builds; README links the active Netlify deployment dashboard. |
| Progressive Rollout | N/A | Skipped | Not an infrastructure repository; it contains a browser library and static documentation site. Netlify previews are not percentage-based rollouts. |
| Rollback Automation | N/A | Skipped | Not an infrastructure repository. No in-scope deployment infrastructure requiring this criterion was identified. |
| Version Drift Detection | N/A | Skipped | There is only one dependency-managed npm package/graph. The separate Zola site has no sibling dependency manifest to compare. |
| Dead Feature Flag Detection | N/A | Skipped | Skipped because feature_flag_infrastructure does not pass; no managed release flags exist to audit. |

## Testing

| Criterion | Score | Status | Rationale |
|-----------|-------|--------|-----------|
| Unit Tests Runnable | 0/2 | 🔴 Failed | No successful test collection was obtained. Bounded node ./node_modules/@web/test-runner/dist/bin.js --help exited 1 with MODULE_NOT_FOUND. Node is installed, so this is not a missing-runtime skip.... |
| Flaky Test Detection | 0/2 | 🔴 Failed | The 10 latest PR check rollups have no duplicate check names, and local configurations contain no retry/quarantine or flaky-test management. A transient-failure comment alone is not proactive track... |
| Test Coverage Thresholds | 0/2 | 🔴 Failed | The library enables coverage reporting but sets no minimum coverage threshold or blocking coverage gate. The website has no coverage enforcement. |
| Unit Tests Exist | 1/2 | 🔴 Failed | The library has 50 JavaScript test files in test/core and test/attributes. www/static/test mirrors library tests, not website-specific unit tests. |
| Integration Tests Exist | 1/2 | 🔴 Failed | Library browser tests integrate DOM events, request generation, swaps, and Sinon fake HTTP responses using Web Test Runner/Playwright. No website-specific integration suite exists locally. |
| Test Performance Tracking | 1/2 | 🔴 Failed | Library CI run 35739169203 retains reporter timing: Finished running tests in 19.3s. The local website has no separate test-duration reporting configuration. |
| Test File Naming Conventions | 1/2 | 🔴 Failed | web-test-runner.config.mjs explicitly discovers test/attributes/**/*.js and test/core/**/*.js; TESTING.md documents these patterns. No website-specific test naming configuration exists. |
| Test Isolation | 1/2 | 🔴 Failed | Library tests run in Web Test Runner browser test pages and reset Sinon servers/work areas in beforeEach/afterEach. No website-specific isolated test suite is configured. |
| Interactive QA Exists | 2/2 | 🟢 Passed | Library README/TESTING document dependency installation, a local server/manual runner, and selecting/replaying browser tests. www/README documents Zola setup; click-to-edit docs supply a mocked edi... |
| Interactive QA Runnable | 2/2 | 🟢 Passed | Documentation fallback used, not live success: npm run test:debug failed because dependencies are absent; zola serve failed because Zola is unavailable. Both complete QA paths cover setup, launch, ... |

## Documentation

| Criterion | Score | Status | Rationale |
|-----------|-------|--------|-----------|
| AGENTS.md File | 0/1 | 🔴 Failed | No AGENTS.md exists at repository root or elsewhere in the repository. |
| Skills Configuration | 0/1 | 🔴 Failed | No repository-local skill directory or valid skill-name/SKILL.md was found. |
| Service Architecture Documented | 0/1 | 🔴 Failed | No project architecture diagram or service-dependency map was found. The architecture-named image is a meme, not an architecture diagram. |
| AGENTS.md Freshness Validation | 0/1 | 🔴 Failed | AGENTS.md is absent, and no automation validates agent instructions or their commands. |
| README File | 1/1 | 🟢 Passed | Root README.md includes npm installation, usage examples, local development setup, and test navigation. |
| Automated Documentation Generation | 1/1 | 🟢 Passed | The Zola configuration and Netlify build generate and publish the documentation website from Markdown and templates. |
| Documentation Freshness | 1/1 | 🟢 Passed | Git history records README.md updates on 2026-09-22 and 2026-09-07, within 180 days of the audit date. |
| API Schema Docs | N/A | Skipped | Neither application exposes a service API requiring OpenAPI/GraphQL. Recursive schema-pattern searches found none. |

## Development Environment

| Criterion | Score | Status | Rationale |
|-----------|-------|--------|-----------|
| Dev Container | 0/1 | 🔴 Failed | No .devcontainer/devcontainer.json or equivalent devcontainer configuration was found. |
| Environment Template | 0/1 | 🔴 Failed | No .env.example or environment-variable documentation in README.md/AGENTS.md. CHROME_PATH is documented only in CONTRIBUTING.md. |
| Local Services Setup | N/A | Skipped | Neither application needs a local database or external backend service; browser tests and website demos use Sinon mocks. |
| Database Schema | N/A | Skipped | Neither application has a database; example contacts live in browser-local demo objects. |
| Devcontainer Runnable | N/A | Skipped | The devcontainer CLI is unavailable, so the runnable-devcontainer check is skipped. |

## Debugging & Observability

| Criterion | Score | Status | Rationale |
|-----------|-------|--------|-----------|
| Structured Logging | 0/2 | 🔴 Failed | No logging-library dependency or dedicated logger module exists in either application. htmx.logger is an optional callback inside the core file; demo timelines are not a structured logging system. |
| Distributed Tracing | 0/2 | 🔴 Failed | Neither application propagates trace IDs or request IDs across requests. Demo timeline counters are local UI identifiers, not distributed tracing. |
| Metrics Collection | 0/2 | 🔴 Failed | Neither application configures operational metrics/telemetry. performance.now assertions are test benchmarks, and demo counters are not a telemetry backend. |
| Error Tracking Contextualized | 0/2 | 🔴 Failed | Neither application configures Sentry, Bugsnag, Rollbar, or contextualized error reporting with source maps/breadcrumbs. |
| Alerting Configured | 0/2 | 🔴 Failed | No alert rules, PagerDuty/OpsGenie integration, or custom operational notification system is configured. |
| Runbooks Documented | 0/1 | 🔴 Failed | No incident runbook/playbook directory or documentation link to operational runbooks was found. |
| Deployment Observability | 0/2 | 🔴 Failed | README links Netlify deployment/build status, but neither application documents runtime-impact monitoring dashboards or deployment annotations/notifications. |
| Health Checks | 0/2 | 🔴 Failed | The deployed www site has no configured health endpoint or explicit health-check mechanism. The library is not a deployed service; the fixed application denominator remains 2. |
| Profiling Instrumentation | 0/2 | 🔴 Failed | The library has performance.now benchmark assertions but no CPU/memory profiler, flame-graph tooling, or APM configuration. No website profiling instrumentation is configured. |
| Code Quality Metrics Dashboard | 1/2 | 🔴 Failed | The library enables coverage for src/htmx.js and documents the HTML coverage report; historical CI prints coverage. No website-specific quality-metric configuration was found. Admin-only scanning a... |
| Circuit Breakers | N/A | Skipped | Neither application has required external backend-service calls needing circuit breakers; library HTTP requests are consumer-controlled and site demos use mocks. |

## Security

| Criterion | Score | Status | Rationale |
|-----------|-------|--------|-----------|
| CODEOWNERS File | 0/1 | 🔴 Failed | No CODEOWNERS file exists at root or under .github. |
| Gitignore Comprehensive | 0/1 | 🔴 Failed | Ignore rules cover node_modules, coverage, IDE files, .DS_Store, and www/public, but do not exclude .env or other environment-secret files. |
| DAST Scanning | 0/2 | 🔴 Failed | The deployed website has no DAST scan configuration. Library security tests use fake HTTP responses, not a scanner against a deployed test service. |
| Secrets Management | 0/1 | 🔴 Failed | No secrets-manager integration, documented secure secret source, secrets.* workflow references, or ignored-.env plus template pattern was found. |
| Sensitive Data Log Scrubbing | 0/2 | 🔴 Failed | Neither application configures log redaction, sensitive-field filtering, or documented log scrubbing. HTML escaping and suppressing event logs are not sensitive-data redaction. |
| Minimum Dependency Release Age | 0/1 | 🔴 Failed | No explicit dependency waiting-period policy, minimumReleaseAge/stabilityDays setting, or release-age CI gate was found. |
| Automated Security Review Generation | 1/1 | 🟢 Passed | Live GitHub evidence shows successful CodeQL analysis, including run 41011761324. Dependabot PR #4115 also contains readable release/security-advisory content. Admin-only alert APIs were not queried. |
| Dependency Update Automation | 1/1 | 🟢 Passed | GitHub shows active Dependabot update PRs, including #4115 and #4116 from 2026-10-02, plus merged bot updates in local history. |
| Branch Protection | N/A | Skipped | Authenticated repository permission lookup returned permissions.admin=false; branch protection inspection is skipped as required. |
| Secret Scanning | N/A | Skipped | No local secret-scanning tooling was found. Native configuration cannot be verified because the authenticated account lacks admin access. |
| PII Handling | N/A | Skipped | No production personal-data collection or storage flow is present in these library/static-site applications. Demo contact records are synthetic and remain in browser memory. |
| Privacy Compliance | N/A | Skipped | No end-user data collection backend or tracking integration is present. The library and static site use synthetic, browser-local demonstration data. |

## Task Discovery

| Criterion | Score | Status | Rationale |
|-----------|-------|--------|-----------|
| Issue Templates | 0/1 | 🔴 Failed | No .github/ISSUE_TEMPLATE directory exists; CONTRIBUTING.md explicitly states there is no issue template. |
| Issue Labeling System | 0/1 | 🔴 Failed | GitHub labels include types and areas such as bug, enhancement, website, and javascript, but lack a priority/severity taxonomy. |
| Backlog Health | 0/1 | 🔴 Failed | Only 5 of 50 sampled open issues have both a descriptive title and at least one label, 10%, below the required >70%. None of this newest-issue sample is stale over one year. |
| PR Templates | 1/1 | 🟢 Passed | .github/PULL_REQUEST_TEMPLATE.md provides Description, corresponding issue, Testing, and a contribution checklist. |

## Product & Experimentation

| Criterion | Score | Status | Rationale |
|-----------|-------|--------|-----------|
| Product Analytics Instrumentation | 0/2 | 🔴 Failed | Neither application configures product analytics such as GA4, PostHog, Mixpanel, or Amplitude. |
| Error to Insight Pipeline | 0/2 | 🔴 Failed | No error-tracker-to-issue integration, incident-to-issue automation, or equivalent error-to-insight pipeline exists. |

---

*Generated by Factory Agent Readiness*