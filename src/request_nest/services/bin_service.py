"""Service layer for Bin operations."""

from typing import Any

from request_nest.domain import Bin
from request_nest.dtos.v1 import BinResponse
from request_nest.repositories import BinRepositoryProtocol

__all__ = ["BinService"]


class BinService:
    """Service for Bin business logic.

    Handles creation, retrieval, and listing of bins.
    Converts domain models to DTOs for API responses.
    """

    def __init__(self, repository: BinRepositoryProtocol) -> None:
        """Initialize the service with a repository.

        Args:
            repository: Any implementation of BinRepositoryProtocol.
        """
        self._repository = repository

    def _to_response(self, bin_obj: Bin, base_url: str) -> BinResponse:
        """Convert a Bin domain object to a BinResponse DTO.

        Args:
            bin_obj: The Bin domain object.
            base_url: The base URL for generating ingest URLs.

        Returns:
            A BinResponse DTO.
        """
        return BinResponse(
            id=bin_obj.id,
            name=bin_obj.name,
            ingest_url=bin_obj.ingest_url(base_url),
            created_at=bin_obj.created_at,
        )

    async def create_bin(
        self,
        session: Any,
        name: str | None,
        base_url: str,
    ) -> BinResponse:
        """Create a new bin.

        Args:
            session: The database session.
            name: Optional human-readable name for the bin.
            base_url: The base URL for generating the ingest URL.

        Returns:
            The created bin as a BinResponse DTO.
        """
        bin_obj = await self._repository.create(session, name=name)
        await session.commit()
        return self._to_response(bin_obj, base_url)

    async def get_bin(
        self,
        session: Any,
        bin_id: str,
        base_url: str,
    ) -> BinResponse | None:
        """Get a bin by ID.

        Args:
            session: The database session.
            bin_id: The unique identifier of the bin.
            base_url: The base URL for generating the ingest URL.

        Returns:
            The bin as a BinResponse DTO, or None if not found.
        """
        bin_obj = await self._repository.get_by_id(session, bin_id)
        if bin_obj is None:
            return None
        return self._to_response(bin_obj, base_url)

    async def list_bins(
        self,
        session: Any,
        base_url: str,
    ) -> list[BinResponse]:
        """List all bins.

        Args:
            session: The database session.
            base_url: The base URL for generating ingest URLs.

        Returns:
            A list of bins as BinResponse DTOs.
        """
        bins = await self._repository.list_all(session)
        return [self._to_response(bin_obj, base_url) for bin_obj in bins]
