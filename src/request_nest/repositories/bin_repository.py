"""Repository for Bin persistence operations."""

import secrets

from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from request_nest.domain import Bin

__all__ = ["BinRepository"]


class BinRepository:
    """Repository for Bin CRUD operations.

    All methods accept an AsyncSession for external transaction control.
    The caller is responsible for committing or rolling back transactions.
    """

    async def create(self, session: AsyncSession, name: str | None = None) -> Bin:
        """Create a new Bin and persist it to the database.

        Args:
            session: The async database session.
            name: Optional human-readable name for the bin.

        Returns:
            The created Bin with generated ID and server-set created_at.
        """
        bin_id = f"b_{secrets.token_urlsafe(12)}"
        bin_obj = Bin(id=bin_id, name=name)

        session.add(bin_obj)
        await session.flush()
        await session.refresh(bin_obj)

        return bin_obj

    async def get_by_id(self, session: AsyncSession, bin_id: str) -> Bin | None:
        """Retrieve a Bin by its ID.

        Args:
            session: The async database session.
            bin_id: The unique identifier of the bin.

        Returns:
            The Bin if found, None otherwise.
        """
        result = await session.execute(select(Bin).where(Bin.id == bin_id))
        return result.scalars().first()

    async def list_all(self, session: AsyncSession) -> list[Bin]:
        """Retrieve all Bins ordered by creation date (newest first).

        Args:
            session: The async database session.

        Returns:
            List of all Bins ordered by created_at descending.
        """
        result = await session.execute(
            select(Bin).order_by(desc(Bin.created_at))  # type: ignore[arg-type]
        )
        return list(result.scalars().all())
