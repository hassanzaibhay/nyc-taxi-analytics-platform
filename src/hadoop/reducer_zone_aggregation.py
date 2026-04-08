#!/usr/bin/env python3
"""Reducer: aggregate trips per (zone_id, hour) into counts and averages.

Expects mapper output sorted by key on stdin. Emits one line per key.

Output format:
    zone_id\\thour\\ttrip_count\\tavg_fare\\tavg_distance
"""
import sys
from typing import Optional


def emit(key: str, count: int, total_fare: float, total_distance: float) -> None:
    if count == 0:
        return
    avg_fare = total_fare / count
    avg_distance = total_distance / count
    sys.stdout.write(f"{key}\t{count}\t{avg_fare:.4f}\t{avg_distance:.4f}\n")


def main() -> None:
    current_key: Optional[str] = None
    count = 0
    total_fare = 0.0
    total_distance = 0.0

    for raw_line in sys.stdin:
        line = raw_line.rstrip("\n")
        if not line:
            continue
        try:
            zone_id, hour, fare_s, distance_s, count_s = line.split("\t")
        except ValueError as exc:
            sys.stderr.write(f"Skipping malformed reducer input: {exc}\n")
            continue

        key = f"{zone_id}\t{hour}"
        try:
            fare = float(fare_s)
            distance = float(distance_s)
            cnt = int(count_s)
        except ValueError:
            continue

        if current_key is None:
            current_key = key

        if key != current_key:
            emit(current_key, count, total_fare, total_distance)
            current_key = key
            count = 0
            total_fare = 0.0
            total_distance = 0.0

        count += cnt
        total_fare += fare
        total_distance += distance

    if current_key is not None:
        emit(current_key, count, total_fare, total_distance)


if __name__ == "__main__":
    main()
