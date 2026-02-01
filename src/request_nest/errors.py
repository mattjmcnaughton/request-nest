"""Error response utilities for consistent API error formatting."""

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

__all__ = ["ErrorDetail", "ErrorResponse", "error_response", "not_found_error"]


class ErrorDetail(BaseModel):
    """Error detail with code and message."""

    code: str
    message: str


class ErrorResponse(BaseModel):
    """Wrapper for error responses following API convention."""

    error: ErrorDetail


def error_response(code: str, message: str, status_code: int) -> JSONResponse:
    """Create a JSON error response following the API convention.

    Args:
        code: Error code (e.g., "NOT_FOUND", "UNAUTHORIZED").
        message: Human-readable error message.
        status_code: HTTP status code.

    Returns:
        JSONResponse with the error envelope format.
    """
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


def not_found_error(resource: str, resource_id: str) -> HTTPException:
    """Create a 404 Not Found HTTPException.

    Args:
        resource: The type of resource (e.g., "Bin", "Event").
        resource_id: The ID that was not found.

    Returns:
        HTTPException with 404 status and error detail.
    """
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error": {"code": "NOT_FOUND", "message": f"{resource} '{resource_id}' not found"}},
    )
