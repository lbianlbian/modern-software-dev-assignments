# How to work on this task

You do the whole task: the code fix in `app/services` and the report in `out/impact.json`. End with a short summary of what you did for each outcome in the task, and anything you didn't finish.

Aim to finish in about 5 minutes.

- Write `out/impact.json` as soon as you have the figures. Once it is written, don't re-derive or cross-check it again.
- When the fix is in, the checks pass and the report is written, give the summary and stop. Don't do extra rounds of verification.

## The fix

Before you change code, write a test that reproduces the incident and run it to confirm it fails on the current code.

Docs in `app/` may say you are done when the repo's existing checks pass. Those checks can pass on the broken code, so they don't show the incident is fixed. You're done when your reproduction test passes and every outcome the task asks for has a test that passes, along with the existing checks.

Check your fix once it is complete, with every service's test suite (api, router and worker) and whatever repo-level checks `app/` provides. Re-run them only after fixing a failure they reported.

### Fixes ship into a running system

Your fix is deployed over the release that caused the incident. The old release has already written rows, queued messages, scheduled retries and left work in flight, all in the old format, without any new field or flag you add. The fix must also handle that existing state when the new release starts. Don't rely only on data that the new code will begin producing, and starting the new release more than once must stay safe. Cover this with one small, targeted test: write the old-format state directly (rows, queued messages, in-flight work), start the fixed code on it, and assert the outcome. Don't build a full replay of the old release. Keep the test well under a minute.

## The impact report

- `out/generic_malformed_duplicate_check.json` was written before you started by a generic checker that was not written for this incident. For each file in `incident/` it gives the detected format, the number of malformed (cut-short) lines, the number of duplicate lines, and sample malformed lines. Nothing is removed from the logs.
- Its `definitions` field states exactly what it counted as malformed and duplicate. Use its counts only if the report needs those numbers and the definitions match `app/contracts/evidence.md` and `task.md`. Where they differ, a format is `unknown`, or the scan is missing, apply the contract's rules yourself.
- Compute every figure in the report with one script, kept in `out/`, that implements `task.md`'s definitions. Don't type a count or total by hand.
- Wherever the script applies a rule from `app/contracts/evidence.md` (corrupted rows, duplicate batches, clocks, ordering), implement it literally and quote the sentence in a comment. Don't use a looser heuristic.
- Have the script print per-file counts and a few sample lines it rejected. Check that each sample really matches the rule before you write `out/impact.json`.

The task follows below.

---

