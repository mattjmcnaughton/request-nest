"""Integration tests for Bin API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestCreateBin:
    """Tests for POST /api/v1/bins endpoint."""

    @pytest.mark.asyncio
    async def test_create_bin_with_auth_returns_201(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """POST /api/v1/bins returns 201 with valid auth."""
        response = await client.post(
            "/api/v1/bins",
            json={"name": "Test Bin"},
            headers=admin_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["id"].startswith("b_")
        assert data["name"] == "Test Bin"
        assert "ingest_url" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_bin_ingest_url_contains_bin_id(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """POST /api/v1/bins returns ingest_url containing the bin ID."""
        response = await client.post(
            "/api/v1/bins",
            json={"name": "URL Test"},
            headers=admin_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] in data["ingest_url"]
        assert "/b/" in data["ingest_url"]

    @pytest.mark.asyncio
    async def test_create_bin_with_none_name(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """POST /api/v1/bins accepts null name."""
        response = await client.post(
            "/api/v1/bins",
            json={"name": None},
            headers=admin_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] is None

    @pytest.mark.asyncio
    async def test_create_bin_with_empty_body(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """POST /api/v1/bins accepts empty body (name defaults to null)."""
        response = await client.post(
            "/api/v1/bins",
            json={},
            headers=admin_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] is None

    @pytest.mark.asyncio
    async def test_create_bin_without_auth_returns_401(
        self,
        client: AsyncClient,
    ) -> None:
        """POST /api/v1/bins returns 401 without auth header."""
        response = await client.post(
            "/api/v1/bins",
            json={"name": "Test Bin"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"]["code"] == "UNAUTHORIZED"
        assert "message" in data["detail"]["error"]

    @pytest.mark.asyncio
    async def test_create_bin_with_invalid_token_returns_401(
        self,
        client: AsyncClient,
    ) -> None:
        """POST /api/v1/bins returns 401 with invalid token."""
        response = await client.post(
            "/api/v1/bins",
            json={"name": "Test Bin"},
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.integration
class TestListBins:
    """Tests for GET /api/v1/bins endpoint."""

    @pytest.mark.asyncio
    async def test_list_bins_with_auth_returns_200(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """GET /api/v1/bins returns 200 with valid auth."""
        response = await client.get(
            "/api/v1/bins",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "bins" in data
        assert isinstance(data["bins"], list)

    @pytest.mark.asyncio
    async def test_list_bins_returns_created_bins(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """GET /api/v1/bins returns previously created bins."""
        # Create some bins first
        await client.post("/api/v1/bins", json={"name": "Bin 1"}, headers=admin_headers)
        await client.post("/api/v1/bins", json={"name": "Bin 2"}, headers=admin_headers)

        response = await client.get(
            "/api/v1/bins",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["bins"]) >= 2
        names = {b["name"] for b in data["bins"]}
        assert "Bin 1" in names
        assert "Bin 2" in names

    @pytest.mark.asyncio
    async def test_list_bins_without_auth_returns_401(
        self,
        client: AsyncClient,
    ) -> None:
        """GET /api/v1/bins returns 401 without auth header."""
        response = await client.get("/api/v1/bins")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"]["code"] == "UNAUTHORIZED"

    @pytest.mark.asyncio
    async def test_list_bins_with_invalid_token_returns_401(
        self,
        client: AsyncClient,
    ) -> None:
        """GET /api/v1/bins returns 401 with invalid token."""
        response = await client.get(
            "/api/v1/bins",
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == 401


@pytest.mark.integration
class TestGetBin:
    """Tests for GET /api/v1/bins/{bin_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_bin_with_auth_returns_200(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """GET /api/v1/bins/{bin_id} returns 200 for existing bin."""
        # Create a bin first
        create_response = await client.post(
            "/api/v1/bins",
            json={"name": "Get Me"},
            headers=admin_headers,
        )
        created_bin = create_response.json()

        response = await client.get(
            f"/api/v1/bins/{created_bin['id']}",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_bin["id"]
        assert data["name"] == "Get Me"
        assert "ingest_url" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_get_bin_not_found_returns_404(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """GET /api/v1/bins/{bin_id} returns 404 for non-existent bin."""
        response = await client.get(
            "/api/v1/bins/b_nonexistent123",
            headers=admin_headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"]["code"] == "NOT_FOUND"
        assert "b_nonexistent123" in data["detail"]["error"]["message"]

    @pytest.mark.asyncio
    async def test_get_bin_without_auth_returns_401(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """GET /api/v1/bins/{bin_id} returns 401 without auth header."""
        # Create a bin first
        create_response = await client.post(
            "/api/v1/bins",
            json={"name": "Auth Test"},
            headers=admin_headers,
        )
        created_bin = create_response.json()

        # Try to get without auth
        response = await client.get(f"/api/v1/bins/{created_bin['id']}")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"]["code"] == "UNAUTHORIZED"

    @pytest.mark.asyncio
    async def test_get_bin_with_invalid_token_returns_401(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """GET /api/v1/bins/{bin_id} returns 401 with invalid token."""
        # Create a bin first
        create_response = await client.post(
            "/api/v1/bins",
            json={"name": "Token Test"},
            headers=admin_headers,
        )
        created_bin = create_response.json()

        # Try to get with invalid token
        response = await client.get(
            f"/api/v1/bins/{created_bin['id']}",
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == 401
