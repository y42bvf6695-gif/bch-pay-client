#!/usr/bin/env bash
set -euo pipefail
WORK_DIR="/home/open/.openclaw/workspace"
SCRIPT="memory/2026-03-25-nightly-improve-v2.py"
LOG="$WORK_DIR/memory/2026-03-25-nightly-run-robust.log"
LOCKFILE="/tmp/nightly-robust.lock"

mkdir -p "$WORK_DIR/memory"

cd "$WORK_DIR"

# Acquire a non-blocking lock to prevent multiple instances
exec 200>$LOCKFILE
flock -n 200 || exit 0

while true; do
  H=$(date +%H)
  if [ "$H" -ge 21 ] || [ "$H" -lt 5 ]; then
    if [ -f "$SCRIPT" ]; then
      echo "$(date '+%Y-%m-%d %H:%M:%S') - Running: $SCRIPT" >> "$LOG"
      python3 "$SCRIPT" >> "$LOG" 2>&1 || {
        echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: script failed" >> "$LOG"
      }
    else
      echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: Script not found: $SCRIPT" >> "$LOG"
    fi
  fi
  sleep 900  # 15 minutes
done
