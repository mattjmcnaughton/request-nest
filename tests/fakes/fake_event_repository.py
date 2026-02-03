"""Fake EventRepository for unit testing."""

import secrets
from datetime import UTC, datetime
from typing import Any

from request_nest.domain import Event

__all__ = ["FakeEventRepository"]


class FakeEventRepository:
    """In-memory fake implementation of EventRepository.

    Stores events in a dictionary for testing without database access.
    Implements the same interface as EventRepository.
    """

    def __init__(self) -> None:
        """Initialize the fake repository with empty storage."""
        self._events: dict[str, Event] = {}

    def clear(self) -> None:
        """Clear all stored events."""
        self._events.clear()

    async def create(
        self,
        session: Any,  # noqa: ARG002
        bin_id: str,
        method: str,
        path: str,
        query_params: dict,
        headers: dict,
        body_b64: str,
        remote_ip: str | None = None,
    ) -> Event:
        """Create a new Event and store it in memory.

        Args:
            session: Ignored (for interface compatibility).
            bin_id: The ID of the parent bin.
            method: HTTP method.
            path: Request path.
            query_params: URL query parameters.
            headers: HTTP headers.
            body_b64: Base64-encoded request body.
            remote_ip: Client IP address.

        Returns:
            The created Event with generated ID and timestamp.
        """
        event_id = f"e_{secrets.token_urlsafe(12)}"
        event = Event(
            id=event_id,
            bin_id=bin_id,
            method=method,
            path=path,
            query_params=query_params,
            headers=headers,
            body_b64=body_b64,
            remote_ip=remote_ip,
            created_at=datetime.now(tz=UTC),
        )
        self._events[event_id] = event
        return event

    async def get_by_id(self, session: Any, event_id: str) -> Event | None:  # noqa: ARG002
        """Retrieve an Event by its ID.

        Args:
            session: Ignored (for interface compatibility).
            event_id: The unique identifier of the event.

        Returns:
            The Event if found, None otherwise.
        """
        return self._events.get(event_id)

    async def list_by_bin(self, session: Any, bin_id: str, limit: int = 50) -> list[Event]:  # noqa: ARG002
        """Retrieve Events for a specific bin, ordered by creation date.

        Args:
            session: Ignored (for interface compatibility).
            bin_id: The ID of the bin to list events for.
            limit: Maximum number of events to return.

        Returns:
            List of Events ordered by created_at descending (newest first).
        """
        events = [e for e in self._events.values() if e.bin_id == bin_id]
        events.sort(key=lambda e: e.created_at, reverse=True)
        return events[:limit]

    def add_event(self, event: Event) -> None:
        """Directly add an event for testing purposes.

        Args:
            event: The Event to add.
        """
        self._events[event.id] = event
