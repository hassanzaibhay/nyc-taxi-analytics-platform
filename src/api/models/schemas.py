"""Pydantic v2 response models."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime


class HourlyTrip(ORMModel):
    zone_id: int
    hour_start: datetime
    trip_count: int
    avg_fare: Decimal | None = None
    avg_distance: Decimal | None = None
    total_revenue: Decimal | None = None


class TripSummary(BaseModel):
    total_trips: int
    total_revenue: Decimal
    avg_fare: Decimal
    avg_tip_pct: Decimal
    avg_distance: Decimal


class ZoneDemandPoint(ORMModel):
    zone_id: int
    hour: int
    avg_trip_count: float


class TopZone(ORMModel):
    zone_id: int
    trip_count: int
    total_revenue: Decimal


class DailyRevenue(ORMModel):
    trip_date: date
    total_trips: int
    total_revenue: Decimal
    avg_fare: Decimal
    cash_pct: Decimal | None = None
    credit_pct: Decimal | None = None


class PaymentBreakdown(BaseModel):
    payment_type: str
    trip_count: int
    revenue: Decimal


class DateRange(BaseModel):
    min_date: date
    max_date: date


class RealtimeDemand(ORMModel):
    zone_id: int
    window_start: datetime
    window_end: datetime
    trip_count: int
    avg_fare: Decimal | None = None
