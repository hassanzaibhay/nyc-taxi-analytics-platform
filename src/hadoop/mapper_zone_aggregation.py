#!/usr/bin/env python3
"""Mapper: emit (zone_id, hour) keys with fare and distance for aggregation.

Reads CSV trip records from stdin, emits tab-separated key-value pairs.
Designed for Hadoop Streaming. Bad rows are skipped and reported on stderr.

Output format:
    PULocationID\\thour    fare\\tdistance\\t1
"""

import sys

# CSV column indices for the NYC TLC yellow taxi schema (after parquet → csv).
COL_PICKUP_DT = 1
COL_PU_LOCATION = 7
COL_FARE = 10
COL_DISTANCE = 4

HEADER_TOKENS = ("vendorid", "VendorID")


def parse_hour(value: str) -> str:
    """Return ``YYYY-MM-DDTHH`` from a TLC datetime string.

    Spark CSV writes ``2024-03-01T00:18:51.000`` — the first 13 chars are
    already the hour key, so slice directly (no datetime parsing needed).
    """
    s = value.strip().replace(" ", "T")
    if len(s) < 13:
        raise ValueError(f"datetime too short: {s!r}")
    return s[:13]


def emit(zone_id: str, hour: str, fare: float, distance: float) -> None:
    sys.stdout.write(f"{zone_id}\t{hour}\t{fare}\t{distance}\t1\n")


def main() -> None:
    bad_rows = 0
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line or line.startswith(HEADER_TOKENS):
            continue
        try:
            parts = line.split(",")
            zone_id = parts[COL_PU_LOCATION].strip()
            hour = parse_hour(parts[COL_PICKUP_DT])
            fare = float(parts[COL_FARE])
            distance = float(parts[COL_DISTANCE])
            if fare <= 0 or distance <= 0:
                bad_rows += 1
                continue
            emit(zone_id, hour, fare, distance)
        except (IndexError, ValueError) as exc:
            bad_rows += 1
            if bad_rows <= 10:
                sys.stderr.write(f"reporter:counter:taxi,bad_rows,1\nSkipping row: {exc}\n")

    if bad_rows:
        sys.stderr.write(f"Total bad rows skipped: {bad_rows}\n")


if __name__ == "__main__":
    main()
