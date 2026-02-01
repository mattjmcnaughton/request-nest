"""API v1 router aggregation."""

from __future__ import annotations

from fastapi import APIRouter

from request_nest.routes.v1.bins import router as bins_router
from request_nest.routes.v1.health import router as health_router

v1_router = APIRouter()

v1_router.include_router(health_router, tags=["health"])
v1_router.include_router(bins_router, prefix="/bins", tags=["bins"])
