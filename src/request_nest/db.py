"""Database engine and session management."""

from collections.abc import AsyncGenerator

import structlog
from fastapi import Request
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

__all__ = [
    "create_engine",
    "create_session_factory",
    "get_db_session",
]

logger = structlog.get_logger()


def create_engine(database_url: str) -> AsyncEngine:
    """Create an async SQLAlchemy engine with connection pooling.

    Args:
        database_url: PostgreSQL connection URL. If using 'postgresql://' scheme,
            it will be converted to 'postgresql+asyncpg://' for async support.

    Returns:
        Configured AsyncEngine with pool_size=5, max_overflow=15 (max 20 connections).
    """
    # Convert postgresql:// to postgresql+asyncpg:// if needed
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(
        database_url,
        pool_size=5,
        max_overflow=15,  # pool_size + max_overflow = 20 max connections
    )

    logger.info("database_engine_created", pool_size=5, max_overflow=15)

    return engine


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker:
    """Create an async session factory.

    Args:
        engine: The async engine to bind sessions to.

    Returns:
        Configured async_sessionmaker for creating AsyncSession instances.
    """
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency that yields a database session.

    Args:
        request: The incoming FastAPI request (used to access app.state).

    Yields:
        AsyncSession for database operations.
    """
    async with request.app.state.async_session() as session:
        yield session
