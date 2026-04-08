#!/bin/bash
# Submit a Spark job to the local cluster.
# Usage: submit-spark-job.sh <job_name>
#   where <job_name> is one of: trip_analytics | revenue_aggregation |
#                                fare_prediction_features | realtime_demand
set -euo pipefail

readonly JOB="${1:?Usage: $0 <job_name>}"
readonly MASTER="${SPARK_MASTER_URL:-spark://spark-master:7077}"
readonly INPUT="${SPARK_INPUT:-hdfs://namenode:8020/data/nyc-taxi/raw}"

log() { echo "[$(date -Iseconds)] $*"; }

case "${JOB}" in
    trip_analytics|revenue_aggregation)
        APP="/opt/src/spark/batch/${JOB}.py"
        EXTRA_ARGS=("--input" "${INPUT}")
        ;;
    fare_prediction_features)
        APP="/opt/src/spark/batch/${JOB}.py"
        EXTRA_ARGS=("--input" "${INPUT}" "--output" "${SPARK_OUTPUT:-hdfs://namenode:8020/data/nyc-taxi/features}")
        ;;
    realtime_demand)
        APP="/opt/src/spark/streaming/${JOB}.py"
        EXTRA_ARGS=()
        ;;
    *)
        echo "Unknown job: ${JOB}" >&2
        exit 2
        ;;
esac

log "Submitting Spark job: ${JOB}"

docker compose exec -T -e PYTHONPATH=/opt spark-master /opt/spark/bin/spark-submit \
    --master "${MASTER}" \
    --conf spark.executorEnv.PYTHONPATH=/opt \
    --packages org.postgresql:postgresql:42.7.4,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.4 \
    "${APP}" --master "${MASTER}" "${EXTRA_ARGS[@]}"
