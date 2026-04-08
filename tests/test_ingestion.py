"""Tests for ingestion validation utilities."""
from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from src.ingestion.validate_data import REQUIRED_COLUMNS, validate_file


def _write_parquet(path: Path, table: pa.Table) -> None:
    pq.write_table(table, path)


def test_validate_passes_good_data(tmp_path: Path) -> None:
    cols = {c: [1.0] * 5 for c in REQUIRED_COLUMNS}
    table = pa.table(cols)
    p = tmp_path / "good.parquet"
    _write_parquet(p, table)
    assert validate_file(p) is True


def test_validate_fails_missing_columns(tmp_path: Path) -> None:
    table = pa.table({"VendorID": [1, 2, 3]})
    p = tmp_path / "bad.parquet"
    _write_parquet(p, table)
    assert validate_file(p) is False


def test_validate_fails_empty(tmp_path: Path) -> None:
    cols = {c: pa.array([], type=pa.float64()) for c in REQUIRED_COLUMNS}
    table = pa.table(cols)
    p = tmp_path / "empty.parquet"
    _write_parquet(p, table)
    assert validate_file(p) is False


@pytest.mark.parametrize("missing", ["fare_amount", "PULocationID"])
def test_required_columns(missing: str) -> None:
    assert missing in REQUIRED_COLUMNS
