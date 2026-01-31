"""Repository for Event persistence operations."""

import secrets

from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from request_nest.domain import Event

__all__ = ["EventRepository"]


class EventRepository:
    """Repository for Event CRUD operations.

    All methods accept an AsyncSession for external transaction control.
    The caller is responsible for committing or rolling back transactions.
    """

    async def create(
        self,
        session: AsyncSession,
        bin_id: str,
        method: str,
        path: str,
        query_params: dict,
        headers: dict,
        body_b64: str,
        remote_ip: str | None = None,
    ) -> Event:
        """Create a new Event and persist it to the database.

        Args:
            session: The async database session.
            bin_id: The ID of the parent bin.
            method: HTTP method (GET, POST, etc.).
            path: Request path after the bin URL.
            query_params: URL query parameters.
            headers: HTTP headers.
            body_b64: Base64-encoded request body.
            remote_ip: Client IP address, if available.

        Returns:
            The created Event with generated ID and server-set created_at.
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
        )

        session.add(event)
        await session.flush()
        await session.refresh(event)

        return event

    async def get_by_id(self, session: AsyncSession, event_id: str) -> Event | None:
        """Retrieve an Event by its ID.

        Args:
            session: The async database session.
            event_id: The unique identifier of the event.

        Returns:
            The Event if found, None otherwise.
        """
        result = await session.execute(select(Event).where(Event.id == event_id))
        return result.scalars().first()

    async def list_by_bin(self, session: AsyncSession, bin_id: str, limit: int = 50) -> list[Event]:
        """Retrieve Events for a specific bin, ordered by creation date.

        Args:
            session: The async database session.
            bin_id: The ID of the bin to list events for.
            limit: Maximum number of events to return (default 50).

        Returns:
            List of Events ordered by created_at descending (newest first).
        """
        result = await session.execute(
            select(Event)
            .where(Event.bin_id == bin_id)
            .order_by(desc(Event.created_at))  # type: ignore[arg-type]
            .limit(limit)
        )
        return list(result.scalars().all())
