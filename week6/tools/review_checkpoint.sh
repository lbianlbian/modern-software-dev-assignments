#!/usr/bin/env bash
# PostToolUse hook for the review session only (run.sh passes it with --settings).
# After each tool call that changed app/services or out/impact.json, run the
# checks in tools/state_ok.sh; if they pass, save both as the latest checkpoint.
# Silent to the agent either way: a fix that spans several files fails in
# between edits, and reporting that would only distract.
cd "$(dirname "$0")/.." || exit 0
cat >/dev/null  # the hook's JSON input is not needed

# Skip the checks when nothing has changed since the last one (most tool calls
# only read files). Build output, caches and service state don't count.
hash=$( { find app/services -type f \
            -not -path '*/node_modules/*' -not -path '*/__pycache__/*' \
            -not -path '*/state/*' -not -path '*/.build/*' -not -name '*.log' \
            -print0 | sort -z | xargs -0 cat 2>/dev/null; cat out/impact.json 2>/dev/null; } | md5sum)
[ "$hash" = "$(cat .review/last_hash 2>/dev/null)" ] && exit 0
echo "$hash" > .review/last_hash

rc=0; bash tools/state_ok.sh || rc=$?
if [ "$rc" -eq 0 ]; then
  echo "$(date +%T) checks pass: checkpoint saved" >> .review/checkpoints.log
  rm -rf .review/checkpoint.tmp && mkdir -p .review/checkpoint.tmp
  cp -r app/services .review/checkpoint.tmp/services
  cp out/impact.json .review/checkpoint.tmp/impact.json 2>/dev/null
  rm -rf .review/checkpoint && mv .review/checkpoint.tmp .review/checkpoint
elif [ "$rc" -eq 1 ]; then
  echo "$(date +%T) checks fail: no checkpoint" >> .review/checkpoints.log
fi
exit 0
