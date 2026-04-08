#!/bin/bash
# Bootstraps the DataNode + NodeManager.
set -euo pipefail

log() { echo "[$(date -Iseconds)] $*"; }

log "Waiting for NameNode at namenode:8020..."
until (echo > /dev/tcp/namenode/8020) >/dev/null 2>&1; do
    sleep 2
done

log "Starting DataNode..."
hdfs --daemon start datanode

log "Starting NodeManager..."
mkdir -p /opt/hadoop/logs
rm -f /tmp/hadoop-*-nodemanager.pid
nohup yarn nodemanager >/opt/hadoop/logs/nm.out 2>&1 &

log "Hadoop DataNode + NodeManager up. Sleeping..."
exec tail -f /dev/null
