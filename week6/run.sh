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

# 1. Main session (Haiku, max effort): the whole task, stopped at 7 minutes.
#    Its output goes to agent.log with a [main] prefix and to a file, so the
#    reviewer can read its final summary.
timeout -k 10 420 claude -p "$(cat prompts/main.md)
$(cat "$TASK_FILE")" --model claude-haiku-5-5 --effort max "${CLAUDE_FLAGS[@]}" 2>&1 \
  | tee .review/main.jsonl | sed -u "s/^/[main] /" \
  || echo "[main] claude exited with status $? (124 = stopped at 7 minutes)" >&2

# 2. Review session (Sonnet, high effort) with whatever time is left, ending
#    about 25s before the grader's 10-minute limit. If it runs out of time, its
#    half-finished changes are thrown away and the main session's work is kept.
REVIEW_SECONDS=$((575 - SECONDS))
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
cp -r app/services .review/pre_review_services
cp out/impact.json .review/pre_review_impact.json 2>/dev/null || true

status=0
timeout -k 5 "$REVIEW_SECONDS" claude -p "$(sed "s/REVIEW_SECONDS/$((REVIEW_SECONDS - 30))/" prompts/review.md)
$(cat "$TASK_FILE")" --model claude-sonnet-5-5 --effort high "${CLAUDE_FLAGS[@]}" 2>&1 \
  | sed -u "s/^/[review] /" || status=$?
if [ "$status" -eq 124 ] || [ "$status" -eq 137 ]; then
  echo "[review] stopped at its time limit; restoring the main session's work" >&2
  rm -rf app/services && cp -r .review/pre_review_services app/services
  if [ -f .review/pre_review_impact.json ]; then cp .review/pre_review_impact.json out/impact.json; fi
fi
exit 0
