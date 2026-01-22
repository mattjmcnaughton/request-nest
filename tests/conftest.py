"""Pytest configuration and fixtures."""

import pytest
from httpx import ASGITransport, AsyncClient

from request_nest.config import settings


@pytest.fixture
def admin_headers() -> dict[str, str]:
    """Return headers with admin authentication."""
    return {"Authorization": f"Bearer {settings.admin_token}"}


@pytest.fixture
async def client():
    """Create an async test client.

    Note: This fixture requires a running PostgreSQL database.
    For unit tests without a database, mock the db module.
    """
    from request_nest.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
