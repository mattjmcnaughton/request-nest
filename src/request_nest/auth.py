"""Authentication dependencies for the Admin API."""

from typing import Annotated

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from opentelemetry import metrics

from request_nest.config import settings

__all__ = ["AdminAuth", "verify_admin_token"]

logger = structlog.get_logger()

meter = metrics.get_meter(__name__)
auth_failures_counter = meter.create_counter(
    "request_nest.auth.failures",
    description="Number of failed authentication attempts",
)

_security = HTTPBearer(auto_error=False)
_security_dependency = Depends(_security)


async def verify_admin_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, _security_dependency] = None,
) -> str:
    """Verify the bearer token matches the configured admin token.

    Args:
        credentials: The HTTP authorization credentials from the request.

    Returns:
        The validated token string.

    Raises:
        HTTPException: 401 if token is missing or invalid.
    """
    if credentials is None:
        logger.warning("auth_failure", reason="missing_token")
        auth_failures_counter.add(1, {"reason": "missing_token"})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "UNAUTHORIZED", "message": "Missing authentication token"}},
        )

    if credentials.credentials != settings.admin_token:
        logger.warning("auth_failure", reason="invalid_token")
        auth_failures_counter.add(1, {"reason": "invalid_token"})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "UNAUTHORIZED", "message": "Invalid authentication token"}},
        )

    return credentials.credentials


AdminAuth = Annotated[str, Depends(verify_admin_token)]
