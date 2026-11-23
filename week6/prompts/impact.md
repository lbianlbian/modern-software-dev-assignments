# Your part: the impact report

You own `out/impact.json` and nothing else. Another session is fixing the code in `app/services` at the same time: don't edit anything in `app/`, and don't run the repo's checks or any service's test suites (they would run against code that is being changed). Keep your scripts in `out/`.

`out/original_services/` is a copy of `app/services` taken before either session started: the code that wrote the logs in `incident/`. The other session is changing `app/services` while you work, so if you need the service code, read it from `out/original_services/`. Like the checker's counts below, it is there in case you need it. Read only the parts you need, for example to learn what a log line means or how the old code wrote it. If `task.md`, `app/contracts/` and the logs already tell you enough, don't read it.

The report describes what happened in `incident/` under the old release. It doesn't depend on the fix.

## Impact report

- `out/generic_malformed_duplicate_check.json` was written before you started by a generic checker that was not written for this incident. For each file in `incident/` it gives the detected format, the number of malformed (cut-short) lines, the number of duplicate lines, and sample malformed lines. Nothing is removed from the logs.
- Its `definitions` field states exactly what it counted as malformed and duplicate. Use its counts only if the report needs those numbers and the definitions match `app/contracts/evidence.md` and `task.md`. Where they differ, a format is `unknown`, or the scan is missing, apply the contract's rules yourself.
- Compute every figure in the report with one script that implements `task.md`'s definitions. Don't type a count or total by hand.
- Wherever the script applies a rule from `app/contracts/evidence.md` (corrupted rows, duplicate batches, clocks, ordering), implement it literally and quote the sentence in a comment. Don't use a looser heuristic.
- Have the script print per-file counts and a few sample lines it rejected. Check that each sample really matches the rule before you write `out/impact.json`. Once it is written and checked, don't re-derive it again.

The task follows below.

---

