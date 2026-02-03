"""Fake BinRepository for unit testing."""

import secrets
from datetime import UTC, datetime
from typing import Any

from request_nest.domain import Bin

__all__ = ["FakeBinRepository"]


class FakeBinRepository:
    """In-memory fake implementation of BinRepository.

    Stores bins in a dictionary for testing without database access.
    Implements the same interface as BinRepository.
    """

    def __init__(self) -> None:
        """Initialize the fake repository with empty storage."""
        self._bins: dict[str, Bin] = {}

    def clear(self) -> None:
        """Clear all stored bins."""
        self._bins.clear()

    async def create(self, session: Any, name: str | None = None) -> Bin:  # noqa: ARG002
        """Create a new Bin and store it in memory.

        Args:
            session: Ignored (for interface compatibility).
            name: Optional human-readable name for the bin.

        Returns:
            The created Bin with generated ID and timestamp.
        """
        bin_id = f"b_{secrets.token_urlsafe(12)}"
        bin_obj = Bin(
            id=bin_id,
            name=name,
            created_at=datetime.now(tz=UTC),
        )
        self._bins[bin_id] = bin_obj
        return bin_obj

    async def get_by_id(self, session: Any, bin_id: str) -> Bin | None:  # noqa: ARG002
        """Retrieve a Bin by its ID.

        Args:
            session: Ignored (for interface compatibility).
            bin_id: The unique identifier of the bin.

        Returns:
            The Bin if found, None otherwise.
        """
        return self._bins.get(bin_id)

    async def list_all(self, session: Any) -> list[Bin]:  # noqa: ARG002
        """Retrieve all Bins ordered by creation date (newest first).

        Args:
            session: Ignored (for interface compatibility).

        Returns:
            List of all Bins ordered by created_at descending.
        """
        return sorted(
            self._bins.values(),
            key=lambda b: b.created_at,
            reverse=True,
        )
