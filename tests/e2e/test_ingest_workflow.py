"""E2E tests for webhook ingestion workflow.

These tests cover Workflow 5 (Send Webhook to Bin / Ingest) as a dedicated
user journey: create a bin, send a webhook request to its ingest URL,
and verify the captured event appears in the UI.

Note: Other e2e tests (test_bin_detail_workflows, test_event_detail_workflows)
also send webhooks as part of their setup, but this file tests the ingest
workflow itself as a first-class user journey.
"""

import re

import pytest
import requests
from playwright.sync_api import Page, expect

from request_nest.config import settings


@pytest.mark.ui
@pytest.mark.playwright
class TestUserSendsWebhook:
    """User creates a bin, sends a webhook, and verifies the event is captured."""

    def test_post_webhook_appears_as_event_in_bin_detail(
        self,
        clean_authenticated_page: Page,
        live_server: str,
    ) -> None:
        """User sends a POST webhook and sees it listed in the bin's events table."""
        page = clean_authenticated_page
        admin_headers = {"Authorization": f"Bearer {settings.admin_token}"}

        # Create a bin via the API for reliable setup
        create_response = requests.post(
            f"{live_server}/api/v1/bins",
            json={"name": "Ingest Test Bin"},
            headers=admin_headers,
            timeout=10,
        )
        assert create_response.status_code == 201
        bin_data = create_response.json()
        bin_id = bin_data["id"]

        # Send a POST webhook to the bin's ingest URL
        ingest_response = requests.post(
            f"{live_server}/b/{bin_id}/webhook-path",
            json={"event": "user.created", "user_id": 123},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        assert ingest_response.status_code == 200
        assert ingest_response.json()["ok"] is True

        # Navigate to the bin detail page in the UI
        page.goto(f"{live_server}/bins/{bin_id}")

        # Verify the event appears in the events table
        expect(page.locator("table").get_by_text("POST")).to_be_visible()
        expect(page.locator("table").get_by_text("webhook-path")).to_be_visible()

    def test_get_webhook_appears_as_event(
        self,
        clean_authenticated_page: Page,
        live_server: str,
    ) -> None:
        """User sends a GET webhook and sees it listed with correct method."""
        page = clean_authenticated_page
        admin_headers = {"Authorization": f"Bearer {settings.admin_token}"}

        # Create a bin via the API
        create_response = requests.post(
            f"{live_server}/api/v1/bins",
            json={"name": "GET Webhook Bin"},
            headers=admin_headers,
            timeout=10,
        )
        assert create_response.status_code == 201
        bin_data = create_response.json()
        bin_id = bin_data["id"]

        # Send a GET webhook with query params
        ingest_response = requests.get(
            f"{live_server}/b/{bin_id}/health-check?status=ok",
            timeout=10,
        )
        assert ingest_response.status_code == 200

        # Navigate to the bin detail page
        page.goto(f"{live_server}/bins/{bin_id}")

        # Verify the GET event appears
        expect(page.locator("table").get_by_text("GET")).to_be_visible()

    def test_multiple_webhooks_appear_in_order(
        self,
        clean_authenticated_page: Page,
        live_server: str,
    ) -> None:
        """Multiple webhooks sent to the same bin all appear in the events table."""
        page = clean_authenticated_page
        admin_headers = {"Authorization": f"Bearer {settings.admin_token}"}

        # Create a bin via the API
        create_response = requests.post(
            f"{live_server}/api/v1/bins",
            json={"name": "Multi Webhook Bin"},
            headers=admin_headers,
            timeout=10,
        )
        assert create_response.status_code == 201
        bin_data = create_response.json()
        bin_id = bin_data["id"]

        # Send multiple webhooks with different methods
        requests.post(
            f"{live_server}/b/{bin_id}/first",
            json={"order": 1},
            timeout=10,
        )
        requests.put(
            f"{live_server}/b/{bin_id}/second",
            json={"order": 2},
            timeout=10,
        )
        requests.get(
            f"{live_server}/b/{bin_id}/third",
            timeout=10,
        )

        # Navigate to the bin detail page
        page.goto(f"{live_server}/bins/{bin_id}")

        # Verify all three events appear in the table
        expect(page.locator("table").get_by_text("POST")).to_be_visible()
        expect(page.locator("table").get_by_text("PUT")).to_be_visible()
        expect(page.locator("table").get_by_text("GET")).to_be_visible()

    def test_webhook_event_details_are_inspectable(
        self,
        clean_authenticated_page: Page,
        live_server: str,
    ) -> None:
        """User sends a webhook and can navigate to event detail to inspect its contents."""
        page = clean_authenticated_page
        admin_headers = {"Authorization": f"Bearer {settings.admin_token}"}

        # Create a bin via the API
        create_response = requests.post(
            f"{live_server}/api/v1/bins",
            json={"name": "Inspect Webhook Bin"},
            headers=admin_headers,
            timeout=10,
        )
        assert create_response.status_code == 201
        bin_data = create_response.json()
        bin_id = bin_data["id"]

        # Send a webhook with known content for inspection
        requests.post(
            f"{live_server}/b/{bin_id}/api/notify?source=test",
            json={"action": "deploy", "version": "1.0.0"},
            headers={
                "Content-Type": "application/json",
                "X-Webhook-Source": "ci-pipeline",
            },
            timeout=10,
        )

        # Navigate to the bin detail page
        page.goto(f"{live_server}/bins/{bin_id}")

        # Click on the event row to navigate to event detail
        expect(page.locator("table").get_by_text("POST")).to_be_visible()
        page.locator("table tr").filter(has_text="POST").first.click()

        # Verify event detail page shows the request data
        # Event ID should be visible
        expect(page.locator("code").filter(has_text=re.compile(r"^e_"))).to_be_visible()

        # Headers section should contain our custom header
        expect(page.get_by_role("heading", name="headers")).to_be_visible()
        expect(page.get_by_text("x-webhook-source")).to_be_visible()
        expect(page.get_by_text("ci-pipeline")).to_be_visible()

        # Query params section should show the source parameter
        expect(page.get_by_role("heading", name="query_params")).to_be_visible()
        expect(page.get_by_text("source", exact=True)).to_be_visible()

        # Body should show the JSON payload
        pre = page.locator("pre")
        expect(pre).to_be_visible()
        expect(pre).to_contain_text('"action"')
        expect(pre).to_contain_text('"deploy"')

    def test_webhook_to_nonexistent_bin_returns_404(
        self,
        live_server: str,
    ) -> None:
        """Sending a webhook to a nonexistent bin returns 404 (no UI interaction needed)."""
        response = requests.post(
            f"{live_server}/b/b_nonexistent_bin_id/webhook",
            json={"test": True},
            timeout=10,
        )
        assert response.status_code == 404
