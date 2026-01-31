"""Event domain model for captured HTTP requests."""

import base64
from datetime import datetime
from typing import Any

from sqlalchemy import Column, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

__all__ = ["Event"]


class Event(SQLModel, table=True):
    """A captured HTTP request stored in a bin.

    Events represent incoming webhook requests that have been captured
    by a bin. Each event stores the full HTTP request data including
    method, path, headers, query parameters, and body.

    The body is stored as base64 to handle binary data safely.

    Attributes:
        id: Unique identifier with 'e_' prefix.
        bin_id: Foreign key reference to the parent bin.
        method: HTTP method (GET, POST, PUT, etc.).
        path: Request path after the bin URL.
        query_params: URL query parameters as a dictionary.
        headers: HTTP headers as a dictionary.
        body_b64: Base64-encoded request body.
        remote_ip: Client IP address, if available.
        created_at: Timestamp when the event was captured.
    """

    __tablename__ = "events"

    id: str = Field(primary_key=True)
    bin_id: str
    method: str
    path: str
    query_params: dict[str, Any] = Field(default={}, sa_column=Column(JSONB, nullable=False))
    headers: dict[str, Any] = Field(default={}, sa_column=Column(JSONB, nullable=False))
    body_b64: str = Field(default="", sa_column=Column(Text, nullable=False))
    remote_ip: str | None = Field(default=None)
    created_at: datetime = Field(sa_column_kwargs={"server_default": text("now()")})

    @property
    def size_bytes(self) -> int:
        """Return the size of the decoded body in bytes.

        Returns:
            The byte length of the decoded body, or 0 if the body is empty.
        """
        if not self.body_b64:
            return 0
        return len(base64.b64decode(self.body_b64))
