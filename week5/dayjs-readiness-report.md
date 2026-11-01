# Agent Readiness Report: dayjs

**Level:** 2/5  
**Overall Score:** 38%  
**Generated:** 2026-10-30 01:19:10 UTC  
**Commit:** `436bde0`  
**Branch:** dev  

## Summary

| Metric | Value |
|--------|-------|
| Total Criteria | 84 |
| Passed | 25 |
| Failed | 40 |
| Skipped | 19 |

## Pass Rate by Category

| Category | Pass Rate |
|----------|-----------|
| Style & Validation | 55% |
| Build System | 50% |
| Testing | 60% |
| Documentation | 43% |
| Development Environment | 0% |
| Debugging & Observability | 11% |
| Security | 17% |
| Task Discovery | 25% |
| Product & Experimentation | 0% |

## Style & Validation

| Criterion | Score | Status | Rationale |
|-----------|-------|--------|-----------|
| Type Checker | 0/1 | 🔴 Failed | TypeScript is a devDependency and declarations are supplied, but no tsconfig, checkJs configuration, tsc script, or type-checking CI task exists. |
| Strict Typing | 0/1 | 🔴 Failed | No strict TypeScript or JavaScript type-checking configuration exists; declaration presence alone does not enforce strict types. |
| Cyclomatic Complexity | 0/1 | 🔴 Failed | No enabled complexity threshold, complexity analyzer, or quality platform is configured. |
| Duplicate Code Detection | 0/1 | 🔴 Failed | No jscpd, CPD, Sonar, or other duplicate-code detector is configured. |
| Technical Debt Tracking | 0/1 | 🔴 Failed | TODO comments exist, but no debt scanner, issue-link enforcement, quality platform, or documented debt tracking process is configured. |
| Linter Configuration | 1/1 | 🟢 Passed | .eslintrc.json extends airbnb-base with Jest/import plugins. CI and the lint script invoke ESLint. |
| Code Formatter | 1/1 | 🟢 Passed | prettier.config.js and a Prettier dependency/script configure automated formatting for docs/**/*.md. |
| Pre-commit Hooks | 1/1 | 🟢 Passed | The pre-commit dependency and package.json pre-commit setting run lint before commits. |
| Naming Consistency | 1/1 | 🟢 Passed | The configured Airbnb ESLint base supplies naming rules such as camelcase; local overrides do not disable them. |
| Large File Detection | 1/1 | 🟢 Passed | Release CI runs npm run build, which runs size-limit and rejects dayjs.min.js above 2.99 KB. This guards the generated bundle, not arbitrary source files. |
| Dead Code Detection | 1/1 | 🟢 Passed | Airbnb ESLint base enables unused-variable checking; local overrides do not disable no-unused-vars. |
| Code Modularization Enforcement | N/A | Skipped | A compact date/time core with optional plugins/locales has no substantial service or application-layer architecture requiring boundary enforcement. |
| N+1 Query Detection | N/A | Skipped | No database, ORM, or database-query layer exists. |

## Build System

| Criterion | Score | Status | Rationale |
|-----------|-------|--------|-----------|
| Build Command Documentation | 0/1 | 🔴 Failed | package.json defines build and babel scripts, but README.md has no repository build command and there is no root AGENTS.md. |
| Automated PR Review Generation | 0/1 | 🔴 Failed | The latest 10 PRs have no reviews or comments, and no workflow generates review content. Codecov coverage comments on older PRs are not code reviews. |
| Build Performance Tracking | 0/1 | 🔴 Failed | CI caches npm downloads, but no compiled-output cache, build benchmark, performance budget, build metrics export, or deliberate build-duration monitoring is configured. |
| Deployment Frequency | 0/1 | 🔴 Failed | Both 30 releases and 30 exact release.yml runs were requested. Releases are sporadic, with long gaps; the latest two releases were August 16-17, 2026, not a sustained multiple-per-week cadence. |
| Single Command Setup | 0/1 | 🔴 Failed | README documents installing the published package, not a fresh-clone developer setup. No documented sequence installs dependencies and produces a runnable local checkout. |
| Feature Flag Infrastructure | 0/1 | 🔴 Failed | No rollout flag platform or custom feature-toggle system is configured. Optional library plugins are not release feature flags. |
| Unused Dependencies Detection | 0/1 | 🔴 Failed | No depcheck, knip, npm-check, or equivalent unused-dependency check exists. ESLint dependency classification is explicitly disabled and is not usage analysis. |
| Dependencies Pinned | 1/1 | 🟢 Passed | A committed package-lock.json v2 records resolved dependency versions; release CI uses npm clean-install. |
| VCS CLI Tools | 1/1 | 🟢 Passed | GitHub CLI is installed and gh auth status confirms an authenticated GitHub session. |
| Agentic Development | 1/1 | 🟢 Passed | The last 100 commits include PR #3012 with an explicit Claude Opus 4.6 co-author, also preserved in merge #3018. |
| Fast CI Feedback | 1/1 | 🟢 Passed | Across 20 merged PRs, 18 have timed primary CI checks. Earliest start to latest finish averages 50.39 seconds, below 10 minutes; two lack timing evidence. |
| Release Notes Automation | 1/1 | 🟢 Passed | The release workflow installs semantic-release changelog/git plugins; .releaserc generates and commits CHANGELOG.md. |
| Heavy Dependency Detection | 1/1 | 🟢 Passed | size-limit enforces a 2.99 KB budget for dayjs.min.js; the build also reports gzip size and runs in release CI. |
| Release Automation | 1/1 | 🟢 Passed | release.yml runs on master pushes after lint/tests, builds packages, verifies signatures, and invokes semantic-release. |
| Progressive Rollout | N/A | Skipped | Not applicable: this is an npm library, not an infrastructure repository. |
| Rollback Automation | N/A | Skipped | Not applicable: this is a library repository without infrastructure deployments. |
| Monorepo Tooling | N/A | Skipped | Single root application and one build package; plugins, locales, and demos share its package lifecycle. |
| Version Drift Detection | N/A | Skipped | Only one build package/module exists, so sibling-module dependency drift does not apply. |
| Dead Feature Flag Detection | N/A | Skipped | Skipped because feature_flag_infrastructure does not pass; no feature-flag system exists. |

## Testing

| Criterion | Score | Status | Rationale |
|-----------|-------|--------|-----------|
| Unit Tests Runnable | 0/1 | 🔴 Failed | A direct 60-second bounded command, npx --no-install jest --listTests --runInBand, exited 1 because local Jest is absent. No tests executed and no dependencies were installed. Node is available, so... |
| Flaky Test Detection | 0/1 | 🔴 Failed | The 10-PR check sample shows no retry/duplicate-check evidence, and no retry plugin, quarantine policy, or flakiness tracking configuration exists. |
| Interactive QA Exists | 0/1 | 🔴 Failed | README provides published-package usage, but no complete local-checkout QA path covers dependency setup, building/loading the library, and an executable interaction with expected output. |
| Interactive QA Runnable | 0/1 | 🔴 Failed | A direct Node API interaction through require('.') failed because dayjs.min.js is missing. Build dependencies are absent, and no complete documented checkout QA fallback exists. |
| Unit Tests Exist | 1/1 | 🟢 Passed | Jest unit tests cover construction, parsing, formatting, manipulation, comparison, locales, and plugins under test/. |
| Integration Tests Exist | 1/1 | 🟢 Passed | karma.sauce.conf.js loads the built dayjs.min.js and test/browser.spec.js into real browsers; browser tests verify global installation and chained API behavior. |
| Test Performance Tracking | 1/1 | 🟢 Passed | Retained GitHub CI job 95371243662 reports runtime for each timezone invocation and the full Jest stage, including Time: 7.119s, beyond pass/fail status. |
| Test Coverage Thresholds | 1/1 | 🟢 Passed | The final Jest stage in npm test enforces global lines coverageThreshold=100; CI invokes that script. |
| Test File Naming Conventions | 1/1 | 🟢 Passed | package.json configures Jest roots and testRegex test/(.*?/)?.*test.js$; CONTRIBUTING also prescribes test/*.test.js. |
| Test Isolation | 1/1 | 🟢 Passed | CI invokes Jest without --runInBand, using Jest's default worker-based execution and isolated per-file test environments. |

## Documentation

| Criterion | Score | Status | Rationale |
|-----------|-------|--------|-----------|
| AGENTS.md File | 0/1 | 🔴 Failed | No AGENTS.md exists at the repository root or elsewhere in the repository. |
| Skills Configuration | 0/1 | 🔴 Failed | No repository-local skill directory or valid {skill-name}/SKILL.md exists. |
| Service Architecture Documented | 0/1 | 🔴 Failed | No architecture/flow diagram, architecture documentation, or service dependency document was found. |
| AGENTS.md Freshness Validation | 0/1 | 🔴 Failed | No AGENTS.md exists, so its commands and accuracy cannot be validated by automation. |
| README File | 1/1 | 🟢 Passed | Root README.md explains npm installation, the date/time API, locales, plugins, and documentation links. |
| Automated Documentation Generation | 1/1 | 🟢 Passed | Configured semantic-release changelog generation updates CHANGELOG.md automatically during releases. |
| Documentation Freshness | 1/1 | 🟢 Passed | Git history shows README.md updated September 15, 2026 and CONTRIBUTING.md updated August 18, 2026, within 180 days of the audit. |
| API Schema Docs | N/A | Skipped | This library exposes JavaScript APIs, not HTTP/GraphQL service APIs. |

## Development Environment

| Criterion | Score | Status | Rationale |
|-----------|-------|--------|-----------|
| Dev Container | 0/1 | 🔴 Failed | No .devcontainer/devcontainer.json or equivalent development-container configuration exists. |
| Environment Template | 0/1 | 🔴 Failed | No .env.example or README/AGENTS environment-variable documentation exists. The library itself needs no service credentials, but this non-skippable documentation check is unmet. |
| Local Services Setup | N/A | Skipped | The date/time library has no database or external runtime service dependencies. Optional SauceLabs browser testing is not a local application dependency. |
| Database Schema | N/A | Skipped | No database is used. |
| Devcontainer Runnable | N/A | Skipped | The devcontainer CLI is unavailable; no container build or run was attempted. |

## Debugging & Observability

| Criterion | Score | Status | Rationale |
|-----------|-------|--------|-----------|
| Structured Logging | 0/1 | 🔴 Failed | No structured logging dependency or dedicated logger module exists; devHelper emits plain console warnings. |
| Distributed Tracing | 0/1 | 🔴 Failed | No OpenTelemetry, request/trace ID propagation, or equivalent tracing instrumentation exists. |
| Metrics Collection | 0/1 | 🔴 Failed | No runtime metrics/telemetry instrumentation is configured. Build size and test coverage are not application telemetry. |
| Error Tracking Contextualized | 0/1 | 🔴 Failed | No Sentry, Bugsnag, Rollbar, or contextual production error tracking is configured. |
| Alerting Configured | 0/1 | 🔴 Failed | No PagerDuty/OpsGenie integration or custom operational alerting rules exist. |
| Runbooks Documented | 0/1 | 🔴 Failed | No incident runbooks/playbooks directory or operational runbook pointer appears in repository documentation. |
| Deployment Observability | 0/1 | 🔴 Failed | No deployment-impact dashboard or deploy notification/annotation integration is documented. |
| Profiling Instrumentation | 0/1 | 🔴 Failed | No CPU/memory profiling, flamegraph generation, APM, or development profiler is configured; date/time library performance remains meaningful. |
| Code Quality Metrics Dashboard | 1/1 | 🟢 Passed | CI collects coverage and uploads to Codecov. Merged PR #3180 has a Codecov coverage comment and patch/project checks. |
| Health Checks | N/A | Skipped | An npm library is not a running deployed service and has no health endpoint/probe requirement. |
| Circuit Breakers | N/A | Skipped | The library makes no external service calls requiring circuit breakers or retry resilience. |

## Security

| Criterion | Score | Status | Rationale |
|-----------|-------|--------|-----------|
| CODEOWNERS File | 0/1 | 🔴 Failed | No root or .github CODEOWNERS file exists. |
| Dependency Update Automation | 0/1 | 🔴 Failed | No Dependabot/Renovate configuration exists, and a bounded search for Dependabot PRs returned none. |
| Gitignore Comprehensive | 0/1 | 🔴 Failed | .gitignore covers node_modules, generated bundles, coverage, IDEs, and .DS_Store, but does not exclude .env or other environment-secret files. |
| Sensitive Data Log Scrubbing | 0/1 | 🔴 Failed | No log redaction, masking, sanitization utility, or documented scrubbing policy exists. |
| Minimum Dependency Release Age | 0/1 | 🔴 Failed | No dependency minimumReleaseAge/stabilityDays setting, waiting-period policy, or release-date gate exists. |
| Secrets Management | 1/1 | 🟢 Passed | GitHub Actions obtains GITHUB_TOKEN and CODECOV_TOKEN via secrets references rather than hardcoded values. |
| Branch Protection | N/A | Skipped | Authenticated gh api reports permissions.admin=false and maintain=false; protection/ruleset inspection is skipped under the required access rule. |
| Secret Scanning | N/A | Skipped | No local secret-scanning workflow or hook was found. Native GitHub scanning is unverified because the authenticated user lacks admin access. |
| Automated Security Review Generation | N/A | Skipped | No configured readable automated security assessment was found. Native code-scanning inspection is skipped because admin access is unavailable; npm audit signatures is provenance verification, not ... |
| DAST Scanning | N/A | Skipped | The library is not deployed as a web service with endpoints suitable for DAST. |
| PII Handling | N/A | Skipped | The standalone developer library does not collect or manage personal/user records. |
| Privacy Compliance | N/A | Skipped | The standalone date/time library does not collect end-user data. |

## Task Discovery

| Criterion | Score | Status | Rationale |
|-----------|-------|--------|-----------|
| Issue Labeling System | 0/1 | 🔴 Failed | GitHub labels include bug/enhancement and high priority, but no consistent area labels. None of the 50 sampled open issues had labels. |
| Backlog Health | 0/1 | 🔴 Failed | Among 50 sampled open issues, 0 have both a title longer than 10 characters and at least one label, below the required >70%. |
| PR Templates | 0/1 | 🔴 Failed | No pull-request template exists with description, testing, and contextual sections. |
| Issue Templates | 1/1 | 🟢 Passed | .github/ISSUE_TEMPLATE/--bug-report.md requests symptoms, expected behavior, version, OS, browser, and time zone. |

## Product & Experimentation

| Criterion | Score | Status | Rationale |
|-----------|-------|--------|-----------|
| Product Analytics Instrumentation | 0/1 | 🔴 Failed | No product-analytics SDK or event instrumentation is present. |
| Error to Insight Pipeline | 0/1 | 🔴 Failed | No error-tracker-to-issue integration, error webhook workflow, or incident-to-issue automation exists. |

---

*Generated by Factory Agent Readiness*