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

potential things to try 
- Have run.sh delete assignment.md and writeup.md from the workspace before the agent starts.
- Tell the agent to read targeted parts of files instead of whole files.
- Use fewer turns, since every turn re-reads the full context.
- Tell the agent to check every requirement in the task before stopping.
- Tell it to always consider state the old release left behind at deploy time.
- Have it run all three services' test suites.
- Point out that the docs inside app/ may be stale.

One row per change you tried, including the ones you dropped. Try to run each change a few times to check its reliability; report how many runs you made.

| #   | Change | Why you expected it to help | Runs passed / attempted | Avg repair / impact | Avg cost | Kept? |
| --- | ------ | --------------------------- | ----------------------- | ------------------- | -------- | ----- |
| 1   | TODO   | TODO                        | TODO                    | TODO                | TODO     | TODO  |
| 2   | TODO   | TODO                        | TODO                    | TODO                | TODO     | TODO  |
| 3   | TODO   | TODO                        | TODO                    | TODO                | TODO     | TODO  |

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
