"""Tests for Hadoop streaming reducers."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REDUCER_ZONE = Path(__file__).parent.parent / "src" / "hadoop" / "reducer_zone_aggregation.py"
REDUCER_FARE = Path(__file__).parent.parent / "src" / "hadoop" / "reducer_fare_analysis.py"


def run(script: Path, stdin_data: str) -> str:
    return subprocess.run(
        [sys.executable, str(script)],
        input=stdin_data,
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def test_zone_reducer_single_key() -> None:
    data = "132\t2024-01-15T08\t10.0\t2.0\t1\n132\t2024-01-15T08\t20.0\t4.0\t1\n"
    out = run(REDUCER_ZONE, data).strip()
    parts = out.split("\t")
    assert parts[0] == "132"
    assert parts[2] == "2"
    assert float(parts[3]) == 15.0
    assert float(parts[4]) == 3.0


def test_zone_reducer_multiple_keys() -> None:
    data = (
        "132\t2024-01-15T08\t10.0\t2.0\t1\n"
        "132\t2024-01-15T08\t20.0\t4.0\t1\n"
        "236\t2024-01-15T09\t30.0\t5.0\t1\n"
    )
    lines = run(REDUCER_ZONE, data).strip().split("\n")
    assert len(lines) == 2


def test_fare_reducer_aggregates() -> None:
    data = "1\t10.0\t1.0\t1\n1\t20.0\t2.0\t1\n2\t5.0\t0.5\t1\n"
    out = run(REDUCER_FARE, data).strip().split("\n")
    assert len(out) == 2
    first = out[0].split("\t")
    assert first[0] == "1"
    assert int(first[1]) == 2
    assert float(first[2]) == 15.0
