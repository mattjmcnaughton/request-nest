"""E2E test fixtures for Playwright browser tests."""

import os
import socket
import subprocess
import time
from collections.abc import Generator

import pytest
from playwright.sync_api import Page

from request_nest.config import settings
from tests.conftest import get_test_database_url


def _get_free_port() -> int:
    """Get an available port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        s.listen(1)
        return s.getsockname()[1]


def _wait_for_server(url: str, timeout: float = 10) -> bool:
    """Wait for server to be ready."""
    import urllib.error
    import urllib.request

    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(f"{url}/health", timeout=1)
            return True
        except (urllib.error.URLError, ConnectionRefusedError):
            time.sleep(0.1)
    return False


@pytest.fixture(scope="session")
def live_server(setup_test_database: None) -> Generator[str]:
    """Start a live FastAPI server for E2E tests.

    Uses subprocess for complete isolation from test process modules.
    Session-scoped to avoid startup overhead for each test.
    """
    _ = setup_test_database  # Ensure database exists

    port = _get_free_port()
    test_db_url = get_test_database_url()
    base_url = f"http://127.0.0.1:{port}"

    # Start server as subprocess with test database
    env = os.environ.copy()
    env["REQUEST_NEST_DATABASE_URL"] = test_db_url
    env["REQUEST_NEST_BASE_URL"] = base_url
    env["REQUEST_NEST_LOG_LEVEL"] = "WARNING"

    process = subprocess.Popen(
        [
            "uv",
            "run",
            "uvicorn",
            "request_nest.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for server to be ready
    if not _wait_for_server(base_url):
        process.terminate()
        raise RuntimeError("Server failed to start within timeout")

    yield base_url

    # Cleanup
    process.terminate()
    process.wait(timeout=5)


@pytest.fixture
def authenticated_page(page: Page, live_server: str) -> Page:
    """A Playwright page with admin token pre-set in localStorage.

    This fixture navigates to the live server and sets the admin token
    in localStorage before returning the page for testing.
    """
    # Navigate to the app to establish the origin for localStorage
    page.goto(live_server)

    # Set the admin token in localStorage
    page.evaluate(f"() => localStorage.setItem('request_nest_admin_token', '{settings.admin_token}')")

    # Reload to apply the token
    page.reload()

    return page
