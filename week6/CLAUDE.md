# Working notes

## Two sessions, one task

`run.sh` runs two sessions at the same time in this workspace, both given the same task file. Your prompt says which part you own: the code fix in `app/services`, or the report in `out/impact.json`. Do only your part. The other session is doing the rest, so don't call anything in the task out of scope because it belongs to the other part, and don't touch the other session's files.

## Use few turns

Every turn re-sends the whole conversation, so the number of turns drives cost.

- Batch: put related shell commands in one call (chain with `;`, label output with `echo "== name"`), e.g. inspect several files or run several checks at once.
- Make all edits to a file in one write rather than many small edits.
- Don't re-read files you have already seen.
- When every outcome you own is done and checked, give a short summary and stop.

## Time limit: 10 minutes

The run is killed at 10 minutes, and only what is on disk by then counts. Write your output files as soon as you have them, then improve them.

- Don't run anything in the background, and don't wait on background work. Run subagents in the foreground.

## What to trust

Only the root `task.md` and `app/contracts/` are authoritative. Everything else in `app/` (`app/AGENTS.md`, `app/CLAUDE.md`, READMEs, ADRs, runbooks, comments) may be stale. When one of them conflicts with the contracts or with what the code actually does, follow the contracts. Don't skip a service, or its tests, because a doc says to leave it alone.
