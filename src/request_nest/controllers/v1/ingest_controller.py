"""Controller for Ingest API endpoint."""

import structlog
from fastapi import Request

from request_nest.config import Settings
from request_nest.dtos.v1 import IngestResponse
from request_nest.errors import not_found_error, payload_too_large_error
from request_nest.services import EventService, PayloadTooLargeError

__all__ = ["IngestController"]

logger = structlog.get_logger()


def extract_client_ip(request: Request) -> str | None:
    """Extract client IP from request.

    Checks X-Forwarded-For header first (takes first IP in comma-separated list),
    falls back to request.client.host.

    Args:
        request: The FastAPI request object.

    Returns:
        Client IP address string, or None if unavailable.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


def get_content_length(request: Request) -> int | None:
    """Get Content-Length header value if present and valid.

    Args:
        request: The FastAPI request object.

    Returns:
        Content length in bytes, or None if not present/invalid.
    """
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            return int(content_length)
        except ValueError:
            return None
    return None


class IngestController:
    """Controller for webhook ingest operations.

    Handles request orchestration and error handling for the ingest endpoint.
    """

    def __init__(self, service: EventService, settings: Settings) -> None:
        """Initialize the controller.

        Args:
            service: The EventService for business logic.
            settings: Application settings for max_body_size.
        """
        self._service = service
        self._settings = settings

    async def ingest(
        self,
        session: object,
        bin_id: str,
        path: str,
        request: Request,
    ) -> IngestResponse:
        """Ingest an HTTP request to a bin.

        Args:
            session: The database session.
            bin_id: The target bin ID.
            path: The captured path after bin_id.
            request: The FastAPI request object.

        Returns:
            IngestResponse with ok=True and event_id.

        Raises:
            HTTPException: 404 if bin not found, 413 if body too large.
        """
        # Early rejection based on Content-Length header (before reading body)
        content_length = get_content_length(request)
        if content_length is not None and content_length > self._settings.max_body_size:
            raise payload_too_large_error(self._settings.max_body_size, content_length)

        method = request.method
        query_params = dict(request.query_params)
        headers = dict(request.headers)
        body_bytes = await request.body()
        remote_ip = extract_client_ip(request)

        try:
            event = await self._service.ingest_request(
                session=session,
                bin_id=bin_id,
                method=method,
                path=path,
                query_params=query_params,
                headers=headers,
                body_bytes=body_bytes,
                remote_ip=remote_ip,
                max_body_size=self._settings.max_body_size,
            )
        except PayloadTooLargeError as e:
            raise payload_too_large_error(e.max_size, e.actual_size) from e

        if event is None:
            raise not_found_error("Bin", bin_id)

        logger.info("event_ingested", bin_id=bin_id, event_id=event.id, method=method)

        return IngestResponse(ok=True, event_id=event.id)
