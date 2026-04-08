#!/bin/bash
# Submit the zone-aggregation Hadoop Streaming job.
set -euo pipefail

readonly INPUT="${HDFS_INPUT:-/data/nyc-taxi/csv}"
readonly OUTPUT="${HDFS_OUTPUT:-/data/nyc-taxi/output/zone-agg-$(date +%Y%m%d%H%M%S)}"
readonly STREAMING_JAR="${HADOOP_STREAMING_JAR:-/opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.1.jar}"

log() { echo "[$(date -Iseconds)] $*"; }

log "Submitting Hadoop Streaming job"
log "  input=${INPUT}"
log "  output=${OUTPUT}"

docker compose exec -T namenode hadoop jar "${STREAMING_JAR}" \
    -files /opt/mapreduce/mapper_zone_aggregation.py,/opt/mapreduce/reducer_zone_aggregation.py \
    -mapper "/usr/bin/python3 mapper_zone_aggregation.py" \
    -reducer "/usr/bin/python3 reducer_zone_aggregation.py" \
    -input "${INPUT}" \
    -output "${OUTPUT}"

log "Job complete: ${OUTPUT}"
