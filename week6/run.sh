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

# The grader only scores runs whose run.sh exits within 10 minutes, so stop the
# agent at 9 (-k: force-kill 15s later if it ignores SIGTERM). Whatever it has
# written to app/services and out/ by then is what gets scored.
# Loop/wait tools have no use in a one-shot headless run and kept a finished
# session alive in practice, so they are disabled.
timeout -k 15 540 claude -p "$(cat "$TASK_FILE")" \
  --model claude-haiku-5-5 \
  --effort high \
  --permission-mode bypassPermissions \
  --disallowedTools "ScheduleWakeup CronCreate Monitor" \
  --output-format stream-json --verbose || echo "claude exited with status $? (124 = stopped at 9 minutes)" >&2
