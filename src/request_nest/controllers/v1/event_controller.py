"""Controller for Event API endpoints."""

import structlog
from opentelemetry import metrics
from sqlalchemy.ext.asyncio import AsyncSession

from request_nest.dtos.v1 import EventDetail, EventListResponse
from request_nest.errors import not_found_error
from request_nest.services import EventService

__all__ = ["EventController"]

logger = structlog.get_logger()

meter = metrics.get_meter(__name__)
events_viewed_counter = meter.create_counter(
    "request_nest.events.viewed",
    description="Number of event detail views",
)
bin_events_listed_counter = meter.create_counter(
    "request_nest.bins.events_listed",
    description="Number of bin event list views",
)


class EventController:
    """Controller for Event operations.

    Handles request orchestration and error handling for event endpoints.
    """

    def __init__(self, service: EventService) -> None:
        """Initialize the controller with a service.

        Args:
            service: The EventService for business logic.
        """
        self._service = service

    async def get_event(
        self,
        session: AsyncSession,
        event_id: str,
    ) -> EventDetail:
        """Get an event by ID with full details.

        Args:
            session: The database session.
            event_id: The unique identifier of the event.

        Returns:
            The event as an EventDetail DTO.

        Raises:
            HTTPException: 404 if the event is not found.
        """
        result = await self._service.get_event(session, event_id=event_id)
        if result is None:
            raise not_found_error("Event", event_id)
        logger.info("event_retrieved", event_id=event_id, bin_id=result.bin_id)
        events_viewed_counter.add(1)
        return result

    async def list_events_by_bin(
        self,
        session: AsyncSession,
        bin_id: str,
        limit: int = 50,
    ) -> EventListResponse:
        """List events for a specific bin.

        Args:
            session: The database session.
            bin_id: The ID of the bin to list events for.
            limit: Maximum number of events to return.

        Returns:
            An EventListResponse containing event summaries.

        Raises:
            HTTPException: 404 if the bin is not found.
        """
        result = await self._service.list_events_by_bin(session, bin_id=bin_id, limit=limit)
        if result is None:
            raise not_found_error("Bin", bin_id)
        logger.info("bin_events_listed", bin_id=bin_id, count=len(result))
        bin_events_listed_counter.add(1)
        return EventListResponse(events=result)
