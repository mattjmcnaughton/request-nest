"""Service layer for Event operations."""

import base64
from typing import Any

from request_nest.domain import Event
from request_nest.dtos.v1 import EventDetail, EventSummary
from request_nest.repositories import BinRepositoryProtocol, EventRepositoryProtocol

__all__ = ["EventService", "PayloadTooLargeError"]

# Maximum allowed limit for listing events
MAX_LIMIT = 100
DEFAULT_LIMIT = 50


class PayloadTooLargeError(Exception):
    """Raised when request body exceeds max_body_size."""

    def __init__(self, max_size: int, actual_size: int) -> None:
        self.max_size = max_size
        self.actual_size = actual_size
        super().__init__(f"Body size {actual_size} exceeds max {max_size}")


class EventService:
    """Service for Event business logic.

    Handles retrieval and listing of events.
    Converts domain models to DTOs for API responses.
    """

    def __init__(
        self,
        event_repository: EventRepositoryProtocol,
        bin_repository: BinRepositoryProtocol,
    ) -> None:
        """Initialize the service with repositories.

        Args:
            event_repository: Any implementation of EventRepositoryProtocol.
            bin_repository: Any implementation of BinRepositoryProtocol.
        """
        self._event_repository = event_repository
        self._bin_repository = bin_repository

    def _to_summary(self, event: Event) -> EventSummary:
        """Convert an Event domain object to an EventSummary DTO.

        Args:
            event: The Event domain object.

        Returns:
            An EventSummary DTO.
        """
        return EventSummary(
            id=event.id,
            method=event.method,
            path=event.path,
            size_bytes=event.size_bytes,
            created_at=event.created_at,
        )

    async def get_event(
        self,
        session: Any,
        event_id: str,
    ) -> EventDetail | None:
        """Get an event by ID with full details.

        Args:
            session: The database session.
            event_id: The unique identifier of the event.

        Returns:
            The event as an EventDetail DTO, or None if not found.
        """
        event = await self._event_repository.get_by_id(session, event_id)
        if event is None:
            return None
        return EventDetail.from_event(event)

    async def list_events_by_bin(
        self,
        session: Any,
        bin_id: str,
        limit: int = DEFAULT_LIMIT,
    ) -> list[EventSummary] | None:
        """List events for a specific bin.

        Args:
            session: The database session.
            bin_id: The ID of the bin to list events for.
            limit: Maximum number of events to return (default 50, max 100).

        Returns:
            A list of events as EventSummary DTOs, or None if the bin doesn't exist.
        """
        # Verify the bin exists
        bin_obj = await self._bin_repository.get_by_id(session, bin_id)
        if bin_obj is None:
            return None

        # Clamp limit to max
        effective_limit = min(limit, MAX_LIMIT)

        events = await self._event_repository.list_by_bin(session, bin_id, limit=effective_limit)
        return [self._to_summary(event) for event in events]

    async def ingest_request(
        self,
        session: Any,
        bin_id: str,
        method: str,
        path: str,
        query_params: dict[str, str],
        headers: dict[str, str],
        body_bytes: bytes,
        remote_ip: str | None,
        max_body_size: int,
    ) -> Event | None:
        """Ingest and store a captured HTTP request.

        Args:
            session: The database session.
            bin_id: The ID of the bin to capture to.
            method: HTTP method (GET, POST, etc.).
            path: Request path after the bin URL.
            query_params: URL query parameters.
            headers: HTTP headers.
            body_bytes: Raw request body bytes.
            remote_ip: Client IP address, if available.
            max_body_size: Maximum allowed body size in bytes.

        Returns:
            The created Event, or None if the bin doesn't exist.

        Raises:
            PayloadTooLargeError: If body_bytes exceeds max_body_size.
        """
        body_size = len(body_bytes)
        if body_size > max_body_size:
            raise PayloadTooLargeError(max_size=max_body_size, actual_size=body_size)

        bin_obj = await self._bin_repository.get_by_id(session, bin_id)
        if bin_obj is None:
            return None

        body_b64 = base64.b64encode(body_bytes).decode("ascii")

        event = await self._event_repository.create(
            session=session,
            bin_id=bin_id,
            method=method,
            path=path,
            query_params=query_params,
            headers=headers,
            body_b64=body_b64,
            remote_ip=remote_ip,
        )

        await session.commit()
        return event
