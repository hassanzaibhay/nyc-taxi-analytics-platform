"""Spark Structured Streaming: real-time zone demand from Kafka."""

from __future__ import annotations

import argparse
import logging
import os
import sys

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("realtime_demand")

EVENT_SCHEMA = StructType(
    [
        StructField("VendorID", IntegerType(), True),
        StructField("tpep_pickup_datetime", StringType(), True),
        StructField("tpep_dropoff_datetime", StringType(), True),
        StructField("passenger_count", IntegerType(), True),
        StructField("trip_distance", DoubleType(), True),
        StructField("PULocationID", IntegerType(), True),
        StructField("DOLocationID", IntegerType(), True),
        StructField("payment_type", IntegerType(), True),
        StructField("fare_amount", DoubleType(), True),
        StructField("tip_amount", DoubleType(), True),
        StructField("total_amount", DoubleType(), True),
    ]
)


def build_session(master: str) -> SparkSession:
    return (
        SparkSession.builder.appName("nyc-taxi-realtime-demand")
        .master(master)
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )


def write_batch_to_postgres(batch_df: DataFrame, batch_id: int) -> None:
    pg_host = os.environ.get("POSTGRES_HOST", "postgres")
    pg_port = os.environ.get("POSTGRES_PORT", "5432")
    pg_db = os.environ.get("POSTGRES_DB", "nyc_taxi")
    pg_user = os.environ.get("POSTGRES_USER", "taxi_user")
    pg_pass = os.environ.get("POSTGRES_PASSWORD", "taxi_pass")
    url = f"jdbc:postgresql://{pg_host}:{pg_port}/{pg_db}"
    log.info("Writing micro-batch %s with %s rows", batch_id, batch_df.count())
    (
        batch_df.write.mode("append")
        .format("jdbc")
        .option("url", url)
        .option("dbtable", "realtime.zone_demand_live")
        .option("user", pg_user)
        .option("password", pg_pass)
        .option("driver", "org.postgresql.Driver")
        .save()
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", default=os.environ.get("SPARK_MASTER_URL", "local[*]"))
    parser.add_argument(
        "--bootstrap-servers",
        default=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    )
    parser.add_argument(
        "--topic", default=os.environ.get("KAFKA_TOPIC_TRIPS", "nyc-taxi.trips.raw")
    )
    parser.add_argument("--checkpoint", default="/tmp/checkpoint/realtime_demand")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    spark = build_session(args.master)
    spark.sparkContext.setLogLevel("WARN")

    try:
        raw = (
            spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", args.bootstrap_servers)
            .option("subscribe", args.topic)
            .option("startingOffsets", "latest")
            .load()
        )

        events = (
            raw.select(F.from_json(F.col("value").cast("string"), EVENT_SCHEMA).alias("e"))
            .select("e.*")
            .withColumn("event_time", F.to_timestamp("tpep_pickup_datetime"))
            .filter(F.col("fare_amount") > 0)
            .withWatermark("event_time", "10 minutes")
        )

        windowed = (
            events.groupBy(
                F.col("PULocationID").alias("zone_id"),
                F.window("event_time", "15 minutes", "5 minutes"),
            )
            .agg(
                F.count("*").alias("trip_count"),
                F.round(F.avg("fare_amount"), 2).alias("avg_fare"),
            )
            .select(
                "zone_id",
                F.col("window.start").alias("window_start"),
                F.col("window.end").alias("window_end"),
                "trip_count",
                "avg_fare",
            )
        )

        query = (
            windowed.writeStream.foreachBatch(write_batch_to_postgres)
            .option("checkpointLocation", args.checkpoint)
            .outputMode("update")
            .start()
        )

        query.awaitTermination()
        return 0
    except Exception:
        log.exception("Streaming job failed")
        return 1
    finally:
        spark.stop()


if __name__ == "__main__":
    sys.exit(main())
