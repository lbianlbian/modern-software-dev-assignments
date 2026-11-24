#!/usr/bin/env bash
# Is the code in app/services in a state worth keeping? Used by the review
# checkpoint hook and by run.sh's final check.
#
#   state_ok.sh baseline   record which checks pass now in .review/baseline_checks
#   state_ok.sh            exit 0 if every check in .review/baseline_checks still
#                          passes, 1 if one fails, 2 if no check passed at baseline
#
# Checks: each service's test suite, and starting all services with app/bin/up
# (it builds them and waits for each health check). Unit suites alone aren't
# enough: an edit can stop a service from starting while its unit tests pass.
# Only checks that passed before the review count, so one that can't run in
# this repo never blocks a checkpoint or forces a restore.
cd "$(dirname "$0")/.." || exit 1
{ command -v python3 >/dev/null && PY=python3 || PY=python; } 2>/dev/null

run_suite() {  # $1 = service directory
  if [ -f "$1/package.json" ]; then
    (cd "$1" && timeout -k 5 30 npm test >/dev/null 2>&1)
  elif [ -f "$1/Makefile" ]; then
    (cd "$1" && timeout -k 5 30 make test >/dev/null 2>&1)
  elif [ -f "$1/go.mod" ]; then
    (cd "$1" && timeout -k 5 30 go test ./... >/dev/null 2>&1)
  else
    return 1
  fi
}

services_start() {  # start everything on a spare port range, then stop it all
  [ -f app/bin/up ] || return 1
  local state rc=0 pid
  state=$(mktemp -d)
  setsid timeout -k 5 40 "$PY" app/bin/up --state "$state" --port-base $((20000 + RANDOM % 20000)) >/dev/null 2>&1 &
  pid=$!
  wait "$pid" || rc=1
  # Each service runs in its own session, so stop them by the state directory
  # they were given (SWITCHYARD_STATE, from app/contracts/harness.md).
  kill -TERM -- "-$pid" 2>/dev/null
  for sig in TERM KILL; do
    for p in /proc/[0-9]*; do
      if { tr '\0' '\n' < "$p/environ"; } 2>/dev/null | grep -qxF "SWITCHYARD_STATE=$state"; then
        kill -"$sig" "${p#/proc/}" 2>/dev/null
      fi
    done
    sleep 1
  done
  rm -rf "$state"
  return $rc
}

run_check() {
  if [ "$1" = start ]; then services_start; else run_suite "$1"; fi
}

if [ "${1:-}" = baseline ]; then
  mkdir -p .review && : > .review/baseline_checks
  for dir in app/services/*/; do
    dir=${dir%/}
    if run_suite "$dir"; then echo "$dir" >> .review/baseline_checks; fi
  done
  if services_start; then echo start >> .review/baseline_checks; fi
  exit 0
fi

[ -s .review/baseline_checks ] || exit 2
while read -r check; do
  run_check "$check" || exit 1
done < .review/baseline_checks
exit 0
