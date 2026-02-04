"""Web UI routes for serving the React SPA."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

# Path to the frontend build directory
FRONTEND_DIR = Path(__file__).parent.parent.parent / "web" / "frontend" / "dist"


@router.get("/")
async def index() -> FileResponse:
    """Serve the React SPA index page."""
    return FileResponse(FRONTEND_DIR / "index.html")


@router.get("/{path:path}")
async def spa_fallback(path: str) -> FileResponse:
    """SPA fallback - serve index.html for client-side routing.

    This route handles all paths that don't match API or static asset routes,
    allowing React Router to handle client-side navigation.
    """
    # Check if the path corresponds to a static file in the dist directory
    static_file = FRONTEND_DIR / path
    if static_file.is_file():
        return FileResponse(static_file)

    # Otherwise, serve index.html for client-side routing
    return FileResponse(FRONTEND_DIR / "index.html")
