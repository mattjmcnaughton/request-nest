"""FastAPI application entry point."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from request_nest import __version__
from request_nest.config import settings
from request_nest.db import create_engine, create_session_factory
from request_nest.observability import setup_logging
from request_nest.routes.v1 import v1_router
from request_nest.routes.v1.ingest import router as ingest_router
from request_nest.routes.web import web_router

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan handler."""
    setup_logging(settings.log_level)
    logger.info("application_started", app_name="request-nest", version=__version__)

    # Initialize database engine and session factory
    engine = create_engine(settings.database_url)
    app.state.db_engine = engine
    app.state.async_session = create_session_factory(engine)

    yield

    # Cleanup database engine
    await engine.dispose()
    logger.info("database_engine_disposed")
    logger.info("application_stopped")


app = FastAPI(
    title="request-nest",
    description="A self-hosted webhook inbox for capturing and inspecting HTTP requests",
    version=__version__,
    lifespan=lifespan,
)

# API v1 routes
app.include_router(v1_router, prefix="/api/v1")

# Ingest routes (public, no auth)
app.include_router(ingest_router, prefix="/b", tags=["ingest"])

# Web UI routes
app.include_router(web_router)
