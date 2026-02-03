"""Integration tests for Ingest API endpoint."""

import base64

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestIngestHttpMethods:
    """Tests for HTTP method capture."""

    @pytest.mark.asyncio
    async def test_ingest_captures_get_request(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """GET request is captured successfully."""
        # Create a bin first
        create_response = await client.post(
            "/api/v1/bins",
            json={"name": "GET Test"},
            headers=admin_headers,
        )
        bin_data = create_response.json()
        bin_id = bin_data["id"]

        # Send GET request to ingest
        response = await client.get(f"/b/{bin_id}/webhook")

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["event_id"].startswith("e_")

    @pytest.mark.asyncio
    async def test_ingest_captures_post_request(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """POST request is captured successfully."""
        create_response = await client.post(
            "/api/v1/bins",
            json={"name": "POST Test"},
            headers=admin_headers,
        )
        bin_id = create_response.json()["id"]

        response = await client.post(
            f"/b/{bin_id}/webhook",
            json={"test": "data"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["event_id"].startswith("e_")

    @pytest.mark.asyncio
    async def test_ingest_captures_put_request(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """PUT request is captured successfully."""
        create_response = await client.post(
            "/api/v1/bins",
            json={"name": "PUT Test"},
            headers=admin_headers,
        )
        bin_id = create_response.json()["id"]

        response = await client.put(
            f"/b/{bin_id}/resource/123",
            json={"update": "value"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True

    @pytest.mark.asyncio
    async def test_ingest_captures_delete_request(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """DELETE request is captured successfully."""
        create_response = await client.post(
            "/api/v1/bins",
            json={"name": "DELETE Test"},
            headers=admin_headers,
        )
        bin_id = create_response.json()["id"]

        response = await client.delete(f"/b/{bin_id}/resource/456")

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True

    @pytest.mark.asyncio
    async def test_ingest_captures_patch_request(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """PATCH request is captured successfully."""
        create_response = await client.post(
            "/api/v1/bins",
            json={"name": "PATCH Test"},
            headers=admin_headers,
        )
        bin_id = create_response.json()["id"]

        response = await client.patch(
            f"/b/{bin_id}/resource/789",
            json={"patch": "data"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True


@pytest.mark.integration
class TestIngestBinValidation:
    """Tests for bin existence validation."""

    @pytest.mark.asyncio
    async def test_ingest_returns_404_for_nonexistent_bin(
        self,
        client: AsyncClient,
    ) -> None:
        """Request to non-existent bin returns 404."""
        response = await client.post(
            "/b/b_nonexistent123/webhook",
            json={"test": "data"},
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"]["code"] == "NOT_FOUND"
        assert "b_nonexistent123" in data["detail"]["error"]["message"]


@pytest.mark.integration
class TestIngestSuccessResponse:
    """Tests for successful capture response format."""

    @pytest.mark.asyncio
    async def test_ingest_returns_200_with_event_id(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """Successful ingest returns 200 with ok=true and event_id."""
        create_response = await client.post(
            "/api/v1/bins",
            json={"name": "Response Test"},
            headers=admin_headers,
        )
        bin_id = create_response.json()["id"]

        response = await client.post(f"/b/{bin_id}/test")

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "event_id" in data
        assert data["event_id"].startswith("e_")

    @pytest.mark.asyncio
    async def test_ingest_stores_event_with_correct_data(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """Ingested request data is stored correctly and retrievable."""
        create_response = await client.post(
            "/api/v1/bins",
            json={"name": "Data Test"},
            headers=admin_headers,
        )
        bin_id = create_response.json()["id"]

        # Send request with specific data
        response = await client.post(
            f"/b/{bin_id}/webhook/path",
            params={"key": "value", "foo": "bar"},
            headers={"X-Custom-Header": "test-value"},
            json={"test": "payload"},
        )

        assert response.status_code == 200
        event_id = response.json()["event_id"]

        # Retrieve the event and verify data
        event_response = await client.get(
            f"/api/v1/events/{event_id}",
            headers=admin_headers,
        )

        assert event_response.status_code == 200
        event_data = event_response.json()

        assert event_data["method"] == "POST"
        assert event_data["path"] == "webhook/path"
        assert event_data["query_params"]["key"] == "value"
        assert event_data["query_params"]["foo"] == "bar"
        assert event_data["headers"]["x-custom-header"] == "test-value"
        assert event_data["bin_id"] == bin_id


@pytest.mark.integration
class TestIngestDataCapture:
    """Tests for request data capture."""

    @pytest.mark.asyncio
    async def test_ingest_captures_query_params(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """Query parameters are captured correctly."""
        create_response = await client.post(
            "/api/v1/bins",
            json={"name": "Query Params Test"},
            headers=admin_headers,
        )
        bin_id = create_response.json()["id"]

        response = await client.get(
            f"/b/{bin_id}/endpoint",
            params={"search": "test", "page": "1", "limit": "10"},
        )

        event_id = response.json()["event_id"]

        event_response = await client.get(
            f"/api/v1/events/{event_id}",
            headers=admin_headers,
        )

        event_data = event_response.json()
        assert event_data["query_params"]["search"] == "test"
        assert event_data["query_params"]["page"] == "1"
        assert event_data["query_params"]["limit"] == "10"

    @pytest.mark.asyncio
    async def test_ingest_captures_headers(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """HTTP headers are captured correctly."""
        create_response = await client.post(
            "/api/v1/bins",
            json={"name": "Headers Test"},
            headers=admin_headers,
        )
        bin_id = create_response.json()["id"]

        response = await client.post(
            f"/b/{bin_id}/webhook",
            headers={
                "X-Webhook-Secret": "secret123",
                "X-Request-Id": "req-456",
            },
            json={},
        )

        event_id = response.json()["event_id"]

        event_response = await client.get(
            f"/api/v1/events/{event_id}",
            headers=admin_headers,
        )

        event_data = event_response.json()
        assert event_data["headers"]["x-webhook-secret"] == "secret123"
        assert event_data["headers"]["x-request-id"] == "req-456"

    @pytest.mark.asyncio
    async def test_ingest_captures_body_as_base64(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """Request body is captured and decoded correctly."""
        create_response = await client.post(
            "/api/v1/bins",
            json={"name": "Body Test"},
            headers=admin_headers,
        )
        bin_id = create_response.json()["id"]

        test_body = '{"webhook": "payload", "number": 123}'
        response = await client.post(
            f"/b/{bin_id}/webhook",
            content=test_body,
            headers={"Content-Type": "application/json"},
        )

        event_id = response.json()["event_id"]

        event_response = await client.get(
            f"/api/v1/events/{event_id}",
            headers=admin_headers,
        )

        event_data = event_response.json()
        # Body is decoded in the response
        assert event_data["body"] == test_body

    @pytest.mark.asyncio
    async def test_ingest_captures_path_with_slashes(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """Path with multiple segments is captured correctly."""
        create_response = await client.post(
            "/api/v1/bins",
            json={"name": "Path Test"},
            headers=admin_headers,
        )
        bin_id = create_response.json()["id"]

        response = await client.post(f"/b/{bin_id}/api/v2/webhooks/github/push")

        event_id = response.json()["event_id"]

        event_response = await client.get(
            f"/api/v1/events/{event_id}",
            headers=admin_headers,
        )

        event_data = event_response.json()
        assert event_data["path"] == "api/v2/webhooks/github/push"

    @pytest.mark.asyncio
    async def test_ingest_captures_empty_body(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """Empty body is handled correctly."""
        create_response = await client.post(
            "/api/v1/bins",
            json={"name": "Empty Body Test"},
            headers=admin_headers,
        )
        bin_id = create_response.json()["id"]

        response = await client.post(f"/b/{bin_id}/webhook")

        event_id = response.json()["event_id"]

        event_response = await client.get(
            f"/api/v1/events/{event_id}",
            headers=admin_headers,
        )

        event_data = event_response.json()
        assert event_data["body"] == ""
        assert event_data["size_bytes"] == 0

    @pytest.mark.asyncio
    async def test_ingest_captures_binary_body(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """Binary body is stored as base64."""
        create_response = await client.post(
            "/api/v1/bins",
            json={"name": "Binary Body Test"},
            headers=admin_headers,
        )
        bin_id = create_response.json()["id"]

        # Send binary data
        binary_data = bytes(range(256))
        response = await client.post(
            f"/b/{bin_id}/upload",
            content=binary_data,
            headers={"Content-Type": "application/octet-stream"},
        )

        event_id = response.json()["event_id"]

        event_response = await client.get(
            f"/api/v1/events/{event_id}",
            headers=admin_headers,
        )

        event_data = event_response.json()
        # Binary data returns as base64 since it can't decode to UTF-8
        decoded = base64.b64decode(event_data["body"])
        assert decoded == binary_data


@pytest.mark.integration
class TestIngestNoAuth:
    """Tests that ingest endpoint is public (no auth required)."""

    @pytest.mark.asyncio
    async def test_ingest_works_without_auth_header(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """Ingest endpoint accepts requests without auth headers."""
        # Create bin with auth
        create_response = await client.post(
            "/api/v1/bins",
            json={"name": "No Auth Test"},
            headers=admin_headers,
        )
        bin_id = create_response.json()["id"]

        # Ingest WITHOUT any auth headers
        response = await client.post(
            f"/b/{bin_id}/webhook",
            json={"test": "data"},
            # No headers at all
        )

        assert response.status_code == 200
        assert response.json()["ok"] is True


@pytest.mark.integration
class TestIngestBodySizeValidation:
    """Tests for body size validation."""

    @pytest.mark.asyncio
    async def test_ingest_returns_413_when_content_length_exceeds_max(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Request with Content-Length exceeding max_body_size returns 413."""
        from request_nest.config import settings

        # Set a small max body size for testing
        monkeypatch.setattr(settings, "max_body_size", 100)

        create_response = await client.post(
            "/api/v1/bins",
            json={"name": "Size Test"},
            headers=admin_headers,
        )
        bin_id = create_response.json()["id"]

        # Send request with body larger than max
        large_body = "x" * 200
        response = await client.post(
            f"/b/{bin_id}/webhook",
            content=large_body,
            headers={"Content-Type": "text/plain"},
        )

        assert response.status_code == 413
        data = response.json()
        assert data["detail"]["error"]["code"] == "PAYLOAD_TOO_LARGE"


@pytest.mark.integration
class TestIngestEmptyPath:
    """Tests for empty path handling."""

    @pytest.mark.asyncio
    async def test_ingest_captures_request_at_root_path(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """Request to /b/{bin_id} (no trailing path) is captured."""
        create_response = await client.post(
            "/api/v1/bins",
            json={"name": "Root Path Test"},
            headers=admin_headers,
        )
        bin_id = create_response.json()["id"]

        # Send request to root path (no trailing segment)
        response = await client.post(
            f"/b/{bin_id}",
            json={"test": "root"},
        )

        assert response.status_code == 200
        event_id = response.json()["event_id"]

        # Verify event was captured with empty path
        event_response = await client.get(
            f"/api/v1/events/{event_id}",
            headers=admin_headers,
        )
        event_data = event_response.json()
        assert event_data["path"] == ""
