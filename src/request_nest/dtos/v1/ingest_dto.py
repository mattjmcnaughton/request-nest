"""Data Transfer Objects for Ingest API endpoint."""

from pydantic import BaseModel, Field

__all__ = ["IngestResponse"]


class IngestResponse(BaseModel):
    """Response for successful webhook capture."""

    ok: bool = Field(description="Whether the request was successfully captured")
    event_id: str = Field(description="ID of the created event")
