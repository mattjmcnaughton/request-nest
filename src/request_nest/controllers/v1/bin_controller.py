"""Controller for Bin API endpoints."""

from sqlalchemy.ext.asyncio import AsyncSession

from request_nest.dtos.v1 import BinListResponse, BinResponse, CreateBinRequest
from request_nest.errors import not_found_error
from request_nest.services import BinService

__all__ = ["BinController"]


class BinController:
    """Controller for Bin operations.

    Handles request orchestration and error handling for bin endpoints.
    """

    def __init__(self, service: BinService) -> None:
        """Initialize the controller with a service.

        Args:
            service: The BinService for business logic.
        """
        self._service = service

    async def create_bin(
        self,
        session: AsyncSession,
        request: CreateBinRequest,
        base_url: str,
    ) -> BinResponse:
        """Create a new bin.

        Args:
            session: The database session.
            request: The create bin request DTO.
            base_url: The base URL for generating the ingest URL.

        Returns:
            The created bin as a BinResponse DTO.
        """
        return await self._service.create_bin(session, name=request.name, base_url=base_url)

    async def get_bin(
        self,
        session: AsyncSession,
        bin_id: str,
        base_url: str,
    ) -> BinResponse:
        """Get a bin by ID.

        Args:
            session: The database session.
            bin_id: The unique identifier of the bin.
            base_url: The base URL for generating the ingest URL.

        Returns:
            The bin as a BinResponse DTO.

        Raises:
            HTTPException: 404 if the bin is not found.
        """
        result = await self._service.get_bin(session, bin_id=bin_id, base_url=base_url)
        if result is None:
            raise not_found_error("Bin", bin_id)
        return result

    async def list_bins(
        self,
        session: AsyncSession,
        base_url: str,
    ) -> BinListResponse:
        """List all bins.

        Args:
            session: The database session.
            base_url: The base URL for generating ingest URLs.

        Returns:
            A BinListResponse containing all bins.
        """
        bins = await self._service.list_bins(session, base_url=base_url)
        return BinListResponse(bins=bins)
