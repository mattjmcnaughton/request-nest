"""CLI entry point for request-nest."""

import uvicorn

from request_nest.config import settings


def main() -> None:
    """Run the request-nest server."""
    uvicorn.run(
        "request_nest.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
