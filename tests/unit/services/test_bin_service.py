"""Unit tests for BinService using FakeBinRepository."""

import pytest

from request_nest.dtos.v1 import BinResponse
from request_nest.services import BinService
from tests.fakes import FakeBinRepository


class FakeSession:
    """Fake session that tracks commit calls."""

    def __init__(self) -> None:
        self.commit_called = False

    async def commit(self) -> None:
        self.commit_called = True


class TestBinServiceCreate:
    """Tests for BinService.create_bin method."""

    @pytest.mark.asyncio
    async def test_create_bin_returns_bin_response(self) -> None:
        """create_bin returns a BinResponse DTO."""
        repo = FakeBinRepository()
        service = BinService(repository=repo)
        session = FakeSession()

        result = await service.create_bin(
            session=session,
            name="Test Bin",
            base_url="http://localhost:8000",
        )

        assert isinstance(result, BinResponse)
        assert result.name == "Test Bin"
        assert result.id.startswith("b_")

    @pytest.mark.asyncio
    async def test_create_bin_includes_ingest_url(self) -> None:
        """create_bin returns a BinResponse with correct ingest_url."""
        repo = FakeBinRepository()
        service = BinService(repository=repo)
        session = FakeSession()

        result = await service.create_bin(
            session=session,
            name="Test Bin",
            base_url="http://localhost:8000",
        )

        assert result.ingest_url == f"http://localhost:8000/b/{result.id}"

    @pytest.mark.asyncio
    async def test_create_bin_commits_session(self) -> None:
        """create_bin commits the session after creating the bin."""
        repo = FakeBinRepository()
        service = BinService(repository=repo)
        session = FakeSession()

        await service.create_bin(
            session=session,
            name="Test Bin",
            base_url="http://localhost:8000",
        )

        assert session.commit_called is True

    @pytest.mark.asyncio
    async def test_create_bin_with_none_name(self) -> None:
        """create_bin accepts None as name."""
        repo = FakeBinRepository()
        service = BinService(repository=repo)
        session = FakeSession()

        result = await service.create_bin(
            session=session,
            name=None,
            base_url="http://localhost:8000",
        )

        assert result.name is None


class TestBinServiceGet:
    """Tests for BinService.get_bin method."""

    @pytest.mark.asyncio
    async def test_get_bin_returns_bin_response_when_found(self) -> None:
        """get_bin returns a BinResponse when the bin exists."""
        repo = FakeBinRepository()
        service = BinService(repository=repo)
        session = FakeSession()

        # Create a bin first
        created = await service.create_bin(
            session=session,
            name="Find Me",
            base_url="http://localhost:8000",
        )

        result = await service.get_bin(
            session=session,
            bin_id=created.id,
            base_url="http://localhost:8000",
        )

        assert result is not None
        assert isinstance(result, BinResponse)
        assert result.id == created.id
        assert result.name == "Find Me"

    @pytest.mark.asyncio
    async def test_get_bin_returns_none_when_not_found(self) -> None:
        """get_bin returns None when the bin does not exist."""
        repo = FakeBinRepository()
        service = BinService(repository=repo)
        session = FakeSession()

        result = await service.get_bin(
            session=session,
            bin_id="b_nonexistent",
            base_url="http://localhost:8000",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_get_bin_includes_ingest_url(self) -> None:
        """get_bin returns a BinResponse with correct ingest_url."""
        repo = FakeBinRepository()
        service = BinService(repository=repo)
        session = FakeSession()

        created = await service.create_bin(
            session=session,
            name="URL Test",
            base_url="http://localhost:8000",
        )

        result = await service.get_bin(
            session=session,
            bin_id=created.id,
            base_url="http://example.com",
        )

        assert result is not None
        assert result.ingest_url == f"http://example.com/b/{created.id}"


class TestBinServiceList:
    """Tests for BinService.list_bins method."""

    @pytest.mark.asyncio
    async def test_list_bins_returns_empty_list_when_no_bins(self) -> None:
        """list_bins returns an empty list when no bins exist."""
        repo = FakeBinRepository()
        service = BinService(repository=repo)
        session = FakeSession()

        result = await service.list_bins(
            session=session,
            base_url="http://localhost:8000",
        )

        assert result == []

    @pytest.mark.asyncio
    async def test_list_bins_returns_all_bins(self) -> None:
        """list_bins returns all created bins."""
        repo = FakeBinRepository()
        service = BinService(repository=repo)
        session = FakeSession()

        await service.create_bin(session=session, name="Bin 1", base_url="http://localhost:8000")
        await service.create_bin(session=session, name="Bin 2", base_url="http://localhost:8000")
        await service.create_bin(session=session, name="Bin 3", base_url="http://localhost:8000")

        result = await service.list_bins(
            session=session,
            base_url="http://localhost:8000",
        )

        assert len(result) == 3
        names = {b.name for b in result}
        assert names == {"Bin 1", "Bin 2", "Bin 3"}

    @pytest.mark.asyncio
    async def test_list_bins_returns_bin_response_instances(self) -> None:
        """list_bins returns a list of BinResponse instances."""
        repo = FakeBinRepository()
        service = BinService(repository=repo)
        session = FakeSession()

        await service.create_bin(session=session, name="Type Check", base_url="http://localhost:8000")

        result = await service.list_bins(
            session=session,
            base_url="http://localhost:8000",
        )

        assert len(result) == 1
        assert isinstance(result[0], BinResponse)

    @pytest.mark.asyncio
    async def test_list_bins_includes_ingest_urls(self) -> None:
        """list_bins returns BinResponse instances with correct ingest_urls."""
        repo = FakeBinRepository()
        service = BinService(repository=repo)
        session = FakeSession()

        created = await service.create_bin(
            session=session,
            name="URL Check",
            base_url="http://localhost:8000",
        )

        result = await service.list_bins(
            session=session,
            base_url="http://example.com",
        )

        assert len(result) == 1
        assert result[0].ingest_url == f"http://example.com/b/{created.id}"
