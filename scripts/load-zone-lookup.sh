#!/usr/bin/env bash
# Load NYC TLC taxi zone lookup into analytics.taxi_zones.
set -euo pipefail

readonly CSV_HOST="data/taxi_zone_lookup.csv"
readonly CSV_CONTAINER="/tmp/taxi_zone_lookup.csv"
readonly PG_SERVICE="postgres"
readonly PG_DB="nyc_taxi"
readonly PG_USER="taxi_user"

if [[ ! -f "${CSV_HOST}" ]]; then
    echo "[$(date -Iseconds)] ERROR: ${CSV_HOST} not found. Run: curl -fsSL -o ${CSV_HOST} https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv" >&2
    exit 1
fi

echo "[$(date -Iseconds)] Copying CSV into postgres container..."
docker compose cp "${CSV_HOST}" "${PG_SERVICE}:${CSV_CONTAINER}"

echo "[$(date -Iseconds)] Ensuring table exists and loading rows..."
docker compose exec -T "${PG_SERVICE}" psql -U "${PG_USER}" -d "${PG_DB}" <<SQL
CREATE TABLE IF NOT EXISTS analytics.taxi_zones (
    location_id  INTEGER       PRIMARY KEY,
    borough      VARCHAR(50)   NOT NULL,
    zone_name    VARCHAR(100)  NOT NULL,
    service_zone VARCHAR(50)
);
TRUNCATE analytics.taxi_zones;
\copy analytics.taxi_zones(location_id, borough, zone_name, service_zone) FROM '${CSV_CONTAINER}' WITH (FORMAT csv, HEADER true);
SELECT COUNT(*) AS rows_loaded FROM analytics.taxi_zones;
SQL

echo "[$(date -Iseconds)] Done."
