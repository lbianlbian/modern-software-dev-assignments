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

# The logs in incident/ came from the code as it is now. The repair session edits
# app/services while the impact session may read it, so keep an untouched copy for
# the impact session. A failure here must not stop the run.
rm -rf out/original_services
cp -r app/services out/original_services || echo "could not copy app/services; the impact session will read app/services" >&2

# Two sessions run in parallel, each owning one deliverable: the repair session
# changes app/services, the impact session writes out/impact.json. The report is
# computed from incident/ alone, so neither waits on the other, and each gets
# the whole time limit. No timeout here: the grader (and practice.py) stop the
# process group at 10 minutes and score whatever is on disk.
# Loop/wait tools have no use in a one-shot headless run and kept a finished
# session alive in practice, so they are disabled.
# Each line of output is prefixed with the session name so agent.log stays readable.
run_session() {
  local name=$1 role=$2
  claude -p "$(cat "$role")
$(cat "$TASK_FILE")" \
    --model claude-haiku-5-5 \
    --effort high \
    --permission-mode bypassPermissions \
    --disallowedTools "ScheduleWakeup CronCreate Monitor" \
    --output-format stream-json --verbose 2>&1 | sed -u "s/^/[$name] /" \
    || echo "[$name] claude exited with status $?" >&2
}

run_session impact prompts/impact.md &
run_session repair prompts/repair.md &
wait
