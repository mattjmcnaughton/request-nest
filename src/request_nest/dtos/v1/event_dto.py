"""Data Transfer Objects for Event API endpoints."""

from __future__ import annotations

import base64
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from request_nest.domain import Event

__all__ = ["EventDetail", "EventListResponse", "EventSummary"]


class EventSummary(BaseModel):
    """Summary response for an event (used in list views)."""

    id: str = Field(description="Unique identifier with 'e_' prefix")
    method: str = Field(description="HTTP method (GET, POST, etc.)")
    path: str = Field(description="Request path")
    size_bytes: int = Field(description="Size of the request body in bytes")
    created_at: datetime = Field(description="Timestamp when the event was captured")


class EventDetail(BaseModel):
    """Detailed response for a single event."""

    id: str = Field(description="Unique identifier with 'e_' prefix")
    bin_id: str = Field(description="ID of the bin this event belongs to")
    method: str = Field(description="HTTP method (GET, POST, etc.)")
    path: str = Field(description="Request path")
    query_params: dict[str, str] = Field(description="URL query parameters")
    headers: dict[str, str] = Field(description="HTTP headers")
    body: str = Field(description="Decoded request body")
    remote_ip: str | None = Field(description="Client IP address, if available")
    size_bytes: int = Field(description="Size of the request body in bytes")
    created_at: datetime = Field(description="Timestamp when the event was captured")

    @classmethod
    def from_event(cls, event: Event) -> EventDetail:
        """Create an EventDetail from an Event domain object.

        Args:
            event: The Event domain object.

        Returns:
            An EventDetail DTO with decoded body.
        """
        # Decode the base64 body
        if event.body_b64:
            try:
                body = base64.b64decode(event.body_b64).decode("utf-8")
            except UnicodeDecodeError:
                # If body is binary, return base64 encoded
                body = event.body_b64
        else:
            body = ""

        return cls(
            id=event.id,
            bin_id=event.bin_id,
            method=event.method,
            path=event.path,
            query_params=event.query_params,
            headers=event.headers,
            body=body,
            remote_ip=event.remote_ip,
            size_bytes=event.size_bytes,
            created_at=event.created_at,
        )


class EventListResponse(BaseModel):
    """Response body for listing events."""

    events: list[EventSummary] = Field(description="List of event summaries")
