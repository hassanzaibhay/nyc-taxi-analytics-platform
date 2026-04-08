"""Simulated real-time taxi event producer.

Replays NYC TLC parquet files into a Kafka topic with configurable delay.
"""
from __future__ import annotations

import argparse
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq
from confluent_kafka import KafkaError, Producer

from src.kafka.schemas import TripEvent, serialize

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("kafka_producer")

_shutdown = False


def _handle_signal(signum: int, _frame: Any) -> None:  # noqa: ANN401
    global _shutdown
    log.info("Received signal %s, shutting down...", signum)
    _shutdown = True


def delivery_report(err: KafkaError | None, msg: Any) -> None:  # noqa: ANN401
    if err is not None:
        log.error("Delivery failed for key %s: %s", msg.key(), err)


def build_producer(bootstrap: str) -> Producer:
    config = {
        "bootstrap.servers": bootstrap,
        "client.id": "nyc-taxi-producer",
        "enable.idempotence": True,
        "acks": "all",
        "linger.ms": 5,
        "batch.size": int(os.environ.get("KAFKA_PRODUCER_BATCH_SIZE", "16384")),
    }
    return Producer(config)


def row_to_event(row: dict[str, Any]) -> TripEvent:
    return TripEvent(
        VendorID=row.get("VendorID"),
        tpep_pickup_datetime=str(row.get("tpep_pickup_datetime")),
        tpep_dropoff_datetime=str(row.get("tpep_dropoff_datetime")),
        passenger_count=row.get("passenger_count"),
        trip_distance=float(row.get("trip_distance") or 0.0),
        PULocationID=int(row.get("PULocationID") or 0),
        DOLocationID=int(row.get("DOLocationID") or 0),
        payment_type=row.get("payment_type"),
        fare_amount=float(row.get("fare_amount") or 0.0),
        tip_amount=float(row.get("tip_amount") or 0.0),
        total_amount=float(row.get("total_amount") or 0.0),
    )


def stream_parquet_files(data_dir: Path) -> Any:
    for path in sorted(data_dir.glob("*.parquet")):
        log.info("Reading %s", path)
        table = pq.read_table(path)
        for batch in table.to_batches(max_chunksize=1000):
            for row in batch.to_pylist():
                yield row


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="NYC Taxi Kafka producer")
    parser.add_argument("--data-dir", default="data/raw", type=Path)
    parser.add_argument("--topic", default=os.environ.get("KAFKA_TOPIC_TRIPS", "nyc-taxi.trips.raw"))
    parser.add_argument(
        "--bootstrap",
        default=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9094"),
    )
    parser.add_argument("--delay-ms", type=int, default=int(os.environ.get("KAFKA_PRODUCER_DELAY_MS", "10")))
    parser.add_argument("--max-events", type=int, default=0, help="0 = unlimited")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    if not args.data_dir.exists():
        log.error("Data dir does not exist: %s", args.data_dir)
        return 2

    producer = build_producer(args.bootstrap)
    sent = 0
    delay = args.delay_ms / 1000.0

    try:
        for row in stream_parquet_files(args.data_dir):
            if _shutdown:
                break
            event = row_to_event(row)
            producer.produce(
                topic=args.topic,
                key=str(event.PULocationID).encode("utf-8"),
                value=serialize(event),
                callback=delivery_report,
            )
            producer.poll(0)
            sent += 1
            if sent % 1000 == 0:
                log.info("Sent %s events", sent)
            if args.max_events and sent >= args.max_events:
                break
            if delay > 0:
                time.sleep(delay)
    finally:
        log.info("Flushing producer (sent=%s)...", sent)
        producer.flush(10)

    return 0


if __name__ == "__main__":
    sys.exit(main())
