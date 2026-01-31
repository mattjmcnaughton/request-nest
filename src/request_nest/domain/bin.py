"""Bin domain model for webhook capture endpoints."""

from datetime import datetime

from sqlalchemy import text
from sqlmodel import Field, SQLModel

__all__ = ["Bin"]


class Bin(SQLModel, table=True):
    """A disposable HTTP endpoint that captures incoming webhooks.

    Bins are the core entity in request-nest. Each bin has a unique ID
    (prefixed with 'b_') and provides an ingest URL where webhooks can
    be sent for capture and inspection.

    Attributes:
        id: Unique identifier with 'b_' prefix.
        name: Optional human-readable name for the bin.
        created_at: Timestamp when the bin was created.
    """

    __tablename__ = "bins"

    id: str = Field(primary_key=True)
    name: str | None = Field(default=None)
    created_at: datetime = Field(sa_column_kwargs={"server_default": text("now()")})

    def ingest_url(self, base_url: str) -> str:
        """Generate the public URL for capturing webhooks to this bin.

        Args:
            base_url: The base URL of the application (e.g., 'https://example.com').

        Returns:
            The full ingest URL for this bin (e.g., 'https://example.com/b/b_abc123').
        """
        # Strip trailing slash from base_url to avoid double slashes
        base = base_url.rstrip("/")
        return f"{base}/b/{self.id}"
