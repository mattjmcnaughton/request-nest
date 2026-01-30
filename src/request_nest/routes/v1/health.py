"""Health check routes."""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from request_nest import __version__
from request_nest.db import get_db_session

router = APIRouter()
logger = structlog.get_logger()

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


@router.get("/health")
async def health() -> HealthResponse:
    """Liveness check - is the service running."""
    return HealthResponse(status="healthy", version=__version__)


@router.get("/ready")
async def ready(
    response: Response,
    session: DbSession,
) -> HealthResponse:
    """Readiness check - is the service ready to accept traffic."""
    try:
        await session.execute(text("SELECT 1"))
        return HealthResponse(status="ready", version=__version__)
    except Exception as e:
        logger.error("database_connectivity_check_failed", error=str(e))
        response.status_code = 503
        return HealthResponse(status="not_ready", version=__version__)
