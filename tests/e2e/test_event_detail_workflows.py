"""E2E tests for event detail page user workflows.

These tests represent core user journeys through the event detail page:
- Navigating from bin detail to event detail
- Viewing full HTTP request details
- Breadcrumb navigation
"""

import re

import pytest
import requests
from playwright.sync_api import Page, expect


@pytest.mark.ui
@pytest.mark.playwright
class TestUserViewsEventDetail:
    """User can view full event details after capturing a webhook."""

    def test_navigates_to_event_detail_from_bin(
        self,
        authenticated_page: Page,
    ) -> None:
        """User clicks on an event in the bin detail to view full request details."""
        page = authenticated_page

        # Create a bin
        page.get_by_role("button", name="new bin").first.click()
        page.get_by_label("name (optional)").fill("Event Detail Bin")
        page.locator("form").get_by_role("button", name="create").click()

        # Navigate to bin detail
        expect(page.get_by_role("cell", name="Event Detail Bin")).to_be_visible()
        page.get_by_role("row", name=re.compile("Event Detail Bin")).click()

        # Wait for detail page to load and get ingest URL
        expect(page.get_by_role("heading", name="Event Detail Bin")).to_be_visible()
        ingest_url_element = page.locator("code").filter(has_text=re.compile(r"^http")).first
        ingest_url = ingest_url_element.inner_text()

        # Send a webhook with known content
        full_ingest_url = f"{ingest_url}/test-path?foo=bar"
        response = requests.post(
            full_ingest_url,
            json={"message": "hello world"},
            headers={"Content-Type": "application/json", "X-Test-Header": "test-value"},
            timeout=10,
        )
        assert response.status_code == 200

        # Refresh to see the event
        page.reload()

        # Click on the event row in the table (desktop view)
        expect(page.locator("table").get_by_text("POST")).to_be_visible()
        page.locator("table tr").filter(has_text="POST").first.click()

        # Verify we're on the event detail page
        expect(page.get_by_text("POST").first).to_be_visible()
        expect(page.locator("code").filter(has_text=re.compile(r"^e_"))).to_be_visible()

    def test_displays_request_headers(
        self,
        authenticated_page: Page,
    ) -> None:
        """User sees HTTP headers on the event detail page."""
        page = authenticated_page

        # Create a bin
        page.get_by_role("button", name="new bin").first.click()
        page.get_by_label("name (optional)").fill("Headers Bin")
        page.locator("form").get_by_role("button", name="create").click()

        # Navigate to bin detail
        expect(page.get_by_role("cell", name="Headers Bin")).to_be_visible()
        page.get_by_role("row", name=re.compile("Headers Bin")).click()
        expect(page.get_by_role("heading", name="Headers Bin")).to_be_visible()

        ingest_url_element = page.locator("code").filter(has_text=re.compile(r"^http")).first
        ingest_url = ingest_url_element.inner_text()

        # Send a webhook with a custom header
        response = requests.post(
            f"{ingest_url}/webhook",
            data="test body",
            headers={"X-Custom-Header": "custom-value"},
            timeout=10,
        )
        assert response.status_code == 200

        # Refresh and navigate to event detail
        page.reload()
        expect(page.locator("table").get_by_text("POST")).to_be_visible()
        page.locator("table tr").filter(has_text="POST").first.click()

        # Verify headers section is displayed
        expect(page.get_by_role("heading", name="headers")).to_be_visible()
        expect(page.get_by_text("x-custom-header")).to_be_visible()
        expect(page.get_by_text("custom-value")).to_be_visible()

    def test_displays_json_body_pretty_printed(
        self,
        authenticated_page: Page,
    ) -> None:
        """User sees JSON body pretty-printed on the event detail page."""
        page = authenticated_page

        # Create a bin
        page.get_by_role("button", name="new bin").first.click()
        page.get_by_label("name (optional)").fill("JSON Body Bin")
        page.locator("form").get_by_role("button", name="create").click()

        # Navigate to bin detail
        expect(page.get_by_role("cell", name="JSON Body Bin")).to_be_visible()
        page.get_by_role("row", name=re.compile("JSON Body Bin")).click()
        expect(page.get_by_role("heading", name="JSON Body Bin")).to_be_visible()

        ingest_url_element = page.locator("code").filter(has_text=re.compile(r"^http")).first
        ingest_url = ingest_url_element.inner_text()

        # Send a JSON webhook
        response = requests.post(
            f"{ingest_url}/webhook",
            json={"name": "test", "count": 42},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        assert response.status_code == 200

        # Navigate to event detail
        page.reload()
        expect(page.locator("table").get_by_text("POST")).to_be_visible()
        page.locator("table tr").filter(has_text="POST").first.click()

        # Verify JSON body is shown with JSON label
        expect(page.get_by_text("(json)")).to_be_visible()
        # Verify pretty-printed content in pre block
        pre = page.locator("pre")
        expect(pre).to_be_visible()
        expect(pre).to_contain_text('"name"')
        expect(pre).to_contain_text('"test"')

    def test_displays_query_parameters(
        self,
        authenticated_page: Page,
    ) -> None:
        """User sees query parameters on the event detail page."""
        page = authenticated_page

        # Create a bin
        page.get_by_role("button", name="new bin").first.click()
        page.get_by_label("name (optional)").fill("Query Params Bin")
        page.locator("form").get_by_role("button", name="create").click()

        # Navigate to bin detail
        expect(page.get_by_role("cell", name="Query Params Bin")).to_be_visible()
        page.get_by_role("row", name=re.compile("Query Params Bin")).click()
        expect(page.get_by_role("heading", name="Query Params Bin")).to_be_visible()

        ingest_url_element = page.locator("code").filter(has_text=re.compile(r"^http")).first
        ingest_url = ingest_url_element.inner_text()

        # Send a webhook with query params
        response = requests.get(
            f"{ingest_url}/webhook?foo=bar&baz=qux",
            timeout=10,
        )
        assert response.status_code == 200

        # Navigate to event detail
        page.reload()
        expect(page.locator("table").get_by_text("GET")).to_be_visible()
        page.locator("table tr").filter(has_text="GET").first.click()

        # Verify query parameters section
        expect(page.get_by_role("heading", name="query_params")).to_be_visible()
        expect(page.get_by_text("foo")).to_be_visible()
        expect(page.get_by_text("bar")).to_be_visible()


@pytest.mark.ui
@pytest.mark.playwright
class TestEventDetailBreadcrumbNavigation:
    """User can navigate using breadcrumbs on the event detail page."""

    def test_breadcrumb_links_back_to_bin(
        self,
        authenticated_page: Page,
    ) -> None:
        """User clicks the bin name in the breadcrumb to return to bin detail."""
        page = authenticated_page

        # Create a bin
        page.get_by_role("button", name="new bin").first.click()
        page.get_by_label("name (optional)").fill("Breadcrumb Bin")
        page.locator("form").get_by_role("button", name="create").click()

        # Navigate to bin detail
        expect(page.get_by_role("cell", name="Breadcrumb Bin")).to_be_visible()
        page.get_by_role("row", name=re.compile("Breadcrumb Bin")).click()
        expect(page.get_by_role("heading", name="Breadcrumb Bin")).to_be_visible()

        ingest_url_element = page.locator("code").filter(has_text=re.compile(r"^http")).first
        ingest_url = ingest_url_element.inner_text()

        # Send a webhook
        response = requests.post(
            f"{ingest_url}/webhook",
            json={"test": True},
            timeout=10,
        )
        assert response.status_code == 200

        # Navigate to event detail
        page.reload()
        expect(page.locator("table").get_by_text("POST")).to_be_visible()
        page.locator("table tr").filter(has_text="POST").first.click()

        # Verify breadcrumb shows bin name
        breadcrumb = page.locator("nav")
        expect(breadcrumb.get_by_role("link", name="bins")).to_be_visible()
        expect(breadcrumb.get_by_role("link", name="Breadcrumb Bin")).to_be_visible()

        # Click breadcrumb to go back to bin detail
        breadcrumb.get_by_role("link", name="Breadcrumb Bin").click()

        # Verify we're back on the bin detail page
        expect(page.get_by_role("heading", name="Breadcrumb Bin")).to_be_visible()
        expect(page.get_by_text("$ events")).to_be_visible()
