#!/usr/bin/env bash
# Entry point. The grader runs `./run.sh task.md` from this directory, with no
# terminal attached and nobody to answer questions. When this script exits,
# app/services/api, app/services/router and app/services/worker are scored,
# and so is out/impact.json.
#
# This is the baseline: one Claude Code call on the medium model with default
# settings. Change anything you like.
#
# --output-format stream-json --verbose prints every turn as it happens, so
# practice.py's agent.log has the whole session even if the run is stopped at
# the time limit. It changes only what is printed, not what is sent to the model.

set -euo pipefail

TASK_FILE="${1:?usage: ./run.sh <task-file>}"
cd "$(dirname "$0")"

rm -f writeup.md assignment.md rate_card.json

# Describe the evidence packet before the agent starts: each file's format and its
# malformed and duplicate line counts, in out/generic_malformed_duplicate_check.json. Deterministic and
# free (no model calls); a failure here must not stop the run.
mkdir -p out
{ command -v python3 >/dev/null && PY=python3 || PY=python; } 2>/dev/null
"$PY" tools/generic_malformed_duplicate_check.py || echo "generic_malformed_duplicate_check failed; the agent will apply evidence.md itself" >&2

# Keep the code as it was before any session, for the reviewer.
rm -rf .review; mkdir -p .review
cp -r app/services .review/original_services || echo "could not copy app/services" >&2

CLAUDE_FLAGS=(--permission-mode bypassPermissions
  --disallowedTools "ScheduleWakeup CronCreate Monitor"
  --output-format stream-json --verbose)

# 1. Main session (Haiku, high effort): the whole task, stopped at 7 minutes
#    (a backstop; its prompt gives a soft 5-minute aim and never mentions the review).
#    Its output goes to agent.log with a [main] prefix and to a file, so the
#    reviewer can read its final summary.
timeout -k 10 420 claude -p "$(cat prompts/main.md)
$(cat "$TASK_FILE")" --model claude-haiku-5-5 --effort high "${CLAUDE_FLAGS[@]}" 2>&1 \
  | tee .review/main.jsonl | sed -u "s/^/[main] /" \
  || echo "[main] claude exited with status $? (124 = stopped at 7 minutes)" >&2

# 2. Review session (Sonnet, high effort) with whatever time is left, until about
#    520s (its prompt gives a soft 3-minute aim, nothing about a cut-off). A hook (prompts/review_settings.json)
#    saves a checkpoint after each tool call that leaves the suites passing and
#    every service starting (tools/state_ok.sh). At the end, if the final code
#    fails those checks, the latest checkpoint (or the main session's work)
#    is restored. The final check is capped at 45s and the restore is a swap, so
#    the run ends well before the grader's 10-minute limit.
REVIEW_SECONDS=$((520 - SECONDS))
if [ "$REVIEW_SECONDS" -lt 60 ]; then
  echo "[review] skipped: only ${REVIEW_SECONDS}s left" >&2
  exit 0
fi
"$PY" - .review/main.jsonl .review/main_summary.md <<'PYEOF' || true
import json, sys
text = ""
for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    try:
        m = json.loads(line)
    except ValueError:
        continue
    if m.get("type") == "result" and m.get("result"):
        text = m["result"]
    elif m.get("type") == "assistant":
        for c in m.get("message", {}).get("content", []):
            if c.get("type") == "text":
                text = c["text"]
open(sys.argv[2], "w", encoding="utf-8").write(text or "(the main session left no summary)\n")
PYEOF
diff -ruN .review/original_services app/services > .review/changes.diff || true
bash tools/state_ok.sh baseline || true
sed "s/^/[review] check passing before review: /" .review/baseline_checks || true
mkdir -p .review/checkpoint
cp -r app/services .review/checkpoint/services
cp out/impact.json .review/checkpoint/impact.json 2>/dev/null || true

timeout -k 5 "$REVIEW_SECONDS" claude -p "$(cat prompts/review.md)
$(cat "$TASK_FILE")" --model claude-sonnet-5-5 --effort high --settings prompts/review_settings.json \
  "${CLAUDE_FLAGS[@]}" 2>&1 | sed -u "s/^/[review] /" \
  || echo "[review] claude exited with status $? (124 = stopped at its time limit)" >&2

# A hook still running when the reviewer was stopped must not race the final check.
pkill -f tools/review_checkpoint.sh 2>/dev/null || true
sed "s/^/[review hook] /" .review/checkpoints.log 2>/dev/null || echo "[review hook] never ran"
rc=0; timeout -k 5 45 bash tools/state_ok.sh || rc=$?
if [ "$rc" -eq 0 ]; then
  echo "[review] final code passes the checks; keeping it" >&2
elif [ "$rc" -eq 2 ]; then
  echo "[review] no check passed before the review, so nothing to check against; keeping the final code" >&2
else
  # rc 1: a check that passed before the review now fails; 124/137: the check
  # itself hung, which also means something is wrong. Restore the last
  # checkpoint, which passed every check. Copy first, then swap, so the code is
  # never missing if the run is stopped part-way.
  echo "[review] final code fails or hangs a check (status $rc); restoring the last checkpoint" >&2
  if [ -d .review/checkpoint/services ]; then
    rm -rf app/services.restore app/services.old
    cp -r .review/checkpoint/services app/services.restore       && mv app/services app/services.old && mv app/services.restore app/services       && rm -rf app/services.old
  fi
  if [ -f .review/checkpoint/impact.json ]; then
    cp .review/checkpoint/impact.json out/impact.json.restore && mv out/impact.json.restore out/impact.json
  fi
fi
exit 0
