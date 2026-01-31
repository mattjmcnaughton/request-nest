"""Integration tests for BinRepository."""

import asyncio

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from request_nest.domain import Bin
from request_nest.repositories import BinRepository


@pytest.mark.integration
class TestBinRepositoryCreate:
    """Tests for BinRepository.create method."""

    @pytest.mark.asyncio
    async def test_create_persists_bin_and_returns_it(self, db_session: AsyncSession) -> None:
        """create() persists a new Bin and returns it."""
        repo = BinRepository()

        bin_obj = await repo.create(db_session, name="Test Bin")
        await db_session.commit()

        assert bin_obj is not None
        assert bin_obj.name == "Test Bin"
        assert bin_obj.created_at is not None

    @pytest.mark.asyncio
    async def test_create_generates_id_with_b_prefix(self, db_session: AsyncSession) -> None:
        """create() generates an ID with 'b_' prefix."""
        repo = BinRepository()

        bin_obj = await repo.create(db_session, name="Prefix Test")
        await db_session.commit()

        assert bin_obj.id.startswith("b_")
        # token_urlsafe(12) produces 16 chars, plus 2 for prefix = ~18 chars
        assert len(bin_obj.id) >= 10

    @pytest.mark.asyncio
    async def test_create_with_none_name(self, db_session: AsyncSession) -> None:
        """create() accepts None as name."""
        repo = BinRepository()

        bin_obj = await repo.create(db_session, name=None)
        await db_session.commit()

        assert bin_obj.name is None

    @pytest.mark.asyncio
    async def test_create_without_name_defaults_to_none(self, db_session: AsyncSession) -> None:
        """create() defaults name to None when not provided."""
        repo = BinRepository()

        bin_obj = await repo.create(db_session)
        await db_session.commit()

        assert bin_obj.name is None


@pytest.mark.integration
class TestBinRepositoryGetById:
    """Tests for BinRepository.get_by_id method."""

    @pytest.mark.asyncio
    async def test_get_by_id_returns_existing_bin(self, db_session: AsyncSession) -> None:
        """get_by_id() returns the correct Bin for an existing ID."""
        repo = BinRepository()
        created_bin = await repo.create(db_session, name="Find Me")
        await db_session.commit()

        found_bin = await repo.get_by_id(db_session, created_bin.id)

        assert found_bin is not None
        assert found_bin.id == created_bin.id
        assert found_bin.name == "Find Me"

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_for_nonexistent_id(self, db_session: AsyncSession) -> None:
        """get_by_id() returns None for a non-existent ID."""
        repo = BinRepository()

        found_bin = await repo.get_by_id(db_session, "b_nonexistent123")

        assert found_bin is None


@pytest.mark.integration
class TestBinRepositoryListAll:
    """Tests for BinRepository.list_all method."""

    @pytest.mark.asyncio
    async def test_list_all_returns_empty_list_when_no_bins(self, db_session: AsyncSession) -> None:
        """list_all() returns empty list when no bins exist."""
        repo = BinRepository()

        bins = await repo.list_all(db_session)

        assert bins == []

    @pytest.mark.asyncio
    async def test_list_all_returns_all_bins(self, db_session: AsyncSession) -> None:
        """list_all() returns all created bins."""
        repo = BinRepository()
        await repo.create(db_session, name="Bin 1")
        await repo.create(db_session, name="Bin 2")
        await repo.create(db_session, name="Bin 3")
        await db_session.commit()

        bins = await repo.list_all(db_session)

        assert len(bins) == 3
        names = {b.name for b in bins}
        assert names == {"Bin 1", "Bin 2", "Bin 3"}

    @pytest.mark.asyncio
    async def test_list_all_returns_bins_ordered_by_created_at_desc(self, db_session: AsyncSession) -> None:
        """list_all() returns bins ordered by created_at descending (newest first)."""
        repo = BinRepository()

        # Create bins with small delays to ensure different timestamps
        first_bin = await repo.create(db_session, name="First")
        await db_session.commit()
        await asyncio.sleep(0.01)

        second_bin = await repo.create(db_session, name="Second")
        await db_session.commit()
        await asyncio.sleep(0.01)

        third_bin = await repo.create(db_session, name="Third")
        await db_session.commit()

        bins = await repo.list_all(db_session)

        assert len(bins) == 3
        # Newest first (descending order)
        assert bins[0].id == third_bin.id
        assert bins[1].id == second_bin.id
        assert bins[2].id == first_bin.id

    @pytest.mark.asyncio
    async def test_list_all_returns_bin_instances(self, db_session: AsyncSession) -> None:
        """list_all() returns a list of Bin instances."""
        repo = BinRepository()
        await repo.create(db_session, name="Type Check")
        await db_session.commit()

        bins = await repo.list_all(db_session)

        assert len(bins) == 1
        assert isinstance(bins[0], Bin)
