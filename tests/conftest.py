"""Pytest configuration and fixtures."""

import uuid
from collections.abc import AsyncGenerator
from urllib.parse import urlparse, urlunparse

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient

from request_nest.config import settings

# Cache the original database URL before any monkeypatching
_original_database_url = settings.database_url

# Generate unique database suffix for this test session
# Allows multiple test sessions to run concurrently
_session_id = uuid.uuid4().hex[:8]
TEST_DB_SUFFIX = f"_test_{_session_id}"


def get_test_database_url() -> str:
    """Derive test database URL from the main database URL."""
    parsed = urlparse(_original_database_url)
    test_db_name = parsed.path.lstrip("/") + TEST_DB_SUFFIX
    test_parsed = parsed._replace(path=f"/{test_db_name}")
    return urlunparse(test_parsed)


def get_admin_connection_url() -> str:
    """Get connection URL to the default 'postgres' database for admin operations."""
    parsed = urlparse(_original_database_url)
    admin_parsed = parsed._replace(
        scheme="postgresql",
        path="/postgres",
    )
    return urlunparse(admin_parsed)


def get_test_migration_url() -> str:
    """Get psycopg-compatible URL for running migrations on test database."""
    parsed = urlparse(_original_database_url)
    test_db_name = parsed.path.lstrip("/") + TEST_DB_SUFFIX
    migration_parsed = parsed._replace(
        scheme="postgresql+psycopg",
        path=f"/{test_db_name}",
    )
    return urlunparse(migration_parsed)


def get_test_db_name() -> str:
    """Get the test database name."""
    parsed = urlparse(_original_database_url)
    return parsed.path.lstrip("/") + TEST_DB_SUFFIX


def get_sync_test_db_url() -> str:
    """Get psycopg-compatible URL for sync operations on test database."""
    parsed = urlparse(_original_database_url)
    test_db_name = parsed.path.lstrip("/") + TEST_DB_SUFFIX
    sync_parsed = parsed._replace(
        scheme="postgresql",
        path=f"/{test_db_name}",
    )
    return urlunparse(sync_parsed)


def create_test_database() -> None:
    """Create the test database if it doesn't exist."""
    admin_url = get_admin_connection_url()
    test_db_name = get_test_db_name()

    with (
        psycopg.connect(admin_url, autocommit=True) as conn,
        conn.cursor() as cur,
    ):
        cur.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (test_db_name,),
        )
        if not cur.fetchone():
            cur.execute(f'CREATE DATABASE "{test_db_name}"')


def drop_test_database() -> None:
    """Drop the test database."""
    admin_url = get_admin_connection_url()
    test_db_name = get_test_db_name()

    with (
        psycopg.connect(admin_url, autocommit=True) as conn,
        conn.cursor() as cur,
    ):
        cur.execute(
            """
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = %s AND pid <> pg_backend_pid()
            """,
            (test_db_name,),
        )
        cur.execute(f'DROP DATABASE IF EXISTS "{test_db_name}"')


def run_migrations() -> None:
    """Run alembic migrations on the test database."""
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", get_test_migration_url())
    command.upgrade(alembic_cfg, "head")


def create_schema_from_public(schema_name: str) -> None:
    """Create a new schema by cloning table structure from public schema.

    Uses CREATE TABLE ... (LIKE ... INCLUDING ALL) to copy:
    - Column definitions and defaults
    - Constraints (primary keys, foreign keys, check, unique)
    - Indexes
    - Comments
    """
    sync_url = get_sync_test_db_url()

    with (
        psycopg.connect(sync_url, autocommit=True) as conn,
        conn.cursor() as cur,
    ):
        # Create the new schema
        cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')

        # Get all tables from public schema
        cur.execute("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        tables = [row[0] for row in cur.fetchall()]

        # Clone each table structure to the new schema
        for table in tables:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS "{schema_name}"."{table}"
                (LIKE public."{table}" INCLUDING ALL)
            """)


def drop_schema(schema_name: str) -> None:
    """Drop a schema and all its contents."""
    sync_url = get_sync_test_db_url()

    with (
        psycopg.connect(sync_url, autocommit=True) as conn,
        conn.cursor() as cur,
    ):
        cur.execute(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE')


def get_worker_id(request: pytest.FixtureRequest) -> str:
    """Get pytest-xdist worker ID, or 'main' if not running in parallel."""
    # pytest-xdist sets worker_id on the config
    worker_id = getattr(request.config, "workerinput", {}).get("workerid", "main")
    return worker_id


def generate_schema_name(request: pytest.FixtureRequest) -> str:
    """Generate a unique schema name for a test.

    Format: test_<worker_id>_<short_uuid>
    """
    worker_id = get_worker_id(request)
    test_id = uuid.uuid4().hex[:8]
    return f"test_{worker_id}_{test_id}"


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test database and run migrations once per test session.

    The database contains migrations applied to the 'public' schema,
    which serves as a template for individual test schemas.
    Database is automatically dropped after all tests complete.
    """
    create_test_database()
    run_migrations()
    yield
    drop_test_database()


@pytest.fixture
def admin_headers() -> dict[str, str]:
    """Return headers with admin authentication."""
    return {"Authorization": f"Bearer {settings.admin_token}"}


@pytest.fixture
async def client(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncGenerator[AsyncClient]:
    """Create an async test client with isolated database schema.

    Each test gets its own schema cloned from 'public', providing full
    isolation for parallel test execution. The schema is dropped after
    the test completes.

    Requires a running PostgreSQL database.
    For unit tests without a database, use a minimal app fixture.
    """
    from request_nest.db import create_engine, create_session_factory
    from request_nest.main import app
    from request_nest.observability import setup_logging

    # Generate unique schema for this test
    schema_name = generate_schema_name(request)
    create_schema_from_public(schema_name)

    try:
        # Override database URL to use test database
        test_db_url = get_test_database_url()
        monkeypatch.setattr(settings, "database_url", test_db_url)

        # Set up app with test database and schema isolation
        setup_logging(settings.log_level)
        engine = create_engine(test_db_url, schema=schema_name)

        app.state.db_engine = engine
        app.state.async_session = create_session_factory(engine)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as ac:
            yield ac

        await engine.dispose()
    finally:
        drop_schema(schema_name)


@pytest.fixture
async def db_session(client: AsyncClient) -> AsyncGenerator:
    """Create a database session for direct repository access in tests.

    This fixture depends on the client fixture to ensure the database
    and schema are properly set up. It provides access to the same
    session factory used by the app.

    Args:
        client: The test client (used to ensure proper setup order).
    """
    # client argument ensures proper fixture dependency ordering
    _ = client
    from request_nest.main import app

    async with app.state.async_session() as session:
        yield session
