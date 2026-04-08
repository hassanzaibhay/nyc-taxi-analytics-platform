"""Daily revenue rollup → analytics.daily_summary."""
from __future__ import annotations

import argparse
import logging
import os
import sys

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from src.spark.schemas import YELLOW_TRIP_SCHEMA

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("revenue_aggregation")


def build_session(master: str) -> SparkSession:
    return (
        SparkSession.builder.appName("nyc-taxi-revenue-rollup")
        .master(master)
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )


def aggregate_daily(df: DataFrame) -> DataFrame:
    is_cash = F.when(F.col("payment_type") == 2, 1.0).otherwise(0.0)
    is_credit = F.when(F.col("payment_type") == 1, 1.0).otherwise(0.0)
    return (
        df.filter(F.col("fare_amount") > 0)
        .withColumn("trip_date", F.to_date("tpep_pickup_datetime"))
        .withColumn("is_cash", is_cash)
        .withColumn("is_credit", is_credit)
        .groupBy("trip_date")
        .agg(
            F.count("*").alias("total_trips"),
            F.round(F.sum("total_amount"), 2).alias("total_revenue"),
            F.round(F.avg("fare_amount"), 2).alias("avg_fare"),
            F.round(F.avg("trip_distance"), 2).alias("avg_trip_distance"),
            F.round(F.avg("is_cash") * 100, 2).alias("cash_payment_pct"),
            F.round(F.avg("is_credit") * 100, 2).alias("credit_payment_pct"),
            F.round(F.avg("passenger_count"), 2).alias("avg_passenger_count"),
        )
    )


def write_postgres(df: DataFrame, table: str) -> None:
    pg_host = os.environ.get("POSTGRES_HOST", "postgres")
    pg_port = os.environ.get("POSTGRES_PORT", "5432")
    pg_db = os.environ.get("POSTGRES_DB", "nyc_taxi")
    pg_user = os.environ.get("POSTGRES_USER", "taxi_user")
    pg_pass = os.environ.get("POSTGRES_PASSWORD", "taxi_pass")
    url = f"jdbc:postgresql://{pg_host}:{pg_port}/{pg_db}"
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", default=os.environ.get("SPARK_MASTER_URL", "local[*]"))
    parser.add_argument("--input", required=True)
    parser.add_argument("--table", default="analytics.daily_summary")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    spark = build_session(args.master)
    try:
        df = spark.read.schema(YELLOW_TRIP_SCHEMA).parquet(args.input)
        write_postgres(aggregate_daily(df), args.table)
        return 0
    except Exception:
        log.exception("Job failed")
        return 1
    finally:
        spark.stop()


if __name__ == "__main__":
    sys.exit(main())
