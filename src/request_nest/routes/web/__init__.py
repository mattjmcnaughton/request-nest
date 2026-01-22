"""Web UI routes."""

from __future__ import annotations

from fastapi import APIRouter

from request_nest.routes.web.index import router as index_router

web_router = APIRouter()

web_router.include_router(index_router)
