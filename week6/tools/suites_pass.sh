#!/usr/bin/env bash
# Exit 0 if every service's test suite passes, 1 otherwise. Each suite gets a
# hard time limit, so a test that leaves a process running can't hang it.
# Used by the review checkpoint hook and by run.sh's final check.
cd "$(dirname "$0")/.." || exit 1
for dir in app/services/api app/services/router app/services/worker; do
  [ -d "$dir" ] || continue
  if [ -f "$dir/package.json" ]; then
    (cd "$dir" && timeout -k 5 45 npm test >/dev/null 2>&1) || exit 1
  elif [ -f "$dir/Makefile" ]; then
    (cd "$dir" && timeout -k 5 45 make test >/dev/null 2>&1) || exit 1
  fi
done
exit 0
