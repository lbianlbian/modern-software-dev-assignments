#!/usr/bin/env bash
# PostToolUse hook for the review session only (run.sh passes it with --settings).
# After each Edit/Write, if every suite that passed before the review still passes, save app/services and
# out/impact.json as the latest checkpoint. Silent either way: a fix that spans
# several files fails in between edits, and reporting that would only distract.
cd "$(dirname "$0")/.." || exit 0
cat >/dev/null  # the hook's JSON input is not needed
rc=0; bash tools/suites_pass.sh || rc=$?
if [ "$rc" -eq 0 ]; then
  echo "$(date +%T) suites pass: checkpoint saved" >> .review/checkpoints.log
  rm -rf .review/checkpoint.tmp && mkdir -p .review/checkpoint.tmp
  cp -r app/services .review/checkpoint.tmp/services
  cp out/impact.json .review/checkpoint.tmp/impact.json 2>/dev/null
  rm -rf .review/checkpoint && mv .review/checkpoint.tmp .review/checkpoint
elif [ "$rc" -eq 1 ]; then
  echo "$(date +%T) suites fail: no checkpoint" >> .review/checkpoints.log
fi
exit 0
