"""Tests for health endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from request_nest import __version__


@pytest.fixture
async def minimal_client():
    """Create a test client with health routes only (no database)."""
    from fastapi import FastAPI

    from request_nest.routes.v1.health import router

    app = FastAPI()
    app.include_router(router, prefix="/api/v1")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


class TestHealthEndpoint:
    """Tests for /health liveness endpoint (no database required)."""

    @pytest.mark.asyncio
    async def test_health_returns_healthy_status(self, minimal_client: AsyncClient) -> None:
        """Test the health endpoint returns healthy status."""
        response = await minimal_client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == __version__


@pytest.mark.integration
class TestReadyEndpoint:
    """Tests for /ready readiness endpoint (requires database)."""

    @pytest.mark.asyncio
    async def test_ready_returns_ready_when_database_connected(self, client: AsyncClient) -> None:
        """Test the ready endpoint returns ready status when database is available."""
        response = await client.get("/api/v1/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["version"] == __version__
