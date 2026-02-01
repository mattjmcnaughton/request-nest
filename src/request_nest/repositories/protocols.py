"""Protocol definitions for repository interfaces."""

from typing import Any, Protocol

from request_nest.domain import Bin

__all__ = ["BinRepositoryProtocol"]


class BinRepositoryProtocol(Protocol):
    """Protocol defining the interface for Bin repository operations.

    This protocol enables type-safe dependency injection and testing with fakes.
    Both BinRepository (real) and FakeBinRepository (test) implement this interface.
    """

    async def create(self, session: Any, name: str | None = None) -> Bin:
        """Create a new Bin.

        Args:
            session: The database session (or fake equivalent).
            name: Optional human-readable name for the bin.

        Returns:
            The created Bin.
        """
        ...

    async def get_by_id(self, session: Any, bin_id: str) -> Bin | None:
        """Retrieve a Bin by its ID.

        Args:
            session: The database session (or fake equivalent).
            bin_id: The unique identifier of the bin.

        Returns:
            The Bin if found, None otherwise.
        """
        ...

    async def list_all(self, session: Any) -> list[Bin]:
        """Retrieve all Bins.

        Args:
            session: The database session (or fake equivalent).

        Returns:
            List of all Bins.
        """
        ...
