"""Kafka event schemas (JSON for dev; Avro recommended for production)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class TripEvent:
    """A single taxi trip event published to Kafka."""

    VendorID: int | None
    tpep_pickup_datetime: str
    tpep_dropoff_datetime: str
    passenger_count: int | None
    trip_distance: float
    PULocationID: int
    DOLocationID: int
    payment_type: int | None
    fare_amount: float
    tip_amount: float
    total_amount: float


def serialize(event: TripEvent) -> bytes:
    return json.dumps(asdict(event), default=str).encode("utf-8")


def deserialize(payload: bytes) -> dict[str, Any]:
    return json.loads(payload.decode("utf-8"))


def validate(payload: dict[str, Any]) -> bool:
    required = {"tpep_pickup_datetime", "PULocationID", "fare_amount"}
    return required.issubset(payload.keys())
