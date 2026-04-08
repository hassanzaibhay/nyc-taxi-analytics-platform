"""Tests for Hadoop streaming mappers (pure stdin/stdout scripts)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

MAPPER_ZONE = Path(__file__).parent.parent / "src" / "hadoop" / "mapper_zone_aggregation.py"
MAPPER_FARE = Path(__file__).parent.parent / "src" / "hadoop" / "mapper_fare_analysis.py"

SAMPLE_ROW = "2,2024-01-15 08:15:00,2024-01-15 08:32:00,1,3.5,1,N,132,236,1,18.5,3.0,0.5,4.5,0.0,1.0,27.5,2.5,0"


def run(script: Path, stdin_data: str) -> str:
    proc = subprocess.run(
        [sys.executable, str(script)],
        input=stdin_data,
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout


def test_zone_mapper_emits_one_record() -> None:
    out = run(MAPPER_ZONE, SAMPLE_ROW + "\n")
    parts = out.strip().split("\t")
    assert parts[0] == "132"
    assert parts[1].startswith("2024-01-15T08")
    assert float(parts[2]) == 18.5
    assert float(parts[3]) == 3.5
    assert parts[4] == "1"


def test_zone_mapper_skips_header() -> None:
    out = run(MAPPER_ZONE, "VendorID,col1,col2\n" + SAMPLE_ROW + "\n")
    assert out.count("\n") == 1


def test_zone_mapper_handles_empty() -> None:
    assert run(MAPPER_ZONE, "") == ""


def test_zone_mapper_skips_malformed() -> None:
    assert run(MAPPER_ZONE, "garbage,row\n") == ""


def test_fare_mapper_emits_payment_type() -> None:
    out = run(MAPPER_FARE, SAMPLE_ROW + "\n")
    parts = out.strip().split("\t")
    assert parts[0] == "1"
    assert float(parts[1]) == 18.5
