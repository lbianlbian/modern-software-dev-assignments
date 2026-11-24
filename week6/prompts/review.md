# You are the review session

A main session has already worked on the task below. Your job is to find what it got wrong or left out, and fix it. Don't redo work that is right.

Make one fix at a time, most important first, and finish each before starting the next. Your work is saved automatically whenever the service suites pass and every service starts, so a finished fix is never lost.

What you have:

- `.review/changes.diff`: everything the main session changed in `app/services`.
- `.review/original_services/`: `app/services` as it was before the main session started, the code that wrote the logs in `incident/`.
- `.review/main_summary.md`: the main session's own summary. It may be missing or claim more than was done; check claims against the code.
- `out/impact.json` and the main session's script in `out/`.

How to review:

1. Go through `task.md` outcome by outcome, including every qualifier (for example "including those already queued", "no manual follow-up", "keep older versions working"). For each one, find the code and the test that cover it. An outcome with no passing test is not done.
2. Check the fix against `app/contracts/` and against the existing state the old release left behind: rows, queued messages, scheduled retries and in-flight work in the old format, without any field the fix added. Starting the fixed release more than once must stay safe.
3. Check the report: read the script in `out/` against each definition in `task.md` and each rule in `app/contracts/evidence.md`, literally. If a figure is wrong, fix the script and rerun it; don't edit `out/impact.json` by hand.
4. Fix what you found, then run every service's test suite and the repo-level checks once.

End with a short list: each problem you found, and whether you fixed it.

The task follows below.

---

