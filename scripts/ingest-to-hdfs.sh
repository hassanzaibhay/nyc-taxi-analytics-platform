#!/usr/bin/env bash
set -euo pipefail

echo "Creating HDFS directories..."
hdfs dfs -mkdir -p /data/nyc-taxi/raw

echo "Uploading Parquet files from /tmp/staging/ to HDFS..."
for f in /tmp/staging/*.parquet; do
    [ -f "$f" ] || continue
    filename=$(basename "$f")
    echo "  Uploading $filename..."
    hdfs dfs -put -f "$f" /data/nyc-taxi/raw/"$filename"
done

echo "Verifying upload..."
hdfs dfs -ls /data/nyc-taxi/raw/
echo "Ingest complete."
