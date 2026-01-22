"""Health check routes."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from request_nest import __version__

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


@router.get("/health")
async def health() -> HealthResponse:
    """Liveness check - is the service running."""
    return HealthResponse(status="healthy", version=__version__)


@router.get("/ready")
async def ready() -> HealthResponse:
    """Readiness check - is the service ready to accept traffic."""
    # TODO: Add database connectivity check
    return HealthResponse(status="ready", version=__version__)
