"""Feature engineering for fare prediction.

Produces a feature dataset (parquet) suitable for downstream ML training.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from src.spark.schemas import YELLOW_TRIP_SCHEMA

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("fare_features")


def build_session(master: str) -> SparkSession:
    return (
        SparkSession.builder.appName("nyc-taxi-fare-features")
        .master(master)
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )


def build_features(df: DataFrame) -> DataFrame:
    base = (
        df.filter(F.col("fare_amount") > 0)
        .filter(F.col("trip_distance") > 0)
        .withColumn("hour_of_day", F.hour("tpep_pickup_datetime"))
        .withColumn("day_of_week", F.dayofweek("tpep_pickup_datetime"))
        .withColumn("month", F.month("tpep_pickup_datetime"))
        .withColumn(
            "distance_bucket",
            F.when(F.col("trip_distance") < 1, "short")
            .when(F.col("trip_distance") < 5, "medium")
            .when(F.col("trip_distance") < 15, "long")
            .otherwise("very_long"),
        )
        .withColumn("zone_pair", F.concat_ws("-", "PULocationID", "DOLocationID"))
    )

    zone_pair_avg = base.groupBy("zone_pair").agg(
        F.avg("fare_amount").alias("zone_pair_avg_fare")
    )

    return base.join(zone_pair_avg, on="zone_pair", how="left").select(
        "tpep_pickup_datetime",
        "PULocationID",
        "DOLocationID",
        "zone_pair",
        "hour_of_day",
        "day_of_week",
        "month",
        "trip_distance",
        "distance_bucket",
        "passenger_count",
        "zone_pair_avg_fare",
        "fare_amount",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", default=os.environ.get("SPARK_MASTER_URL", "local[*]"))
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    spark = build_session(args.master)
    try:
        df = spark.read.schema(YELLOW_TRIP_SCHEMA).parquet(args.input)
        features = build_features(df)
        log.info("Writing features to %s", args.output)
        features.write.mode("overwrite").option("compression", "snappy").parquet(args.output)
        return 0
    except Exception:
        log.exception("Job failed")
        return 1
    finally:
        spark.stop()


if __name__ == "__main__":
    sys.exit(main())
