"""Validate downloaded TLC parquet files for schema and quality."""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pyarrow.parquet as pq

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("validate_data")

REQUIRED_COLUMNS = {
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "PULocationID",
    "DOLocationID",
    "fare_amount",
    "trip_distance",
    "total_amount",
}

MAX_NULL_PCT = 5.0


def validate_file(path: Path) -> bool:
    log.info("Validating %s", path.name)
    try:
        pf = pq.ParquetFile(path)
    except Exception as exc:  # noqa: BLE001
        log.error("Cannot open %s: %s", path, exc)
        return False

    schema_cols = set(pf.schema.names)
    missing = REQUIRED_COLUMNS - schema_cols
    if missing:
        log.error("Missing columns in %s: %s", path.name, missing)
        return False

    table = pf.read()
    rows = table.num_rows
    log.info("  rows=%s", rows)
    if rows == 0:
        log.error("Empty file: %s", path.name)
        return False

    for col in ("fare_amount", "trip_distance"):
        column = table.column(col)
        nulls = column.null_count
        null_pct = (nulls / rows) * 100 if rows else 0
        if null_pct > MAX_NULL_PCT:
            log.error("Column %s has %.2f%% nulls (max %.1f%%)", col, null_pct, MAX_NULL_PCT)
            return False

    log.info("  OK")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="data/raw", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    files = sorted(args.input_dir.glob("*.parquet"))
    if not files:
        log.error("No parquet files found in %s", args.input_dir)
        return 1
    failures = sum(1 for f in files if not validate_file(f))
    if failures:
        log.error("%s files failed validation", failures)
        return 1
    log.info("All %s files passed validation", len(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
