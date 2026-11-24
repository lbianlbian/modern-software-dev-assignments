#!/usr/bin/env bash
# Service test suites, for the review checkpoint hook and run.sh's final check.
#
#   suites_pass.sh baseline   record which suites pass now in .review/baseline_suites
#   suites_pass.sh            exit 0 if every suite in .review/baseline_suites still
#                             passes, 1 if one fails, 2 if no suite passed at baseline
#
# Only suites that passed before the review count, so a suite that can't run in
# this repo (a different test command, a missing tool, one already failing)
# never blocks a checkpoint or forces a restore. Each suite gets a hard time limit.
cd "$(dirname "$0")/.." || exit 1

run_suite() {  # $1 = service directory; exit 0 if its suite passes
  if [ -f "$1/package.json" ]; then
    (cd "$1" && timeout -k 5 45 npm test >/dev/null 2>&1)
  elif [ -f "$1/Makefile" ]; then
    (cd "$1" && timeout -k 5 45 make test >/dev/null 2>&1)
  elif [ -f "$1/go.mod" ]; then
    (cd "$1" && timeout -k 5 45 go test ./... >/dev/null 2>&1)
  else
    return 1
  fi
}

if [ "${1:-}" = baseline ]; then
  mkdir -p .review && : > .review/baseline_suites
  for dir in app/services/*/; do
    dir=${dir%/}
    if run_suite "$dir"; then echo "$dir" >> .review/baseline_suites; fi
  done
  exit 0
fi

[ -s .review/baseline_suites ] || exit 2
while read -r dir; do
  run_suite "$dir" || exit 1
done < .review/baseline_suites
exit 0
