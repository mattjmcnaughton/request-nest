"""FastAPI application entry point."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

from request_nest import __version__
from request_nest.config import settings
from request_nest.db import create_engine, create_session_factory
from request_nest.observability import setup_logging, setup_metrics, setup_tracing
from request_nest.routes.v1 import v1_router
from request_nest.routes.v1.ingest import router as ingest_router
from request_nest.routes.web import web_router

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan handler."""
    is_dev = settings.environment == "development"
    tracer_provider = setup_tracing(enable_console=is_dev)
    meter_provider = setup_metrics()
    setup_logging(settings.log_level)
    logger.info("application_started", app_name="request-nest", version=__version__)

    # Initialize database engine and session factory
    engine = create_engine(settings.database_url, schema=settings.db_schema)
    app.state.db_engine = engine
    app.state.async_session = create_session_factory(engine)

    # Instrument database libraries (after engine creation, after TracerProvider is set)
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
    AsyncPGInstrumentor().instrument()

    yield

    # Cleanup
    AsyncPGInstrumentor().uninstrument()
    SQLAlchemyInstrumentor().uninstrument()
    await engine.dispose()
    logger.info("database_engine_disposed")
    if meter_provider is not None:
        meter_provider.shutdown()
    if tracer_provider is not None:
        tracer_provider.shutdown()
    logger.info("application_stopped")


app = FastAPI(
    title="request-nest",
    description="A self-hosted webhook inbox for capturing and inspecting HTTP requests",
    version=__version__,
    lifespan=lifespan,
)

# Instrument FastAPI at module level so the OpenTelemetry middleware is part of
# the ASGI stack from the start. The middleware's internal tracer is a proxy that
# delegates to whatever TracerProvider is globally configured at span-creation
# time, so it works even though setup_tracing() runs later in the lifespan.
FastAPIInstrumentor.instrument_app(app)

# API v1 routes
app.include_router(v1_router, prefix="/api/v1")

# Ingest routes (public, no auth)
app.include_router(ingest_router, prefix="/b", tags=["ingest"])

# Web UI routes
app.include_router(web_router)
