"""Ingest routes for capturing webhooks (public, no auth)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from request_nest.config import settings
from request_nest.controllers.v1 import IngestController
from request_nest.db import get_db_session
from request_nest.dtos.v1 import IngestResponse
from request_nest.repositories import BinRepository, EventRepository
from request_nest.services import EventService

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db_session)]

# Wire up the controller with its dependencies
_bin_repository = BinRepository()
_event_repository = EventRepository()
_service = EventService(event_repository=_event_repository, bin_repository=_bin_repository)
_controller = IngestController(service=_service, settings=settings)


@router.api_route(
    "/{bin_id}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
    response_model=IngestResponse,
    summary="Capture a webhook request (root path)",
    description="Capture an incoming HTTP request to a bin at root path. Accepts any HTTP method.",
    include_in_schema=False,
)
async def ingest_request_root(
    bin_id: str,
    request: Request,
    session: DbSession,
) -> IngestResponse:
    """Capture an incoming HTTP request to a bin at root path."""
    return await _controller.ingest(
        session=session,
        bin_id=bin_id,
        path="",
        request=request,
    )


@router.api_route(
    "/{bin_id}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
    response_model=IngestResponse,
    summary="Capture a webhook request",
    description="Capture an incoming HTTP request to a bin. Accepts any HTTP method.",
)
async def ingest_request(
    bin_id: str,
    path: str,
    request: Request,
    session: DbSession,
) -> IngestResponse:
    """Capture an incoming HTTP request to a bin."""
    return await _controller.ingest(
        session=session,
        bin_id=bin_id,
        path=path,
        request=request,
    )
