#!/bin/bash
# Bootstraps the NameNode + ResourceManager.
set -euo pipefail

readonly NAME_DIR="/hadoop/dfs/name"

log() { echo "[$(date -Iseconds)] $*"; }

if [ ! -d "${NAME_DIR}/current" ]; then
    log "Formatting NameNode (first run)..."
    hdfs namenode -format -nonInteractive -force "${CLUSTER_NAME:-nyc-taxi}"
fi

log "Starting NameNode..."
hdfs --daemon start namenode

log "Starting ResourceManager..."
mkdir -p /opt/hadoop/logs
rm -f /tmp/hadoop-*-resourcemanager.pid
nohup yarn resourcemanager >/opt/hadoop/logs/rm.out 2>&1 &

log "Hadoop NameNode + ResourceManager up. Sleeping..."
exec tail -f /dev/null
