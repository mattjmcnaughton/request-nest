"""Integration tests for Event API endpoints."""

import base64

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from request_nest.repositories import BinRepository, EventRepository


@pytest.mark.integration
class TestGetEvent:
    """Tests for GET /api/v1/events/{event_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_event_with_auth_returns_200(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
        db_session: AsyncSession,
    ) -> None:
        """GET /api/v1/events/{event_id} returns 200 for existing event."""
        # Create a bin and event directly
        bin_repo = BinRepository()
        event_repo = EventRepository()

        bin_obj = await bin_repo.create(db_session, name="Test Bin")
        event = await event_repo.create(
            db_session,
            bin_id=bin_obj.id,
            method="POST",
            path="/webhook",
            query_params={"key": "value"},
            headers={"Content-Type": "application/json"},
            body_b64=base64.b64encode(b"test body").decode(),
            remote_ip="127.0.0.1",
        )
        await db_session.commit()

        response = await client.get(
            f"/api/v1/events/{event.id}",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == event.id
        assert data["bin_id"] == bin_obj.id
        assert data["method"] == "POST"
        assert data["path"] == "/webhook"
        assert data["body"] == "test body"
        assert data["size_bytes"] == len(b"test body")

    @pytest.mark.asyncio
    async def test_get_event_returns_decoded_body(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
        db_session: AsyncSession,
    ) -> None:
        """GET /api/v1/events/{event_id} returns decoded body."""
        bin_repo = BinRepository()
        event_repo = EventRepository()

        bin_obj = await bin_repo.create(db_session, name="Test Bin")
        original_body = "Hello, World! 🌍"
        event = await event_repo.create(
            db_session,
            bin_id=bin_obj.id,
            method="POST",
            path="/test",
            query_params={},
            headers={},
            body_b64=base64.b64encode(original_body.encode()).decode(),
        )
        await db_session.commit()

        response = await client.get(
            f"/api/v1/events/{event.id}",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["body"] == original_body

    @pytest.mark.asyncio
    async def test_get_event_not_found_returns_404(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """GET /api/v1/events/{event_id} returns 404 for non-existent event."""
        response = await client.get(
            "/api/v1/events/e_nonexistent123",
            headers=admin_headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"]["code"] == "NOT_FOUND"
        assert "e_nonexistent123" in data["detail"]["error"]["message"]

    @pytest.mark.asyncio
    async def test_get_event_without_auth_returns_401(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """GET /api/v1/events/{event_id} returns 401 without auth header."""
        # Create an event
        bin_repo = BinRepository()
        event_repo = EventRepository()

        bin_obj = await bin_repo.create(db_session, name="Test Bin")
        event = await event_repo.create(
            db_session,
            bin_id=bin_obj.id,
            method="GET",
            path="/test",
            query_params={},
            headers={},
            body_b64="",
        )
        await db_session.commit()

        response = await client.get(f"/api/v1/events/{event.id}")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"]["code"] == "UNAUTHORIZED"

    @pytest.mark.asyncio
    async def test_get_event_with_invalid_token_returns_401(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """GET /api/v1/events/{event_id} returns 401 with invalid token."""
        bin_repo = BinRepository()
        event_repo = EventRepository()

        bin_obj = await bin_repo.create(db_session, name="Test Bin")
        event = await event_repo.create(
            db_session,
            bin_id=bin_obj.id,
            method="GET",
            path="/test",
            query_params={},
            headers={},
            body_b64="",
        )
        await db_session.commit()

        response = await client.get(
            f"/api/v1/events/{event.id}",
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_event_includes_all_fields(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
        db_session: AsyncSession,
    ) -> None:
        """GET /api/v1/events/{event_id} includes all expected fields."""
        bin_repo = BinRepository()
        event_repo = EventRepository()

        bin_obj = await bin_repo.create(db_session, name="Test Bin")
        event = await event_repo.create(
            db_session,
            bin_id=bin_obj.id,
            method="PUT",
            path="/update",
            query_params={"id": "123", "action": "update"},
            headers={"X-Custom": "header", "Content-Type": "text/plain"},
            body_b64=base64.b64encode(b"update content").decode(),
            remote_ip="192.168.1.1",
        )
        await db_session.commit()

        response = await client.get(
            f"/api/v1/events/{event.id}",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == event.id
        assert data["bin_id"] == bin_obj.id
        assert data["method"] == "PUT"
        assert data["path"] == "/update"
        assert data["query_params"] == {"id": "123", "action": "update"}
        assert data["headers"] == {"X-Custom": "header", "Content-Type": "text/plain"}
        assert data["body"] == "update content"
        assert data["remote_ip"] == "192.168.1.1"
        assert data["size_bytes"] == len(b"update content")
        assert "created_at" in data


@pytest.mark.integration
class TestListEventsByBin:
    """Tests for GET /api/v1/bins/{bin_id}/events endpoint."""

    @pytest.mark.asyncio
    async def test_list_events_with_auth_returns_200(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
        db_session: AsyncSession,
    ) -> None:
        """GET /api/v1/bins/{bin_id}/events returns 200 with valid auth."""
        bin_repo = BinRepository()
        bin_obj = await bin_repo.create(db_session, name="Test Bin")
        await db_session.commit()

        response = await client.get(
            f"/api/v1/bins/{bin_obj.id}/events",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert isinstance(data["events"], list)

    @pytest.mark.asyncio
    async def test_list_events_returns_event_summaries(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
        db_session: AsyncSession,
    ) -> None:
        """GET /api/v1/bins/{bin_id}/events returns event summaries."""
        bin_repo = BinRepository()
        event_repo = EventRepository()

        bin_obj = await bin_repo.create(db_session, name="Test Bin")
        event = await event_repo.create(
            db_session,
            bin_id=bin_obj.id,
            method="POST",
            path="/webhook",
            query_params={},
            headers={},
            body_b64=base64.b64encode(b"test").decode(),
        )
        await db_session.commit()

        response = await client.get(
            f"/api/v1/bins/{bin_obj.id}/events",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) == 1
        summary = data["events"][0]
        assert summary["id"] == event.id
        assert summary["method"] == "POST"
        assert summary["path"] == "/webhook"
        assert summary["size_bytes"] == 4
        assert "created_at" in summary

    @pytest.mark.asyncio
    async def test_list_events_bin_not_found_returns_404(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """GET /api/v1/bins/{bin_id}/events returns 404 for non-existent bin."""
        response = await client.get(
            "/api/v1/bins/b_nonexistent123/events",
            headers=admin_headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"]["code"] == "NOT_FOUND"
        assert "b_nonexistent123" in data["detail"]["error"]["message"]

    @pytest.mark.asyncio
    async def test_list_events_without_auth_returns_401(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """GET /api/v1/bins/{bin_id}/events returns 401 without auth header."""
        bin_repo = BinRepository()
        bin_obj = await bin_repo.create(db_session, name="Test Bin")
        await db_session.commit()

        response = await client.get(f"/api/v1/bins/{bin_obj.id}/events")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_events_with_invalid_token_returns_401(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """GET /api/v1/bins/{bin_id}/events returns 401 with invalid token."""
        bin_repo = BinRepository()
        bin_obj = await bin_repo.create(db_session, name="Test Bin")
        await db_session.commit()

        response = await client.get(
            f"/api/v1/bins/{bin_obj.id}/events",
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_events_respects_limit_parameter(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
        db_session: AsyncSession,
    ) -> None:
        """GET /api/v1/bins/{bin_id}/events?limit=N respects limit parameter."""
        bin_repo = BinRepository()
        event_repo = EventRepository()

        bin_obj = await bin_repo.create(db_session, name="Test Bin")
        # Create 5 events
        for i in range(5):
            await event_repo.create(
                db_session,
                bin_id=bin_obj.id,
                method="POST",
                path=f"/webhook{i}",
                query_params={},
                headers={},
                body_b64="",
            )
        await db_session.commit()

        response = await client.get(
            f"/api/v1/bins/{bin_obj.id}/events?limit=3",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) == 3

    @pytest.mark.asyncio
    async def test_list_events_default_limit_is_50(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
        db_session: AsyncSession,
    ) -> None:
        """GET /api/v1/bins/{bin_id}/events uses default limit of 50."""
        bin_repo = BinRepository()
        event_repo = EventRepository()

        bin_obj = await bin_repo.create(db_session, name="Test Bin")
        # Create 60 events
        for i in range(60):
            await event_repo.create(
                db_session,
                bin_id=bin_obj.id,
                method="POST",
                path=f"/webhook{i}",
                query_params={},
                headers={},
                body_b64="",
            )
        await db_session.commit()

        response = await client.get(
            f"/api/v1/bins/{bin_obj.id}/events",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) == 50

    @pytest.mark.asyncio
    async def test_list_events_max_limit_is_100(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """GET /api/v1/bins/{bin_id}/events rejects limit > 100."""
        response = await client.get(
            "/api/v1/bins/b_test/events?limit=101",
            headers=admin_headers,
        )

        # FastAPI validates query param and returns 422 for invalid values
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_events_min_limit_is_1(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """GET /api/v1/bins/{bin_id}/events rejects limit < 1."""
        response = await client.get(
            "/api/v1/bins/b_test/events?limit=0",
            headers=admin_headers,
        )

        # FastAPI validates query param and returns 422 for invalid values
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_events_only_returns_events_for_specified_bin(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
        db_session: AsyncSession,
    ) -> None:
        """GET /api/v1/bins/{bin_id}/events only returns events for that bin."""
        bin_repo = BinRepository()
        event_repo = EventRepository()

        bin1 = await bin_repo.create(db_session, name="Bin 1")
        bin2 = await bin_repo.create(db_session, name="Bin 2")

        # Create events for both bins
        await event_repo.create(
            db_session,
            bin_id=bin1.id,
            method="POST",
            path="/bin1-event",
            query_params={},
            headers={},
            body_b64="",
        )
        await event_repo.create(
            db_session,
            bin_id=bin2.id,
            method="POST",
            path="/bin2-event",
            query_params={},
            headers={},
            body_b64="",
        )
        await db_session.commit()

        response = await client.get(
            f"/api/v1/bins/{bin1.id}/events",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) == 1
        assert data["events"][0]["path"] == "/bin1-event"
