# Assignment 6 (Writeup)

## Part I: Baseline

Run the provided `run.sh` on the starter incident (`python tools/practice.py`). Record the result below; add rows if you repeat it.

| Run | Repair | Impact | Cost | Model requests | Time |
| --- | ------ | ------ | ---- | -------------- | ---- |
| 1   | 0.44   | 1.00   | $1.3738 | 39           | 353.1 seconds |

**Tokens by kind**, averaged if you ran the baseline more than once:

| Model | Input | Output | Cache read | Cache write | Cost |
| ----- | ----- | ------ | ---------- | ----------- | ---- |
| claude-sonnet-5-5  | 80  | 41571   | 3705860       | 146836        | $1.3738 |

**Where did the money go?** Which kind of token dominated, and what in the run produced it:

> Cache writes were the largest cost while cache reads used the most tokens. This is becasue cache writes are more expensive. A totla of 59 cents was spent on cache writes. The cache writes came from everything the agent put into its context, and over a third came in the first five turns. That was the ~18k-token system prompt plus large cat commands on the workspace docs, including assignment.md and writeup.md, which don't help with the fix, and on whole service source files.

**What did the baseline get wrong?** Record scenarios passed per category and the impact report's precision and recall (averaged if you repeated the run). Then read the transcripts: what did the agent believe, and where did that belief come from?

| Category | Passed |
| -------- | ------ |
| incident     | 4/9   |
| regressions | 10/10 |
| compat | 2/2|

> Precision: 1, Recall: 1. The impact report was perfect, but the repair only half-worked. The agent correctly found the root cause: 2.3.1 kept idempotency keys in each api process's memory, so a retry that hit a restarted process or a different replica (production runs 3, and the logs show 56 api.started lines) was accepted as a new event. It moved the key check into the database, which passed all four "retry after api stop/restart" scenarios. It failed all five scenarios where duplicates were created while 2.3.1 was running and then the release was replaced: retries already queued, deliveries in flight, multiple payments, and starting the new release twice. The agent believed those were out of scope. Its summary says "repeats already routed without a key, from the old api, are not cancelled automatically. Nothing tells the router about them after the fact." That belief came from its own design: it only flagged repeats through new fields on bus messages. That ignores the task's explicit "including those already queued for delivery… No manual follow-up", even though the agent had seen that the events table already stored idempotency_key and could have cancelled old repeats on startup. The stale AGENTS.md/CLAUDE.md (at-most-once delivery, bus version 2) also led it to "leave worker behavior alone" and skip the worker tests. Its own new scenarios only covered the cases it had in mind, so they passed and gave it false confidence.

## Part II: Experiments

### Run result 2
on graded run, most recent setup got 
run.sh exited with code 0 after 297.8s
repair 1.00
  incident    17 of 17 scenarios passed
  regressions 51 of 51 scenarios passed
  compat      8 of 8 scenarios passed
impact 0.93
the run did not pass (a pass needs repair 1.00 and impact 1.00)

cost $0.0509, model requests: 12
  claude-haiku-5-5: $0.0509  in 24  out 58,797  cache read 687,798  cache write 116,988
cost is scored only for a run that passes

### Run result 3
run.sh exited with code 0 after 322.9s
repair 0.76
  incident    13 of 17 scenarios passed
  regressions 51 of 51 scenarios passed
  compat      8 of 8 scenarios passed
impact 1.00
the run did not pass (a pass needs repair 1.00 and impact 1.00)

cost $0.0632, model requests: 17
  claude-haiku-5-5: $0.0632  in 34  out 66,182  cache read 1,251,543  cache write 141,010
baseline $1.5000; full credit at or below $0.7500

Still have 2 more tries
try one claude session for impact and one claude session for repair
try fresh sessions for review, maybe different model/provider
maybe play around with higher effort, still have a max effort setting not used


One row per change you tried, including the ones you dropped. Try to run each change a few times to check its reliability; report how many runs you made.

| #   | Change | Why you expected it to help | Runs passed / attempted | Avg repair / impact | Avg cost | Kept? |
| --- | ------ | --------------------------- | ----------------------- | ------------------- | -------- | ----- |
| 1   | Delete writeup.md and assignment.md | It is context that uses up token cost that the agent doesn't need. It did make the runs more expensive and accurate, but I think that is due to chance that these runs tried harder than the baseline run. If there was a model seed that had been set, I think these would be cheaper. | 2/2   | 1/1   | $1.7715 | Yes  |
| 2   | Root CLAUDE.md telling the agent to grep and read line ranges (`sed -n`) instead of cat-ing whole files and docs | Whole-file reads were a big part of the early cache writes; smaller reads should shrink the context every later turn re-sends | 1/2 | 0.72 / 1.00 | $1.7137 | No. The agent did comply (sed -n reads rose from 1-2 to 14-17 per run) but made more requests (51-56 vs 37-48): small reads turned into extra turns, each re-reading the whole context, so cost didn't drop. One run fell back to the narrow fix (4/9 incident). |
| 3   | Root CLAUDE.md telling the agent to use few turns: batch related shell commands into one call, make all edits to a file in one write, don't re-read files or re-run checks, stop once checks pass | Every turn re-sends the whole context as cache reads, so cost scales with the number of turns more than with the size of any single read (the lesson from #2) | 2/2 | 1.00 / 1.00 | $1.2770 | Yes. Requests fell from 37-48 to 25-32 and cache reads from 3.9-5.4M to 2.0-3.3M per run; both runs still fixed all 9 incident scenarios. |
| 4   | On top of #3: CLAUDE.md section "Before you stop": re-read task.md, list every outcome incl. qualifiers like "already ..."/"no manual follow-up", state what satisfies each, fix rather than call it out of scope | The baseline failures came from the agent declaring already-queued repeats out of scope despite the task asking for them | 1/2 | 0.72 / 1.00 | $1.0074 | No. Cheaper (24 requests per run) but one run still failed the 5 old-release scenarios. Its summary claims queued repeats are cancelled, yet it detected repeats through a new key field on bus messages that the old release never sent, so the checklist produced a confident claim rather than a real check. |
| 5   | On top of #3: CLAUDE.md section "Fixes ship into a running system": the old release has already written rows, queued messages, retries and in-flight work in the old format, without any new field; the fix must handle that state at startup, be safe to start twice, and be tested by creating the bad state with old code first. Worded generally, not about this incident | Every failed run (baseline, #2, #4) missed the same 5 "release is replaced" scenarios because its fix depended on data only the new code produces | 2/2 | 1.00 / 1.00 | $1.0670 | Yes. Both runs passed all 9 incident scenarios at 25-30 requests. It points the agent at the class of mistake (forgetting existing state) instead of at this ticket, so it should carry over to other incidents that involve a deploy. |
| 6   | On top of #5: run.sh runs `npm test` (api) and `make test` (router, worker) after claude exits; if any fail it resumes the session (`claude -p --continue`) with the failing output, and starts no new retry after 8 minutes | The baseline never ran the per-service suites (only bin/evaluate) and skipped the worker entirely; a deterministic check costs nothing when tests pass and only pays for a retry when they fail | 1/2 | 1.00 / 0.97 | $0.9690 | No (by the rule of keeping only changes where both runs pass). The loop never fired: all three suites passed after the first call in both runs, so the agent's behavior was unchanged. The failed run got 5/6 report figures right, which is ordinary report variance, not caused by this change. The existing suites didn't catch the baseline's failures either (regressions were already 10/10), so this is insurance against breaking something, not a fix for the incident scenarios. |
| 7   | On top of #5: CLAUDE.md section "What to trust": only task.md and app/contracts/ are authoritative; app/AGENTS.md, app/CLAUDE.md, READMEs, ADRs may be stale; follow the contracts on conflict and don't skip a service or its tests because a doc says so | In the baseline the stale app/AGENTS.md (at-most-once delivery, bus version 2) led the agent to leave the worker alone and skip its tests; the assignment's Trusted Sources section says the same thing | 2/2 | 1.00 / 1.00 | $0.8433 | Yes. Both runs passed at 19-24 requests, the cheapest so far. The change in visible behavior is modest (doc-reading commands 0-3 vs 3-4 per run with #5, the test suite run in both), so part of the drop from $1.07 may be run-to-run variance; it is kept because it costs nothing and generalizes to any incident where repo docs drift from the contracts. |
| 8   | On top of #7: switch run.sh from claude-sonnet-5-5 to claude-haiku-5-5 (same CLAUDE.md, same effort) | The setup from #7 now steers the agent toward the right fix, so a model 20x cheaper per token might carry it out; Haiku keeps the same harness and CLAUDE.md, unlike gpt-6.1-terra which would need Codex and an AGENTS.md | 2/2 | 1.00 / 1.00 | $0.1570 | Yes, with a caveat: both runs hit the 10-minute limit and were killed (600s). They passed only because the repair and out/impact.json were already written. Haiku made far more tool calls (60-73 vs 19-24), produced 5x the output tokens, kept re-verifying after the work was done, and even called ScheduleWakeup and spawned a subagent. On a harder held-out incident it may not finish in time. |
| 9   | On top of #8, after the first graded run failed because run.sh did not exit within 10 minutes: run.sh wraps claude in `timeout -k 15 540` and disables ScheduleWakeup/CronCreate/Monitor; CLAUDE.md gets an ~8-minute time budget (write out/impact.json early and don't re-check it, run bin/evaluate and the suites once at the end and ignore app docs that say to run them after every change, no background work, stop after the summary) and the old-release test becomes one small targeted test instead of a full replay | The grader gives no result unless run.sh exits within 10 minutes, but practice.py still scores killed runs, which hid the problem. Haiku's long runs had three causes: app/AGENTS.md telling it to run bin/evaluate after every change, our own #5 wording that led to a 5-minute full-release replay, and a background subagent plus ScheduleWakeup keeping a finished session alive | 2/3 | 1.00 / 0.67 | $0.0703 | Yes. Run 1 passed and exited on its own at 300s with 18 requests ($0.077). Run 2 had a correct repair (9/9, 10/10, 2/2) but no report: the laptop went into standby 4.6 minutes in (Windows Kernel-Power events 506/507, 2:56-3:03 PM), the in-flight model request stalled, and the 9-minute guard stopped claude so run.sh still exited cleanly. Because that failure was environmental, I ran a third time with sleep disabled: it passed and exited on its own at 265s with 9 requests ($0.064). Excluding the standby run, 2/2 passed, exiting at 265-300s, well inside the limit. The guard is required for the grader regardless. |
| 10  | On top of #9, after the graded run scored impact 0.93: run.sh first runs `tools/generic_malformed_duplicate_check.py`, a deterministic script with no model calls. For each file in incident/ it detects the format and counts malformed (cut-short) lines and exact duplicate lines into `out/generic_malformed_duplicate_check.json`. The JSON states its own definitions (e.g. a csv row is malformed only if it has fewer fields than the header, and blank cells still count as fields). CLAUDE.md says to use the counts only if the report needs them and the definitions match evidence.md/task.md. An earlier version marked the counts untrusted unless evidence.md's hash matched the practice copy; I dropped that because it would almost always be off on a held-out incident, and the label "untrusted" would make the agent ignore useful context | The graded run lost impact points on the report, not the repair. Counting corrupted and duplicate log lines is where a hand-written script can quietly be wrong, so a deterministic count with stated definitions gives the agent something to check its own script against | 2/2 | 1.00 / 1.00 | $0.0916 | Yes. Both runs passed with 6/6 figures right, at 21-22 requests and 345-418s, and the agent read the JSON in every run. A third run is excluded: WSL's non-interactive shell didn't have nvm's `node` on PATH, so the scorer couldn't run any scenario (repair 0.00, impact 1.00). Cost is up from #9 ($0.064-0.077, 9-18 requests). That is probably run-to-run variance in how long Haiku verifies, but it means this change didn't save money. Impact was already 1.00 on the starter incident, so the starter can't show whether this helps; its value is for the held-out incident's report. |

**The change that fixed the most failing categories**, and why it worked:

> TODO

**The change that saved the most money**, and why it worked:

> TODO

**A change that did not work**, and what it showed you:

> TODO

**Your final setup.** What `run.sh` does, step by step, and which model handles each step:

> TODO

**Final setup on the starter incident.** Record your results; add rows for repeated runs. Briefly explain any variation you observed.

| Run | Repair | Impact | Cost |
| --- | ------ | ------ | ---- |
| 1   | TODO   | TODO   | TODO |

**What will transfer?** The held-out task is a different incident in Switchyard. Which parts of your setup are about how to work in this repository and its evidence, and which might only have helped with duplicate events:

> TODO

## Part III: Graded Submissions

Upload a zip of your `week6/` folder to the **Assignment 6 (Autograder)** assignment on Gradescope (up to 3 submissions, one run each) and report your autograder scores.

| Submission (up to 3, one run each) | Repair | Impact | Passed? | Cost | What you changed before it |
| ---------------------------------- | ------ | ------ | ------- | ---- | -------------------------- |
| 1                                  | TODO   | TODO   | TODO    | TODO | n/a                        |
| 2                                  | TODO   | TODO   | TODO    | TODO | TODO                       |
| 3                                  | TODO   | TODO   | TODO    | TODO | TODO                       |

**Starter incident versus held-out incident.** Did repair, impact and cost carry over? If not, give your best explanation, accounting for each submission having only one graded run:

> TODO

## Submission

1. `Command (⌘) + F` for `TODO`. No results means you're done. Delete rows you did not need.
2. Push all changes to your remote repository and submit the repository link to the **Assignment 6 (Writeup)** assignment on Gradescope. You can resubmit it as often as you like; your `week6/` folder goes to the separate **Assignment 6 (Autograder)** assignment (up to 3 submissions).
