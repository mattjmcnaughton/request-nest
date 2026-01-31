"""Integration tests for EventRepository."""

import asyncio
import base64

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from request_nest.domain import Event
from request_nest.repositories import BinRepository, EventRepository


@pytest.mark.integration
class TestEventRepositoryCreate:
    """Tests for EventRepository.create method."""

    @pytest.mark.asyncio
    async def test_create_persists_event_and_returns_it(self, db_session: AsyncSession) -> None:
        """create() persists a new Event and returns it."""
        bin_repo = BinRepository()
        event_repo = EventRepository()

        parent_bin = await bin_repo.create(db_session, name="Test Bin")
        await db_session.commit()

        event = await event_repo.create(
            db_session,
            bin_id=parent_bin.id,
            method="POST",
            path="/webhook",
            query_params={"key": "value"},
            headers={"Content-Type": "application/json"},
            body_b64=base64.b64encode(b"test body").decode(),
            remote_ip="192.168.1.1",
        )
        await db_session.commit()

        assert event is not None
        assert event.bin_id == parent_bin.id
        assert event.method == "POST"
        assert event.path == "/webhook"
        assert event.created_at is not None

    @pytest.mark.asyncio
    async def test_create_generates_id_with_e_prefix(self, db_session: AsyncSession) -> None:
        """create() generates an ID with 'e_' prefix."""
        bin_repo = BinRepository()
        event_repo = EventRepository()

        parent_bin = await bin_repo.create(db_session, name="Prefix Test Bin")
        await db_session.commit()

        event = await event_repo.create(
            db_session,
            bin_id=parent_bin.id,
            method="GET",
            path="/",
            query_params={},
            headers={},
            body_b64="",
        )
        await db_session.commit()

        assert event.id.startswith("e_")
        assert len(event.id) >= 10

    @pytest.mark.asyncio
    async def test_create_stores_headers_and_query_params_as_jsonb(self, db_session: AsyncSession) -> None:
        """create() correctly stores and retrieves JSONB fields."""
        bin_repo = BinRepository()
        event_repo = EventRepository()

        parent_bin = await bin_repo.create(db_session, name="JSONB Test Bin")
        await db_session.commit()

        query_params = {"search": "test", "page": "1", "nested": "value"}
        headers = {
            "Content-Type": "application/json",
            "X-Custom-Header": "custom-value",
            "Accept": "application/json",
        }

        event = await event_repo.create(
            db_session,
            bin_id=parent_bin.id,
            method="POST",
            path="/api/test",
            query_params=query_params,
            headers=headers,
            body_b64="",
        )
        await db_session.commit()

        retrieved = await event_repo.get_by_id(db_session, event.id)

        assert retrieved is not None
        assert retrieved.query_params == query_params
        assert retrieved.headers == headers

    @pytest.mark.asyncio
    async def test_create_stores_body_b64_correctly(self, db_session: AsyncSession) -> None:
        """create() correctly stores and retrieves base64 body."""
        bin_repo = BinRepository()
        event_repo = EventRepository()

        parent_bin = await bin_repo.create(db_session, name="Body Test Bin")
        await db_session.commit()

        original_body = b"This is the request body content"
        body_b64 = base64.b64encode(original_body).decode()

        event = await event_repo.create(
            db_session,
            bin_id=parent_bin.id,
            method="POST",
            path="/upload",
            query_params={},
            headers={},
            body_b64=body_b64,
        )
        await db_session.commit()

        retrieved = await event_repo.get_by_id(db_session, event.id)

        assert retrieved is not None
        assert retrieved.body_b64 == body_b64
        assert base64.b64decode(retrieved.body_b64) == original_body


@pytest.mark.integration
class TestEventRepositoryGetById:
    """Tests for EventRepository.get_by_id method."""

    @pytest.mark.asyncio
    async def test_get_by_id_returns_existing_event(self, db_session: AsyncSession) -> None:
        """get_by_id() returns the correct Event for an existing ID."""
        bin_repo = BinRepository()
        event_repo = EventRepository()

        parent_bin = await bin_repo.create(db_session, name="Find Me Bin")
        await db_session.commit()

        created_event = await event_repo.create(
            db_session,
            bin_id=parent_bin.id,
            method="PUT",
            path="/resource/123",
            query_params={},
            headers={},
            body_b64="",
        )
        await db_session.commit()

        found_event = await event_repo.get_by_id(db_session, created_event.id)

        assert found_event is not None
        assert found_event.id == created_event.id
        assert found_event.method == "PUT"
        assert found_event.path == "/resource/123"

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_for_nonexistent_id(self, db_session: AsyncSession) -> None:
        """get_by_id() returns None for a non-existent ID."""
        event_repo = EventRepository()

        found_event = await event_repo.get_by_id(db_session, "e_nonexistent123")

        assert found_event is None


@pytest.mark.integration
class TestEventRepositoryListByBin:
    """Tests for EventRepository.list_by_bin method."""

    @pytest.mark.asyncio
    async def test_list_by_bin_returns_empty_list_when_no_events(self, db_session: AsyncSession) -> None:
        """list_by_bin() returns empty list when bin has no events."""
        bin_repo = BinRepository()
        event_repo = EventRepository()

        parent_bin = await bin_repo.create(db_session, name="Empty Bin")
        await db_session.commit()

        events = await event_repo.list_by_bin(db_session, parent_bin.id)

        assert events == []

    @pytest.mark.asyncio
    async def test_list_by_bin_returns_events_for_specified_bin_only(self, db_session: AsyncSession) -> None:
        """list_by_bin() returns only events for the specified bin."""
        bin_repo = BinRepository()
        event_repo = EventRepository()

        bin_a = await bin_repo.create(db_session, name="Bin A")
        bin_b = await bin_repo.create(db_session, name="Bin B")
        await db_session.commit()

        await event_repo.create(
            db_session,
            bin_id=bin_a.id,
            method="GET",
            path="/a1",
            query_params={},
            headers={},
            body_b64="",
        )
        await event_repo.create(
            db_session,
            bin_id=bin_a.id,
            method="GET",
            path="/a2",
            query_params={},
            headers={},
            body_b64="",
        )
        await event_repo.create(
            db_session,
            bin_id=bin_b.id,
            method="GET",
            path="/b1",
            query_params={},
            headers={},
            body_b64="",
        )
        await db_session.commit()

        events_a = await event_repo.list_by_bin(db_session, bin_a.id)
        events_b = await event_repo.list_by_bin(db_session, bin_b.id)

        assert len(events_a) == 2
        assert all(e.bin_id == bin_a.id for e in events_a)
        assert {e.path for e in events_a} == {"/a1", "/a2"}

        assert len(events_b) == 1
        assert events_b[0].bin_id == bin_b.id
        assert events_b[0].path == "/b1"

    @pytest.mark.asyncio
    async def test_list_by_bin_returns_events_ordered_by_created_at_desc(self, db_session: AsyncSession) -> None:
        """list_by_bin() returns events ordered by created_at descending (newest first)."""
        bin_repo = BinRepository()
        event_repo = EventRepository()

        parent_bin = await bin_repo.create(db_session, name="Order Test Bin")
        await db_session.commit()

        first_event = await event_repo.create(
            db_session,
            bin_id=parent_bin.id,
            method="GET",
            path="/first",
            query_params={},
            headers={},
            body_b64="",
        )
        await db_session.commit()
        await asyncio.sleep(0.01)

        second_event = await event_repo.create(
            db_session,
            bin_id=parent_bin.id,
            method="GET",
            path="/second",
            query_params={},
            headers={},
            body_b64="",
        )
        await db_session.commit()
        await asyncio.sleep(0.01)

        third_event = await event_repo.create(
            db_session,
            bin_id=parent_bin.id,
            method="GET",
            path="/third",
            query_params={},
            headers={},
            body_b64="",
        )
        await db_session.commit()

        events = await event_repo.list_by_bin(db_session, parent_bin.id)

        assert len(events) == 3
        assert events[0].id == third_event.id
        assert events[1].id == second_event.id
        assert events[2].id == first_event.id

    @pytest.mark.asyncio
    async def test_list_by_bin_respects_limit_parameter(self, db_session: AsyncSession) -> None:
        """list_by_bin() respects the limit parameter."""
        bin_repo = BinRepository()
        event_repo = EventRepository()

        parent_bin = await bin_repo.create(db_session, name="Limit Test Bin")
        await db_session.commit()

        for i in range(5):
            await event_repo.create(
                db_session,
                bin_id=parent_bin.id,
                method="GET",
                path=f"/event{i}",
                query_params={},
                headers={},
                body_b64="",
            )
        await db_session.commit()

        events = await event_repo.list_by_bin(db_session, parent_bin.id, limit=3)

        assert len(events) == 3

    @pytest.mark.asyncio
    async def test_list_by_bin_uses_default_limit_of_50(self, db_session: AsyncSession) -> None:
        """list_by_bin() uses default limit of 50."""
        bin_repo = BinRepository()
        event_repo = EventRepository()

        parent_bin = await bin_repo.create(db_session, name="Default Limit Bin")
        await db_session.commit()

        for i in range(55):
            await event_repo.create(
                db_session,
                bin_id=parent_bin.id,
                method="GET",
                path=f"/event{i}",
                query_params={},
                headers={},
                body_b64="",
            )
        await db_session.commit()

        events = await event_repo.list_by_bin(db_session, parent_bin.id)

        assert len(events) == 50

    @pytest.mark.asyncio
    async def test_list_by_bin_returns_event_instances(self, db_session: AsyncSession) -> None:
        """list_by_bin() returns a list of Event instances."""
        bin_repo = BinRepository()
        event_repo = EventRepository()

        parent_bin = await bin_repo.create(db_session, name="Type Check Bin")
        await db_session.commit()

        await event_repo.create(
            db_session,
            bin_id=parent_bin.id,
            method="GET",
            path="/check",
            query_params={},
            headers={},
            body_b64="",
        )
        await db_session.commit()

        events = await event_repo.list_by_bin(db_session, parent_bin.id)

        assert len(events) == 1
        assert isinstance(events[0], Event)
