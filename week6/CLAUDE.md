# Working notes

## Two sessions, one after the other

`run.sh` runs a main session that does the whole task, then a review session that checks the main session's work against the task and fixes what is missing. Your prompt says which one you are and how much time you have.

## Use few turns

Every turn re-sends the whole conversation, so the number of turns drives cost.

- Batch: put related shell commands in one call (chain with `;`, label output with `echo "== name"`), e.g. inspect several files or run several checks at once.
- Make all edits to a file in one write rather than many small edits.
- Don't re-read files you have already seen.
- When every outcome you own is done and checked, give a short summary and stop.

## Time

The whole run is killed at 10 minutes, and only what is on disk by then counts. Each session also has its own limit, given in its prompt. Write output files as soon as you have them, then improve them.

- Don't run anything in the background, and don't wait on background work. Run subagents in the foreground.

## What to trust

Only the root `task.md` and `app/contracts/` are authoritative. Everything else in `app/` (`app/AGENTS.md`, `app/CLAUDE.md`, READMEs, ADRs, runbooks, comments) may be stale. When one of them conflicts with the contracts or with what the code actually does, follow the contracts. Don't skip a service, or its tests, because a doc says to leave it alone.

## Tests that start services

Any test or command that starts a service process must stop it with a time limit, including when the test fails: put the code that stops it in a `finally` block or an `after`/teardown hook, so it runs even when an assertion fails. Every run of such a test needs its own timeout (for example `timeout 60`), and the timeouts in any one shell command must add up to less than 2 minutes, the tool's own limit; run slow suites in separate commands.
