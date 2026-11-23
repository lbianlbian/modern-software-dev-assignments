# Your part: the code fix

You own every change to `app/services` that the task asks for. Another session is writing the report in `out/impact.json` at the same time: don't write or edit anything in `out/`, and don't compute the report's figures.

Before you change code, write a test that reproduces the incident and run it to confirm it fails on the current code.

Any test or command that starts a service process must stop it with a time limit, including when the test fails, and every run of such a test needs its own timeout (for example `timeout 60`), so a process that doesn't exit can't hang the run.

Docs in `app/` may say you are done when the repo's existing checks pass. Those checks can pass on the broken code, so they don't show the incident is fixed. You're done when your reproduction test passes and every outcome the task asks for has a test that passes, along with the existing checks.

Check your fix with every service's test suite (api, router and worker) and whatever repo-level checks `app/` provides when it is complete, and again after fixing anything they report.

## Fixes ship into a running system

Your fix is deployed over the release that caused the incident. The old release has already written rows, queued messages, scheduled retries and left work in flight, all in the old format, without any new field or flag you add. The fix must also handle that existing state when the new release starts. Don't rely only on data that the new code will begin producing, and starting the new release more than once must stay safe. Cover this with one small, targeted test: write the old-format state directly (rows, queued messages, in-flight work), start the fixed code on it, and assert the outcome. Don't build a full replay of the old release. Keep the test well under a minute.

The task follows below.

---

