#!/usr/bin/env bash
# Entry point. The grader runs `./run.sh task.md` from this directory, with no
# terminal attached and nobody to answer questions. When this script exits,
# app/services/api, app/services/router and app/services/worker are scored,
# and so is out/impact.json.
#
# One Haiku session does the whole task, following CLAUDE.md. It calls a Sonnet advisor subagent
# (.claude/agents/advisor.md, read-only): first for a plan for the fix, and
# on stop for a review of the diff. A Stop hook (prompts/main_settings.json ->
# tools/advisor_stop.sh) blocks the first stop once to ask for the diff review, if there is still time.
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

# The code as it was before the session, for the diff the advisor reviews, and the
# start time the Stop hook measures its deadline from.
rm -rf .review; mkdir -p .review
cp -r app/services .review/original_services || echo "could not copy app/services" >&2
date +%s > .review/start

# Subagents and shell commands run in the foreground, so an advisor call blocks
# until its reply arrives and the session can't end its turn to wait on one.
export CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1

# Stopped at 9 minutes (CLAUDE.md tells it so), inside the grader's 10-minute limit.
timeout -k 15 540 claude -p "$(cat "$TASK_FILE")" --model claude-haiku-5-5 --effort high \
  --settings prompts/main_settings.json \
  --permission-mode bypassPermissions \
  --disallowedTools "ScheduleWakeup CronCreate Monitor" \
  --output-format stream-json --verbose 2>&1 \
  || echo "claude exited with status $? (124 = stopped at 9 minutes)" >&2

sed "s/^/[stop hook] /" .review/stop_hook.log 2>/dev/null || echo "[stop hook] never ran"
exit 0
