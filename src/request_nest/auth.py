"""Authentication dependencies for the Admin API."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from request_nest.config import settings

__all__ = ["AdminAuth", "verify_admin_token"]

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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "UNAUTHORIZED", "message": "Missing authentication token"}},
        )

    if credentials.credentials != settings.admin_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "UNAUTHORIZED", "message": "Invalid authentication token"}},
        )

    return credentials.credentials


AdminAuth = Annotated[str, Depends(verify_admin_token)]
