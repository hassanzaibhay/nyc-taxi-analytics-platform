#!/usr/bin/env python3
"""Mapper: emit (payment_type, fare, tip) for fare analysis."""

from __future__ import annotations

import sys

COL_PAYMENT_TYPE = 9
COL_FARE = 10
COL_TIP = 13

HEADER_TOKENS = ("vendorid", "VendorID")


def main() -> None:
    bad_rows = 0
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line or line.startswith(HEADER_TOKENS):
            continue
        try:
            parts = line.split(",")
            payment_type = parts[COL_PAYMENT_TYPE].strip()
            fare = float(parts[COL_FARE])
            tip = float(parts[COL_TIP])
            if fare <= 0:
                continue
            sys.stdout.write(f"{payment_type}\t{fare}\t{tip}\t1\n")
        except (IndexError, ValueError):
            bad_rows += 1

    if bad_rows:
        sys.stderr.write(f"Bad rows skipped: {bad_rows}\n")


if __name__ == "__main__":
    main()
