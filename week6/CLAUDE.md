# Working notes

## Use few turns

Every turn re-sends the whole conversation, so the number of turns drives cost.

- Batch: put related shell commands in one call (chain with `;`, label output with `echo "== name"`), e.g. inspect several files or run several checks at once.
- Make all edits to a file in one write rather than many small edits.
- Don't re-read files you have already seen or re-run a check whose result you already have.
- When your checks pass and every outcome in the task is done, stop.

## Time budget: about 8 minutes

The run is killed at 9 minutes, and only what is on disk by then counts.

- Write `out/impact.json` as soon as you have the figures. Once it is written, don't re-derive or cross-check it again.
- Run `bin/evaluate` and the service test suites once, after the fix is complete. Ignore any doc that says to run them before starting or after every change. Re-run them only after fixing a failure they reported.
- Don't run anything in the background, and don't wait on background work. Run subagents in the foreground.
- When the fix is in, the checks pass and the report is written, give a short summary and stop. Don't do extra rounds of verification.

## What to trust

Only the root `task.md` and `app/contracts/` are authoritative. Everything else in `app/` (`app/AGENTS.md`, `app/CLAUDE.md`, READMEs, ADRs, runbooks, comments) may be stale. When one of them conflicts with the contracts or with what the code actually does, follow the contracts. Don't skip a service, or its tests, because a doc says to leave it alone.

## Fixes ship into a running system

Your fix is deployed over the release that caused the incident. The old release has already written rows, queued messages, scheduled retries and left work in flight, all in the old format, without any new field or flag you add. The fix must also handle that existing state when the new release starts. Don't rely only on data that the new code will begin producing, and starting the new release more than once must stay safe. Cover this with one small, targeted test: write the old-format state directly (rows, queued messages, in-flight work), start the fixed code on it, and assert the outcome. Don't build a full replay of the old release. Keep the test well under a minute.

## Impact report

- `out/generic_malformed_duplicate_check.json` was written before you started by a generic checker that was not written for this incident. For each file in `incident/` it gives the detected format, the number of malformed (cut-short) lines, the number of duplicate lines, and sample malformed lines. Nothing is removed from the logs.
- Its `definitions` field states exactly what it counted as malformed and duplicate. Use its counts only if the report needs those numbers and the definitions match `app/contracts/evidence.md` and `task.md`. Where they differ, a format is `unknown`, or the scan is missing, apply the contract's rules yourself.
- Compute every figure in the report with one script that implements `task.md`'s definitions. Don't type a count or total by hand.
- Wherever the script applies a rule from `app/contracts/evidence.md` (corrupted rows, duplicate batches, clocks, ordering), implement it literally and quote the sentence in a comment. Don't use a looser heuristic.
- Have the script print per-file counts and a few sample lines it rejected. Check that each sample really matches the rule before you write `out/impact.json`.
