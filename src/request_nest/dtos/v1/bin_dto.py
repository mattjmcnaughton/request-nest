"""Data Transfer Objects for Bin API endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field

__all__ = ["BinListResponse", "BinResponse", "CreateBinRequest"]


class CreateBinRequest(BaseModel):
    """Request body for creating a new bin."""

    name: str | None = Field(default=None, description="Optional human-readable name for the bin")


class BinResponse(BaseModel):
    """Response body for a single bin."""

    id: str = Field(description="Unique identifier with 'b_' prefix")
    name: str | None = Field(description="Optional human-readable name")
    ingest_url: str = Field(description="URL for capturing webhooks to this bin")
    created_at: datetime = Field(description="Timestamp when the bin was created")


class BinListResponse(BaseModel):
    """Response body for listing bins."""

    bins: list[BinResponse] = Field(description="List of bins")
