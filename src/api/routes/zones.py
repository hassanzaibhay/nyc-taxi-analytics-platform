"""Zone-level analytics endpoints."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.db import get_db
from api.models.schemas import TopZone, ZoneDemandPoint

router = APIRouter()


@router.get("/demand", response_model=list[ZoneDemandPoint])
async def zone_demand(
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db),
) -> list[ZoneDemandPoint]:
    sql = """
        SELECT
            zone_id,
            EXTRACT(HOUR FROM hour_start)::int AS hour,
            AVG(trip_count)::float             AS avg_trip_count
        FROM analytics.hourly_zone_demand
        WHERE hour_start::date >= :date_from
          AND hour_start::date <= :date_to
        GROUP BY zone_id, hour
        ORDER BY zone_id, hour
    """
    rows = (
        (await db.execute(text(sql), {"date_from": date_from, "date_to": date_to}))
        .mappings()
        .all()
    )
    return [ZoneDemandPoint(**row) for row in rows]


@router.get("/top", response_model=list[TopZone])
async def top_zones(
    n: int = Query(10, ge=1, le=100),
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db),
) -> list[TopZone]:
    sql = """
        SELECT zone_id,
               SUM(trip_count)::int      AS trip_count,
               SUM(total_revenue)        AS total_revenue
        FROM analytics.hourly_zone_demand
        WHERE hour_start::date >= :date_from
          AND hour_start::date <= :date_to
        GROUP BY zone_id
        ORDER BY trip_count DESC
        LIMIT :n
    """
    rows = (
        (await db.execute(text(sql), {"n": n, "date_from": date_from, "date_to": date_to}))
        .mappings()
        .all()
    )
    return [TopZone(**row) for row in rows]
