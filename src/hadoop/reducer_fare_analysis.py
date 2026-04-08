#!/usr/bin/env python3
"""Reducer: aggregate fare and tip statistics per payment type."""

from __future__ import annotations

import sys


def emit(key: str, count: int, total_fare: float, total_tip: float) -> None:
    if count == 0:
        return
    avg_fare = total_fare / count
    avg_tip = total_tip / count
    sys.stdout.write(f"{key}\t{count}\t{avg_fare:.4f}\t{avg_tip:.4f}\n")


def main() -> None:
    current_key: str | None = None
    count = 0
    total_fare = 0.0
    total_tip = 0.0

    for raw_line in sys.stdin:
        line = raw_line.rstrip("\n")
        if not line:
            continue
        try:
            payment_type, fare_s, tip_s, count_s = line.split("\t")
            fare = float(fare_s)
            tip = float(tip_s)
            cnt = int(count_s)
        except ValueError:
            continue

        if current_key is None:
            current_key = payment_type

        if payment_type != current_key:
            emit(current_key, count, total_fare, total_tip)
            current_key = payment_type
            count = 0
            total_fare = 0.0
            total_tip = 0.0

        count += cnt
        total_fare += fare
        total_tip += tip

    if current_key is not None:
        emit(current_key, count, total_fare, total_tip)


if __name__ == "__main__":
    main()
