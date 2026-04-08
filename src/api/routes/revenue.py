"""Revenue endpoints."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.db import get_db
from api.models.schemas import DailyRevenue, PaymentBreakdown

router = APIRouter()

PAYMENT_TYPE_LABELS = {
    1: "credit_card",
    2: "cash",
    3: "no_charge",
    4: "dispute",
    5: "unknown",
    6: "voided",
}


@router.get("/daily", response_model=list[DailyRevenue])
async def daily_revenue(
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db),
) -> list[DailyRevenue]:
    sql = """
        SELECT trip_date, total_trips, total_revenue, avg_fare,
               cash_payment_pct AS cash_pct, credit_payment_pct AS credit_pct
        FROM analytics.daily_summary
        WHERE trip_date >= :date_from
          AND trip_date <= :date_to
        ORDER BY trip_date
    """
    rows = (
        (await db.execute(text(sql), {"date_from": date_from, "date_to": date_to}))
        .mappings()
        .all()
    )
    return [DailyRevenue(**row) for row in rows]


@router.get("/payment-breakdown", response_model=list[PaymentBreakdown])
async def payment_breakdown(
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db),
) -> list[PaymentBreakdown]:
    # Derived from daily_summary aggregates (cash/credit pct + total).
    sql = """
        SELECT
            ROUND(SUM(total_trips * cash_payment_pct / 100.0))::int   AS cash_trips,
            ROUND(SUM(total_trips * credit_payment_pct / 100.0))::int AS credit_trips,
            SUM(total_revenue * cash_payment_pct / 100.0)              AS cash_rev,
            SUM(total_revenue * credit_payment_pct / 100.0)            AS credit_rev
        FROM analytics.daily_summary
        WHERE trip_date >= :date_from
          AND trip_date <= :date_to
    """
    row = (
        (await db.execute(text(sql), {"date_from": date_from, "date_to": date_to}))
        .mappings()
        .one()
    )
    return [
        PaymentBreakdown(
            payment_type="cash", trip_count=row["cash_trips"] or 0, revenue=row["cash_rev"] or 0
        ),
        PaymentBreakdown(
            payment_type="credit_card",
            trip_count=row["credit_trips"] or 0,
            revenue=row["credit_rev"] or 0,
        ),
    ]
