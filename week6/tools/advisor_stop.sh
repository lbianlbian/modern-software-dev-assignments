#!/usr/bin/env bash
# Stop hook for the main session (run.sh passes it with --settings).
# The first time the session tries to stop, block it once and ask for the
# advisor's review of the diff. The deadline lives here, not in the prompt:
# after 420s since run.sh started, let it stop without a review.
cd "$(dirname "$0")/.." || exit 0
input=$(cat)
log=.review/stop_hook.log
mkdir -p .review

if echo "$input" | grep -q '"stop_hook_active" *: *true'; then
  echo "$(date +%T) stop allowed: already continued once" >> "$log"; exit 0
fi
if [ -f .review/advised ]; then
  echo "$(date +%T) stop allowed: already asked for the review" >> "$log"; exit 0
fi
start=$(cat .review/start 2>/dev/null || echo 0)
elapsed=$(( $(date +%s) - start ))
if [ "$start" -eq 0 ] || [ "$elapsed" -gt 420 ]; then
  echo "$(date +%T) stop allowed: ${elapsed}s elapsed" >> "$log"; exit 0
fi

touch .review/advised
echo "$(date +%T) stop blocked at ${elapsed}s: asked for the review" >> "$log"
cat <<'EOF'
{"decision": "block", "reason": "Before finishing: run `diff -ruN .review/original_services app/services > .review/changes.diff`, call the advisor agent and ask it to review .review/changes.diff against task.md, and fix every gap it names. Re-run only the checks that cover what you changed. Also make sure out/impact.json exists. Then give the summary and stop."}
EOF
exit 0
