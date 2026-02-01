"""Bin management routes for Admin API."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from request_nest.auth import AdminAuth
from request_nest.config import settings
from request_nest.controllers.v1 import BinController
from request_nest.db import get_db_session
from request_nest.dtos.v1 import BinListResponse, BinResponse, CreateBinRequest
from request_nest.repositories import BinRepository
from request_nest.services import BinService

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db_session)]

# Wire up the controller with its dependencies
_repository = BinRepository()
_service = BinService(repository=_repository)
_controller = BinController(service=_service)


@router.post(
    "",
    response_model=BinResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new bin",
    description="Create a new webhook capture bin. Returns the bin with its ingest URL.",
)
async def create_bin(
    request: CreateBinRequest,
    session: DbSession,
    _auth: AdminAuth,
) -> BinResponse:
    """Create a new bin for capturing webhooks."""
    return await _controller.create_bin(
        session=session,
        request=request,
        base_url=settings.base_url,
    )


@router.get(
    "",
    response_model=BinListResponse,
    summary="List all bins",
    description="Retrieve all webhook capture bins.",
)
async def list_bins(
    session: DbSession,
    _auth: AdminAuth,
) -> BinListResponse:
    """List all bins."""
    return await _controller.list_bins(
        session=session,
        base_url=settings.base_url,
    )


@router.get(
    "/{bin_id}",
    response_model=BinResponse,
    summary="Get a bin by ID",
    description="Retrieve a specific bin by its unique identifier.",
)
async def get_bin(
    bin_id: str,
    session: DbSession,
    _auth: AdminAuth,
) -> BinResponse:
    """Get a specific bin by ID."""
    return await _controller.get_bin(
        session=session,
        bin_id=bin_id,
        base_url=settings.base_url,
    )
