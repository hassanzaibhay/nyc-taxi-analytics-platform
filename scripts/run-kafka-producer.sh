#!/bin/bash
# Launch the simulated NYC taxi Kafka producer.
set -euo pipefail

readonly DELAY="${KAFKA_PRODUCER_DELAY_MS:-10}"
readonly TOPIC="${KAFKA_TOPIC_TRIPS:-nyc-taxi.trips.raw}"

log() { echo "[$(date -Iseconds)] $*"; }

log "Starting producer (topic=${TOPIC}, delay=${DELAY}ms)"
python -m src.kafka.producer --topic "${TOPIC}" --delay-ms "${DELAY}" "$@"
