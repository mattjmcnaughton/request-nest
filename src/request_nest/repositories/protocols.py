"""Protocol definitions for repository interfaces."""

from typing import Any, Protocol

from request_nest.domain import Bin, Event

__all__ = ["BinRepositoryProtocol", "EventRepositoryProtocol"]


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


class EventRepositoryProtocol(Protocol):
    """Protocol defining the interface for Event repository operations.

    This protocol enables type-safe dependency injection and testing with fakes.
    Both EventRepository (real) and FakeEventRepository (test) implement this interface.
    """

    async def create(
        self,
        session: Any,
        bin_id: str,
        method: str,
        path: str,
        query_params: dict,
        headers: dict,
        body_b64: str,
        remote_ip: str | None = None,
    ) -> Event:
        """Create a new Event.

        Args:
            session: The database session (or fake equivalent).
            bin_id: The ID of the parent bin.
            method: HTTP method (GET, POST, etc.).
            path: Request path after the bin URL.
            query_params: URL query parameters.
            headers: HTTP headers.
            body_b64: Base64-encoded request body.
            remote_ip: Client IP address, if available.

        Returns:
            The created Event.
        """
        ...

    async def get_by_id(self, session: Any, event_id: str) -> Event | None:
        """Retrieve an Event by its ID.

        Args:
            session: The database session (or fake equivalent).
            event_id: The unique identifier of the event.

        Returns:
            The Event if found, None otherwise.
        """
        ...

    async def list_by_bin(self, session: Any, bin_id: str, limit: int = 50) -> list[Event]:
        """Retrieve Events for a specific bin.

        Args:
            session: The database session (or fake equivalent).
            bin_id: The ID of the bin to list events for.
            limit: Maximum number of events to return.

        Returns:
            List of Events ordered by created_at descending.
        """
        ...
