"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from api.config import get_settings
from api.db import close_engine
from api.routes import health, realtime, revenue, trips, zones

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await close_engine()


app = FastAPI(
    title="NYC Taxi Analytics API",
    version="1.0.0",
    description="REST API exposing analytics over the NYC TLC trip dataset.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(trips.router, prefix="/api/trips", tags=["trips"])
app.include_router(zones.router, prefix="/api/zones", tags=["zones"])
app.include_router(revenue.router, prefix="/api/revenue", tags=["revenue"])
app.include_router(realtime.router, prefix="/api/realtime", tags=["realtime"])


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")
