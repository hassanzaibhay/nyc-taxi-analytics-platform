"""Real-time demand endpoints (snapshot + SSE stream)."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from api.db import SessionLocal, get_db
from api.models.schemas import RealtimeDemand

router = APIRouter()

STREAM_INTERVAL_SECONDS = 5


@router.get("/demand", response_model=list[RealtimeDemand])
async def realtime_demand(db: AsyncSession = Depends(get_db)) -> list[RealtimeDemand]:
    sql = """
        SELECT zone_id, window_start, window_end, trip_count, avg_fare
        FROM realtime.zone_demand_live
        WHERE window_start >= (
            SELECT MAX(window_start) - INTERVAL '1 hour'
            FROM realtime.zone_demand_live
        )
        ORDER BY window_start DESC, zone_id
        LIMIT 500
    """
    rows = (await db.execute(text(sql))).mappings().all()
    return [RealtimeDemand(**row) for row in rows]


async def _event_generator(request: Request) -> AsyncGenerator[dict[str, Any], None]:
    sql = """
        SELECT zone_id, window_start, window_end, trip_count, avg_fare
        FROM realtime.zone_demand_live
        WHERE window_start >= (
            SELECT MAX(window_start) - INTERVAL '15 minutes'
            FROM realtime.zone_demand_live
        )
        ORDER BY window_start DESC, zone_id
        LIMIT 100
    """
    while True:
        if await request.is_disconnected():
            break
        async with SessionLocal() as session:
            rows = (await session.execute(text(sql))).mappings().all()
        payload = [
            {
                "zone_id": r["zone_id"],
                "window_start": r["window_start"].isoformat()
                if isinstance(r["window_start"], datetime)
                else r["window_start"],
                "window_end": r["window_end"].isoformat()
                if isinstance(r["window_end"], datetime)
                else r["window_end"],
                "trip_count": r["trip_count"],
                "avg_fare": float(r["avg_fare"]) if r["avg_fare"] is not None else None,
            }
            for r in rows
        ]
        yield {"event": "demand", "data": json.dumps(payload)}
        await asyncio.sleep(STREAM_INTERVAL_SECONDS)


@router.get("/stream")
async def stream(request: Request) -> EventSourceResponse:
    return EventSourceResponse(_event_generator(request))
