"""Trip-level analytics endpoints."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.db import get_db
from api.models.schemas import DateRange, HourlyTrip, TripSummary

router = APIRouter()


@router.get("/date-range", response_model=DateRange)
async def date_range(db: AsyncSession = Depends(get_db)) -> DateRange:
    sql = """
        SELECT MIN(hour_start)::date AS min_date,
               MAX(hour_start)::date AS max_date
        FROM analytics.hourly_zone_demand
    """
    row = (await db.execute(text(sql))).mappings().one()
    return DateRange(min_date=row["min_date"], max_date=row["max_date"])


@router.get("/hourly", response_model=list[HourlyTrip])
async def hourly_trips(
    date_from: date = Query(...),
    date_to: date = Query(...),
    zone_id: int | None = Query(None),
    hour_from: int = Query(0, ge=0, le=23),
    hour_to: int = Query(23, ge=0, le=23),
    db: AsyncSession = Depends(get_db),
) -> list[HourlyTrip]:
    base_sql = """
        SELECT zone_id, hour_start, trip_count, avg_fare, avg_distance, total_revenue
        FROM analytics.hourly_zone_demand
        WHERE hour_start::date >= :date_from
          AND hour_start::date <= :date_to
          AND EXTRACT(HOUR FROM hour_start) >= :hour_from
          AND EXTRACT(HOUR FROM hour_start) <= :hour_to
    """
    params: dict[str, Any] = {
        "date_from": date_from,
        "date_to": date_to,
        "hour_from": hour_from,
        "hour_to": hour_to,
    }
    if zone_id is not None:
        base_sql += " AND zone_id = :zone_id"
        params["zone_id"] = zone_id
    base_sql += " ORDER BY hour_start LIMIT 5000"
    rows = (await db.execute(text(base_sql), params)).mappings().all()
    return [HourlyTrip(**row) for row in rows]


@router.get("/summary", response_model=TripSummary)
async def trip_summary(
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db),
) -> TripSummary:
    sql = """
        SELECT
            COALESCE(SUM(trip_count), 0)              AS total_trips,
            COALESCE(SUM(total_revenue), 0)           AS total_revenue,
            COALESCE(AVG(avg_fare), 0)                AS avg_fare,
            COALESCE(AVG(avg_tip_percentage), 0)      AS avg_tip_pct,
            COALESCE(AVG(avg_distance), 0)            AS avg_distance
        FROM analytics.hourly_zone_demand
        WHERE hour_start::date >= :date_from
          AND hour_start::date <= :date_to
    """
    row = (
        (await db.execute(text(sql), {"date_from": date_from, "date_to": date_to}))
        .mappings()
        .one()
    )
    return TripSummary(
        total_trips=int(row["total_trips"]),
        total_revenue=Decimal(row["total_revenue"]),
        avg_fare=Decimal(row["avg_fare"]),
        avg_tip_pct=Decimal(row["avg_tip_pct"]),
        avg_distance=Decimal(row["avg_distance"]),
    )
