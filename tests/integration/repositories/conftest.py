"""Pytest fixtures for repository integration tests."""

from collections.abc import AsyncGenerator

import pytest
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.pool import ConnectionPoolEntry

from request_nest.config import settings
from request_nest.db import create_engine, create_session_factory
from tests.conftest import (
    create_schema_from_public,
    drop_schema,
    generate_schema_name,
    get_test_database_url,
)


@pytest.fixture
async def db_session(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncGenerator[AsyncSession]:
    """Provide an isolated database session for repository tests.

    Each test gets its own schema cloned from 'public', providing full
    isolation for parallel test execution. The schema is dropped after
    the test completes.
    """
    # Generate unique schema for this test
    schema_name = generate_schema_name(request)
    create_schema_from_public(schema_name)

    try:
        # Override database URL to use test database
        test_db_url = get_test_database_url()
        monkeypatch.setattr(settings, "database_url", test_db_url)

        # Create engine with test database
        engine = create_engine(test_db_url)

        # Set search_path on every new connection from the pool
        @event.listens_for(engine.sync_engine, "connect")
        def set_search_path(dbapi_conn: ConnectionPoolEntry, _connection_record: object) -> None:
            cursor = dbapi_conn.cursor()
            cursor.execute(f'SET search_path TO "{schema_name}", public')
            cursor.close()

        # Create session factory and session
        session_factory = create_session_factory(engine)

        async with session_factory() as session:
            # Explicitly set search_path to ensure it's applied
            await session.execute(text(f'SET search_path TO "{schema_name}", public'))
            yield session

        await engine.dispose()
    finally:
        drop_schema(schema_name)
