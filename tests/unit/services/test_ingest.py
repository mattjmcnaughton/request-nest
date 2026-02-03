"""Unit tests for ingest functionality."""

import pytest

from request_nest.services import EventService, PayloadTooLargeError
from tests.fakes.fake_bin_repository import FakeBinRepository
from tests.fakes.fake_event_repository import FakeEventRepository


class FakeSession:
    """Fake session for unit testing."""

    async def commit(self) -> None:
        """No-op commit for testing."""
        pass


class TestIngestBodySizeValidation:
    """Tests for body size validation in ingest."""

    @pytest.mark.asyncio
    async def test_ingest_rejects_body_exceeding_max_size(self) -> None:
        """Ingest raises PayloadTooLargeError when body exceeds max_body_size."""
        bin_repo = FakeBinRepository()
        event_repo = FakeEventRepository()
        service = EventService(event_repository=event_repo, bin_repository=bin_repo)
        session = FakeSession()

        # Create a bin first
        bin_obj = await bin_repo.create(session, name="Test Bin")

        # Body of 100 bytes, max of 50
        body_bytes = b"x" * 100
        max_body_size = 50

        with pytest.raises(PayloadTooLargeError) as exc_info:
            await service.ingest_request(
                session=session,
                bin_id=bin_obj.id,
                method="POST",
                path="webhook",
                query_params={},
                headers={},
                body_bytes=body_bytes,
                remote_ip="127.0.0.1",
                max_body_size=max_body_size,
            )

        assert exc_info.value.max_size == 50
        assert exc_info.value.actual_size == 100

    @pytest.mark.asyncio
    async def test_ingest_accepts_body_at_max_size(self) -> None:
        """Ingest accepts body exactly at max_body_size."""
        bin_repo = FakeBinRepository()
        event_repo = FakeEventRepository()
        service = EventService(event_repository=event_repo, bin_repository=bin_repo)
        session = FakeSession()

        # Create a bin first
        bin_obj = await bin_repo.create(session, name="Test Bin")

        # Body exactly at max
        body_bytes = b"x" * 100
        max_body_size = 100

        event = await service.ingest_request(
            session=session,
            bin_id=bin_obj.id,
            method="POST",
            path="webhook",
            query_params={},
            headers={},
            body_bytes=body_bytes,
            remote_ip="127.0.0.1",
            max_body_size=max_body_size,
        )

        assert event is not None
        assert event.id.startswith("e_")

    @pytest.mark.asyncio
    async def test_ingest_accepts_body_under_max_size(self) -> None:
        """Ingest accepts body under max_body_size."""
        bin_repo = FakeBinRepository()
        event_repo = FakeEventRepository()
        service = EventService(event_repository=event_repo, bin_repository=bin_repo)
        session = FakeSession()

        # Create a bin first
        bin_obj = await bin_repo.create(session, name="Test Bin")

        # Body under max
        body_bytes = b"x" * 50
        max_body_size = 100

        event = await service.ingest_request(
            session=session,
            bin_id=bin_obj.id,
            method="POST",
            path="webhook",
            query_params={},
            headers={},
            body_bytes=body_bytes,
            remote_ip="127.0.0.1",
            max_body_size=max_body_size,
        )

        assert event is not None


class TestIngestBinValidation:
    """Tests for bin existence validation in ingest."""

    @pytest.mark.asyncio
    async def test_ingest_returns_none_when_bin_not_found(self) -> None:
        """Ingest returns None when bin doesn't exist."""
        bin_repo = FakeBinRepository()
        event_repo = FakeEventRepository()
        service = EventService(event_repository=event_repo, bin_repository=bin_repo)
        session = FakeSession()

        event = await service.ingest_request(
            session=session,
            bin_id="b_nonexistent",
            method="POST",
            path="webhook",
            query_params={},
            headers={},
            body_bytes=b"test",
            remote_ip="127.0.0.1",
            max_body_size=1000,
        )

        assert event is None


class TestIngestDataCapture:
    """Tests for data capture in ingest."""

    @pytest.mark.asyncio
    async def test_ingest_stores_all_request_data(self) -> None:
        """Ingest stores method, path, query_params, headers, body, and remote_ip."""
        bin_repo = FakeBinRepository()
        event_repo = FakeEventRepository()
        service = EventService(event_repository=event_repo, bin_repository=bin_repo)
        session = FakeSession()

        bin_obj = await bin_repo.create(session, name="Test Bin")

        event = await service.ingest_request(
            session=session,
            bin_id=bin_obj.id,
            method="PUT",
            path="api/v1/data",
            query_params={"key": "value", "foo": "bar"},
            headers={"content-type": "application/json", "x-custom": "header"},
            body_bytes=b'{"test": "data"}',
            remote_ip="192.168.1.1",
            max_body_size=1000,
        )

        assert event is not None
        assert event.method == "PUT"
        assert event.path == "api/v1/data"
        assert event.query_params == {"key": "value", "foo": "bar"}
        assert event.headers == {"content-type": "application/json", "x-custom": "header"}
        # Body is base64 encoded
        import base64

        assert base64.b64decode(event.body_b64) == b'{"test": "data"}'
        assert event.remote_ip == "192.168.1.1"
        assert event.bin_id == bin_obj.id
