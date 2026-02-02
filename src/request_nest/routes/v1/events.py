"""Event management routes for Admin API."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from request_nest.auth import AdminAuth
from request_nest.controllers.v1 import EventController
from request_nest.db import get_db_session
from request_nest.dtos.v1 import EventDetail, EventListResponse
from request_nest.repositories import BinRepository, EventRepository
from request_nest.services import EventService

# Router for /events endpoints (GET /api/v1/events/{event_id})
router = APIRouter()

# Router for bin-scoped event endpoints (GET /api/v1/bins/{bin_id}/events)
bin_events_router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db_session)]

# Wire up the controller with its dependencies
_event_repository = EventRepository()
_bin_repository = BinRepository()
_service = EventService(event_repository=_event_repository, bin_repository=_bin_repository)
_controller = EventController(service=_service)


@router.get(
    "/{event_id}",
    response_model=EventDetail,
    summary="Get event details",
    description="Retrieve full details of a specific event including decoded body.",
)
async def get_event(
    event_id: str,
    session: DbSession,
    _auth: AdminAuth,
) -> EventDetail:
    """Get a specific event by ID with full details."""
    return await _controller.get_event(
        session=session,
        event_id=event_id,
    )


@bin_events_router.get(
    "/{bin_id}/events",
    response_model=EventListResponse,
    summary="List events for a bin",
    description="Retrieve event summaries for a specific bin, ordered by creation date (newest first).",
)
async def list_events_by_bin(
    bin_id: str,
    session: DbSession,
    _auth: AdminAuth,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum number of events to return")] = 50,
) -> EventListResponse:
    """List events for a specific bin."""
    return await _controller.list_events_by_bin(
        session=session,
        bin_id=bin_id,
        limit=limit,
    )
