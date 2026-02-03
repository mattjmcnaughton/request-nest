"""Unit tests for ingest controller - client IP extraction."""

from unittest.mock import MagicMock

import pytest

from request_nest.controllers.v1.ingest_controller import extract_client_ip


class TestExtractClientIp:
    """Tests for client IP extraction logic."""

    @pytest.mark.asyncio
    async def test_extracts_ip_from_x_forwarded_for_single(self) -> None:
        """Extract IP when X-Forwarded-For has single IP."""
        request = MagicMock()
        request.headers = {"x-forwarded-for": "203.0.113.50"}
        request.client = MagicMock()
        request.client.host = "10.0.0.1"

        ip = extract_client_ip(request)

        assert ip == "203.0.113.50"

    @pytest.mark.asyncio
    async def test_extracts_ip_from_x_forwarded_for_multiple(self) -> None:
        """Extract first IP when X-Forwarded-For has multiple IPs."""
        request = MagicMock()
        request.headers = {"x-forwarded-for": "203.0.113.50, 70.41.3.18, 150.172.238.178"}
        request.client = MagicMock()
        request.client.host = "10.0.0.1"

        ip = extract_client_ip(request)

        assert ip == "203.0.113.50"

    @pytest.mark.asyncio
    async def test_extracts_ip_from_x_forwarded_for_with_spaces(self) -> None:
        """Extract IP correctly when X-Forwarded-For has extra spaces."""
        request = MagicMock()
        request.headers = {"x-forwarded-for": "  203.0.113.50  ,  70.41.3.18  "}
        request.client = MagicMock()
        request.client.host = "10.0.0.1"

        ip = extract_client_ip(request)

        assert ip == "203.0.113.50"

    @pytest.mark.asyncio
    async def test_falls_back_to_client_host(self) -> None:
        """Fall back to request.client.host when no X-Forwarded-For."""
        request = MagicMock()
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "192.168.1.100"

        ip = extract_client_ip(request)

        assert ip == "192.168.1.100"

    @pytest.mark.asyncio
    async def test_returns_none_when_no_client(self) -> None:
        """Return None when no X-Forwarded-For and no client."""
        request = MagicMock()
        request.headers = {}
        request.client = None

        ip = extract_client_ip(request)

        assert ip is None

    @pytest.mark.asyncio
    async def test_empty_x_forwarded_for_falls_back(self) -> None:
        """Fall back to client.host when X-Forwarded-For is empty string."""
        request = MagicMock()
        request.headers = {"x-forwarded-for": ""}
        request.client = MagicMock()
        request.client.host = "192.168.1.100"

        ip = extract_client_ip(request)

        # Empty string is falsy, so falls back to client.host
        assert ip == "192.168.1.100"
