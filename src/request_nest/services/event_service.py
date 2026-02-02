"""Service layer for Event operations."""

from typing import Any

from request_nest.domain import Event
from request_nest.dtos.v1 import EventDetail, EventSummary
from request_nest.repositories import BinRepositoryProtocol, EventRepositoryProtocol

__all__ = ["EventService"]

# Maximum allowed limit for listing events
MAX_LIMIT = 100
DEFAULT_LIMIT = 50


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
