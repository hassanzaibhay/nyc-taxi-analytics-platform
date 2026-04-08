"""Smoke tests for the FastAPI application.

These tests use TestClient and a stubbed DB session to avoid requiring a
running PostgreSQL during unit testing.
"""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient  # noqa: E402

from api.db import get_db  # noqa: E402
from api.main import app  # noqa: E402


class _StubResult:
    def __init__(self, value=None):
        self._value = value

    def scalar_one(self):
        return self._value

    def mappings(self):
        return self

    def all(self):
        return []

    def one(self):
        return {
            "total_trips": 0,
            "total_revenue": 0,
            "avg_fare": 0,
            "avg_tip_pct": 0,
            "avg_distance": 0,
        }


class _StubSession:
    async def execute(self, *_args, **_kwargs):
        return _StubResult(value=1)


async def _override_get_db():
    yield _StubSession()


app.dependency_overrides[get_db] = _override_get_db
client = TestClient(app)


def test_health_ok() -> None:
    res = client.get("/api/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "healthy"
    assert body["database"] == "connected"


def test_trip_summary_returns_schema() -> None:
    res = client.get(
        "/api/trips/summary",
        params={"date_from": "2024-01-01", "date_to": "2024-01-31"},
    )
    assert res.status_code == 200
    body = res.json()
    assert set(body.keys()) >= {"total_trips", "total_revenue", "avg_fare"}


def test_invalid_query_param() -> None:
    res = client.get(
        "/api/zones/top",
        params={"n": 0, "date_from": "2024-01-01", "date_to": "2024-01-31"},
    )
    assert res.status_code == 422


def test_missing_required_dates() -> None:
    res = client.get("/api/trips/summary")
    assert res.status_code == 422
