"""Health and readiness endpoints."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.db import get_db
from api.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar_one()
        db_status = "connected"
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=f"Database unreachable: {exc}") from exc

    return HealthResponse(
        status="healthy",
        database=db_status,
        timestamp=datetime.now(UTC),
    )
