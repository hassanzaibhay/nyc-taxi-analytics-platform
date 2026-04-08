#!/bin/bash
# Block until HDFS is ready to accept commands.
set -euo pipefail

readonly MAX_ATTEMPTS=60

log() { echo "[$(date -Iseconds)] $*"; }

log "Waiting for HDFS to leave safe mode..."
for i in $(seq 1 "${MAX_ATTEMPTS}"); do
    if hdfs dfsadmin -safemode get 2>/dev/null | grep -q "OFF"; then
        log "HDFS is ready."
        exit 0
    fi
    sleep 2
done

log "ERROR: HDFS did not become ready in time." >&2
exit 1
