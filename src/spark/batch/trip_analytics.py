"""Hourly zone-level demand analytics.

Reads NYC TLC parquet data, computes per-zone hourly aggregates, and writes
results to PostgreSQL ``analytics.hourly_zone_demand``.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from src.spark.schemas import YELLOW_TRIP_SCHEMA

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("trip_analytics")


def build_session(master: str) -> SparkSession:
    return (
        SparkSession.builder.appName("nyc-taxi-trip-analytics")
        .master(master)
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", "32")
        .getOrCreate()
    )


def clean(df: DataFrame) -> DataFrame:
    """Drop outliers and clearly invalid rows before aggregation."""
    return df.filter(
        (F.col("tpep_pickup_datetime") >= F.lit("2024-01-01"))
        & (F.col("tpep_pickup_datetime") < F.lit("2025-01-01"))
        & (F.col("fare_amount") > 0)
        & (F.col("fare_amount") < 500)
        & (F.col("trip_distance") > 0)
        & (F.col("trip_distance") < 200)
        & F.col("PULocationID").isNotNull()
        & F.col("DOLocationID").isNotNull()
    )


def aggregate(df: DataFrame) -> DataFrame:
    """Compute hourly per-zone demand metrics."""
    duration_min = (
        F.unix_timestamp("tpep_dropoff_datetime") - F.unix_timestamp("tpep_pickup_datetime")
    ) / 60.0
    tip_pct = F.when(F.col("fare_amount") > 0, F.col("tip_amount") / F.col("fare_amount") * 100)

    return (
        clean(df)
        .withColumn("hour_start", F.date_trunc("hour", "tpep_pickup_datetime"))
        .withColumn("duration_minutes", duration_min)
        .withColumn("tip_pct", tip_pct)
        .groupBy("PULocationID", "hour_start")
        .agg(
            F.count("*").alias("trip_count"),
            F.round(F.avg("fare_amount"), 2).alias("avg_fare"),
            F.round(F.avg("trip_distance"), 2).alias("avg_distance"),
            F.round(F.avg("duration_minutes"), 2).alias("avg_duration_minutes"),
            F.round(F.sum("total_amount"), 2).alias("total_revenue"),
            F.round(F.avg("tip_pct"), 2).alias("avg_tip_percentage"),
        )
        .withColumnRenamed("PULocationID", "zone_id")
    )


def write_postgres(df: DataFrame, table: str) -> None:
    pg_host = os.environ.get("POSTGRES_HOST", "postgres")
    pg_port = os.environ.get("POSTGRES_PORT", "5432")
    pg_db = os.environ.get("POSTGRES_DB", "nyc_taxi")
    pg_user = os.environ.get("POSTGRES_USER", "taxi_user")
    pg_pass = os.environ.get("POSTGRES_PASSWORD", "taxi_pass")
    url = f"jdbc:postgresql://{pg_host}:{pg_port}/{pg_db}"

    log.info("Writing %s rows to %s.%s", df.count(), pg_db, table)
    (
        df.write.mode("overwrite")
        .format("jdbc")
        .option("url", url)
        .option("dbtable", table)
        .option("user", pg_user)
        .option("password", pg_pass)
        .option("driver", "org.postgresql.Driver")
        .save()
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hourly zone demand analytics")
    parser.add_argument("--master", default=os.environ.get("SPARK_MASTER_URL", "local[*]"))
    parser.add_argument("--input", required=True, help="Input parquet path (HDFS or local)")
    parser.add_argument("--table", default="analytics.hourly_zone_demand")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    start = time.time()
    spark = build_session(args.master)
    try:
        log.info("Reading parquet from %s", args.input)
        df = spark.read.schema(YELLOW_TRIP_SCHEMA).parquet(args.input)
        result = aggregate(df).cache()
        row_count = result.count()
        write_postgres(result, args.table)
        elapsed = time.time() - start
        log.info("Job completed in %.1fs — %s rows written", elapsed, row_count)
        return 0
    except Exception:
        log.exception("Job failed")
        return 1
    finally:
        spark.stop()


if __name__ == "__main__":
    sys.exit(main())
