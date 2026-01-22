"""Tests for health endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from request_nest import __version__
from request_nest.routes.v1.health import router


@pytest.fixture
async def client():
    """Create a test client with health routes."""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router, prefix="/api/v1")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient) -> None:
    """Test the health endpoint returns healthy status."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == __version__


@pytest.mark.asyncio
async def test_ready_endpoint(client: AsyncClient) -> None:
    """Test the ready endpoint returns ready status."""
    response = await client.get("/api/v1/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["version"] == __version__
