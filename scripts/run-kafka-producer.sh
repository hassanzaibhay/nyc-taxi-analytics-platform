#!/usr/bin/env bash
# Launch the NYC taxi Kafka producer inside its container (profile: producer).
set -euo pipefail
echo "[$(date -Iseconds)] Starting Kafka producer container..."
docker compose --profile producer up --build kafka-producer
