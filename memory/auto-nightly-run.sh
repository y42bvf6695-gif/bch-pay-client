#!/usr/bin/env bash
set -euo pipefail
WORK_DIR="/home/open/.openclaw/workspace"
SCRIPT="memory/2026-03-25-nightly-improve-v2.py"
LOG="$WORK_DIR/memory/2026-03-25-nightly-run.log"

mkdir -p "$WORK_DIR/memory"

cd "$WORK_DIR"

LOCKFILE="/tmp/nightly-improve-run.lock"
exec 200>$LOCKFILE
flock -n 200 || exit 0

while true; do
  H=$(date +%H)
  if [ "$H" -ge 21 ] || [ "$H" -lt 5 ]; then
    if [ -f "$SCRIPT" ]; then
      python3 "$SCRIPT" >> "$LOG" 2>&1
    else
      echo "Script not found: $SCRIPT" >> "$LOG"
      exit 1
    fi
  fi
  sleep 60
done
