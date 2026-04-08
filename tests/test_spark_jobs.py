"""Smoke tests for Spark transformations.

These tests are skipped automatically when pyspark is not installed,
which keeps the basic CI run lightweight.
"""

from __future__ import annotations

import pytest

pyspark = pytest.importorskip("pyspark")


@pytest.fixture(scope="module")
def spark():
    from pyspark.sql import SparkSession

    s = (
        SparkSession.builder.appName("tests")
        .master("local[2]")
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )
    yield s
    s.stop()


def test_trip_aggregate(spark) -> None:
    from datetime import datetime

    from src.spark.batch.trip_analytics import aggregate

    rows = [
        (
            1,
            datetime(2024, 1, 1, 8, 0),
            datetime(2024, 1, 1, 8, 15),
            1,
            2.0,
            1,
            "N",
            132,
            236,
            1,
            10.0,
            0,
            0,
            1.0,
            0,
            0,
            12.0,
            0,
            0,
        ),
        (
            1,
            datetime(2024, 1, 1, 8, 30),
            datetime(2024, 1, 1, 8, 50),
            1,
            4.0,
            1,
            "N",
            132,
            100,
            1,
            20.0,
            0,
            0,
            2.0,
            0,
            0,
            24.0,
            0,
            0,
        ),
    ]
    from src.spark.schemas import YELLOW_TRIP_SCHEMA

    df = spark.createDataFrame(rows, schema=YELLOW_TRIP_SCHEMA)
    out = aggregate(df).collect()
    assert len(out) == 1
    assert out[0]["zone_id"] == 132
    assert out[0]["trip_count"] == 2


def test_revenue_aggregate(spark) -> None:
    from datetime import datetime

    from src.spark.batch.revenue_aggregation import aggregate_daily
    from src.spark.schemas import YELLOW_TRIP_SCHEMA

    rows = [
        (
            1,
            datetime(2024, 1, 1, 8, 0),
            datetime(2024, 1, 1, 8, 15),
            1,
            2.0,
            1,
            "N",
            132,
            236,
            1,
            10.0,
            0,
            0,
            1.0,
            0,
            0,
            12.0,
            0,
            0,
        ),
        (
            1,
            datetime(2024, 1, 1, 9, 0),
            datetime(2024, 1, 1, 9, 20),
            2,
            3.0,
            1,
            "N",
            100,
            200,
            2,
            15.0,
            0,
            0,
            0.0,
            0,
            0,
            16.0,
            0,
            0,
        ),
    ]
    df = spark.createDataFrame(rows, schema=YELLOW_TRIP_SCHEMA)
    result = aggregate_daily(df).collect()
    assert len(result) == 1
    assert result[0]["total_trips"] == 2
