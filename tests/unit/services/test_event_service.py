"""Unit tests for EventService using fake repositories."""

import base64
from datetime import UTC, datetime

import pytest

from request_nest.domain import Event
from request_nest.dtos.v1 import EventDetail, EventSummary
from request_nest.services import EventService
from tests.fakes import FakeBinRepository, FakeEventRepository


class FakeSession:
    """Fake session for unit testing."""

    pass


def create_test_event(
    bin_id: str,
    event_id: str = "e_test123",
    method: str = "POST",
    path: str = "/webhook",
    body: str = "test body",
) -> Event:
    """Create a test event with given parameters."""
    return Event(
        id=event_id,
        bin_id=bin_id,
        method=method,
        path=path,
        query_params={"key": "value"},
        headers={"Content-Type": "application/json"},
        body_b64=base64.b64encode(body.encode()).decode(),
        remote_ip="127.0.0.1",
        created_at=datetime.now(tz=UTC),
    )


class TestEventServiceGetEvent:
    """Tests for EventService.get_event method."""

    @pytest.mark.asyncio
    async def test_get_event_returns_event_detail_when_found(self) -> None:
        """get_event returns an EventDetail DTO when the event exists."""
        bin_repo = FakeBinRepository()
        event_repo = FakeEventRepository()
        service = EventService(event_repository=event_repo, bin_repository=bin_repo)
        session = FakeSession()

        # Create test event directly
        event = create_test_event(bin_id="b_test123")
        event_repo.add_event(event)

        result = await service.get_event(session=session, event_id=event.id)

        assert result is not None
        assert isinstance(result, EventDetail)
        assert result.id == event.id
        assert result.method == "POST"
        assert result.path == "/webhook"

    @pytest.mark.asyncio
    async def test_get_event_decodes_body(self) -> None:
        """get_event returns EventDetail with decoded body."""
        bin_repo = FakeBinRepository()
        event_repo = FakeEventRepository()
        service = EventService(event_repository=event_repo, bin_repository=bin_repo)
        session = FakeSession()

        event = create_test_event(bin_id="b_test123", body="Hello, World!")
        event_repo.add_event(event)

        result = await service.get_event(session=session, event_id=event.id)

        assert result is not None
        assert result.body == "Hello, World!"

    @pytest.mark.asyncio
    async def test_get_event_returns_none_when_not_found(self) -> None:
        """get_event returns None when the event does not exist."""
        bin_repo = FakeBinRepository()
        event_repo = FakeEventRepository()
        service = EventService(event_repository=event_repo, bin_repository=bin_repo)
        session = FakeSession()

        result = await service.get_event(session=session, event_id="e_nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_event_includes_size_bytes(self) -> None:
        """get_event returns EventDetail with correct size_bytes."""
        bin_repo = FakeBinRepository()
        event_repo = FakeEventRepository()
        service = EventService(event_repository=event_repo, bin_repository=bin_repo)
        session = FakeSession()

        body = "test body"
        event = create_test_event(bin_id="b_test123", body=body)
        event_repo.add_event(event)

        result = await service.get_event(session=session, event_id=event.id)

        assert result is not None
        assert result.size_bytes == len(body)

    @pytest.mark.asyncio
    async def test_get_event_includes_all_fields(self) -> None:
        """get_event returns EventDetail with all expected fields."""
        bin_repo = FakeBinRepository()
        event_repo = FakeEventRepository()
        service = EventService(event_repository=event_repo, bin_repository=bin_repo)
        session = FakeSession()

        event = create_test_event(bin_id="b_test123")
        event_repo.add_event(event)

        result = await service.get_event(session=session, event_id=event.id)

        assert result is not None
        assert result.bin_id == "b_test123"
        assert result.query_params == {"key": "value"}
        assert result.headers == {"Content-Type": "application/json"}
        assert result.remote_ip == "127.0.0.1"
        assert result.created_at is not None


class TestEventServiceListEventsByBin:
    """Tests for EventService.list_events_by_bin method."""

    @pytest.mark.asyncio
    async def test_list_events_returns_empty_list_when_no_events(self) -> None:
        """list_events_by_bin returns empty list when no events exist for the bin."""
        bin_repo = FakeBinRepository()
        event_repo = FakeEventRepository()
        service = EventService(event_repository=event_repo, bin_repository=bin_repo)
        session = FakeSession()

        # Create a bin
        bin_obj = await bin_repo.create(session, name="Test Bin")

        result = await service.list_events_by_bin(session=session, bin_id=bin_obj.id)

        assert result is not None
        assert result == []

    @pytest.mark.asyncio
    async def test_list_events_returns_none_when_bin_not_found(self) -> None:
        """list_events_by_bin returns None when the bin does not exist."""
        bin_repo = FakeBinRepository()
        event_repo = FakeEventRepository()
        service = EventService(event_repository=event_repo, bin_repository=bin_repo)
        session = FakeSession()

        result = await service.list_events_by_bin(session=session, bin_id="b_nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_list_events_returns_event_summaries(self) -> None:
        """list_events_by_bin returns EventSummary DTOs."""
        bin_repo = FakeBinRepository()
        event_repo = FakeEventRepository()
        service = EventService(event_repository=event_repo, bin_repository=bin_repo)
        session = FakeSession()

        # Create bin and event
        bin_obj = await bin_repo.create(session, name="Test Bin")
        event = create_test_event(bin_id=bin_obj.id)
        event_repo.add_event(event)

        result = await service.list_events_by_bin(session=session, bin_id=bin_obj.id)

        assert result is not None
        assert len(result) == 1
        assert isinstance(result[0], EventSummary)

    @pytest.mark.asyncio
    async def test_list_events_summary_has_correct_fields(self) -> None:
        """list_events_by_bin returns EventSummary with id, method, path, size_bytes, created_at."""
        bin_repo = FakeBinRepository()
        event_repo = FakeEventRepository()
        service = EventService(event_repository=event_repo, bin_repository=bin_repo)
        session = FakeSession()

        bin_obj = await bin_repo.create(session, name="Test Bin")
        body = "test content"
        event = create_test_event(bin_id=bin_obj.id, body=body)
        event_repo.add_event(event)

        result = await service.list_events_by_bin(session=session, bin_id=bin_obj.id)

        assert result is not None
        assert len(result) == 1
        summary = result[0]
        assert summary.id == event.id
        assert summary.method == "POST"
        assert summary.path == "/webhook"
        assert summary.size_bytes == len(body)
        assert summary.created_at is not None

    @pytest.mark.asyncio
    async def test_list_events_respects_limit(self) -> None:
        """list_events_by_bin respects the limit parameter."""
        bin_repo = FakeBinRepository()
        event_repo = FakeEventRepository()
        service = EventService(event_repository=event_repo, bin_repository=bin_repo)
        session = FakeSession()

        bin_obj = await bin_repo.create(session, name="Test Bin")

        # Create 5 events
        for i in range(5):
            event = create_test_event(bin_id=bin_obj.id, event_id=f"e_test{i}")
            event_repo.add_event(event)

        result = await service.list_events_by_bin(session=session, bin_id=bin_obj.id, limit=3)

        assert result is not None
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_list_events_clamps_limit_to_max(self) -> None:
        """list_events_by_bin clamps limit to MAX_LIMIT (100)."""
        bin_repo = FakeBinRepository()
        event_repo = FakeEventRepository()
        service = EventService(event_repository=event_repo, bin_repository=bin_repo)
        session = FakeSession()

        bin_obj = await bin_repo.create(session, name="Test Bin")

        # Create 5 events
        for i in range(5):
            event = create_test_event(bin_id=bin_obj.id, event_id=f"e_test{i}")
            event_repo.add_event(event)

        # Request more than MAX_LIMIT
        result = await service.list_events_by_bin(session=session, bin_id=bin_obj.id, limit=200)

        # Should still work, but the effective limit is 100 (all 5 events returned)
        assert result is not None
        assert len(result) == 5

    @pytest.mark.asyncio
    async def test_list_events_default_limit_is_50(self) -> None:
        """list_events_by_bin uses default limit of 50."""
        bin_repo = FakeBinRepository()
        event_repo = FakeEventRepository()
        service = EventService(event_repository=event_repo, bin_repository=bin_repo)
        session = FakeSession()

        bin_obj = await bin_repo.create(session, name="Test Bin")

        # Create 60 events
        for i in range(60):
            event = create_test_event(bin_id=bin_obj.id, event_id=f"e_test{i}")
            event_repo.add_event(event)

        result = await service.list_events_by_bin(session=session, bin_id=bin_obj.id)

        assert result is not None
        assert len(result) == 50

    @pytest.mark.asyncio
    async def test_list_events_only_returns_events_for_specified_bin(self) -> None:
        """list_events_by_bin only returns events belonging to the specified bin."""
        bin_repo = FakeBinRepository()
        event_repo = FakeEventRepository()
        service = EventService(event_repository=event_repo, bin_repository=bin_repo)
        session = FakeSession()

        bin1 = await bin_repo.create(session, name="Bin 1")
        bin2 = await bin_repo.create(session, name="Bin 2")

        # Create events for both bins
        event1 = create_test_event(bin_id=bin1.id, event_id="e_bin1_event")
        event2 = create_test_event(bin_id=bin2.id, event_id="e_bin2_event")
        event_repo.add_event(event1)
        event_repo.add_event(event2)

        result = await service.list_events_by_bin(session=session, bin_id=bin1.id)

        assert result is not None
        assert len(result) == 1
        assert result[0].id == "e_bin1_event"
