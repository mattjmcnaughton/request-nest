"""E2E tests for bin detail page user workflows.

These tests represent core user journeys through the bin detail page:
- Navigating from bins list to bin detail
- Viewing captured events
- Copying ingest URL
"""

import re

import pytest
import requests
from playwright.sync_api import Page, expect


@pytest.mark.ui
@pytest.mark.playwright
class TestUserViewsBinDetail:
    """User can view bin details and captured events."""

    def test_navigates_to_bin_detail_from_list(
        self,
        authenticated_page: Page,
    ) -> None:
        """User clicks on a bin in the list to view its details."""
        page = authenticated_page

        # Create a bin first
        page.get_by_role("button", name="Create Bin").first.click()
        page.get_by_label("Name (optional)").fill("Detail Test Bin")
        page.locator("form").get_by_role("button", name="Create Bin").click()

        # Wait for bin to appear in the table
        expect(page.get_by_role("cell", name="Detail Test Bin")).to_be_visible()

        # Click on the bin row to navigate to detail
        page.get_by_role("row", name=re.compile("Detail Test Bin")).click()

        # Verify we're on the bin detail page
        expect(page.get_by_role("heading", name="Detail Test Bin")).to_be_visible()
        # Verify ingest URL section is shown
        expect(page.get_by_text("Send a request to the ingest URL")).to_be_visible()

    def test_displays_bin_information(
        self,
        authenticated_page: Page,
    ) -> None:
        """User sees bin name, ID, and ingest URL on detail page."""
        page = authenticated_page

        # Create a bin
        page.get_by_role("button", name="Create Bin").first.click()
        page.get_by_label("Name (optional)").fill("Info Test Bin")
        page.locator("form").get_by_role("button", name="Create Bin").click()

        # Wait for bin to appear and navigate
        expect(page.get_by_role("cell", name="Info Test Bin")).to_be_visible()
        page.get_by_role("row", name=re.compile("Info Test Bin")).click()

        # Verify bin information is displayed
        expect(page.get_by_role("heading", name="Info Test Bin")).to_be_visible()
        # Verify bin ID is shown (format: b_...)
        expect(page.locator("code").filter(has_text=re.compile(r"^b_"))).to_be_visible()
        # Verify ingest URL contains the bin ID pattern
        expect(page.locator("code").filter(has_text=re.compile(r"/b/b_"))).to_be_visible()

    def test_shows_empty_state_when_no_events(
        self,
        authenticated_page: Page,
    ) -> None:
        """User sees empty state message when no events have been captured."""
        page = authenticated_page

        # Create a bin
        page.get_by_role("button", name="Create Bin").first.click()
        page.get_by_label("Name (optional)").fill("Empty Events Bin")
        page.locator("form").get_by_role("button", name="Create Bin").click()

        # Navigate to detail
        expect(page.get_by_role("cell", name="Empty Events Bin")).to_be_visible()
        page.get_by_role("row", name=re.compile("Empty Events Bin")).click()

        # Verify empty state
        expect(page.get_by_text("No events captured yet")).to_be_visible()

    def test_displays_captured_events(
        self,
        authenticated_page: Page,
    ) -> None:
        """User sees events in the table after sending webhooks."""
        page = authenticated_page

        # Create a bin
        page.get_by_role("button", name="Create Bin").first.click()
        page.get_by_label("Name (optional)").fill("Events Test Bin")
        page.locator("form").get_by_role("button", name="Create Bin").click()

        # Wait for bin and get its ingest URL
        expect(page.get_by_role("cell", name="Events Test Bin")).to_be_visible()

        # Navigate to detail to get the ingest URL
        page.get_by_role("row", name=re.compile("Events Test Bin")).click()

        # Wait for detail page to load
        expect(page.get_by_role("heading", name="Events Test Bin")).to_be_visible()

        # Get the ingest URL from the header section (it's the code element in the rounded bg-gray-50 div)
        ingest_url_element = page.locator(".rounded-md.bg-gray-50 code")
        ingest_url = ingest_url_element.inner_text()

        # Send a webhook request to the ingest URL (it already includes the full URL)
        full_ingest_url = f"{ingest_url}/webhook"
        response = requests.post(
            full_ingest_url,
            json={"message": "test webhook"},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        assert response.status_code == 200

        # Refresh the page to see the event
        page.reload()

        # Verify event appears in the table
        # Look for POST method badge in the table (desktop view is visible by default)
        expect(page.locator("table").get_by_text("POST")).to_be_visible()

    def test_back_link_returns_to_bins_list(
        self,
        authenticated_page: Page,
    ) -> None:
        """User can navigate back to bins list from detail page."""
        page = authenticated_page

        # Create a bin and navigate to detail
        page.get_by_role("button", name="Create Bin").first.click()
        page.get_by_label("Name (optional)").fill("Back Link Bin")
        page.locator("form").get_by_role("button", name="Create Bin").click()

        expect(page.get_by_role("cell", name="Back Link Bin")).to_be_visible()
        page.get_by_role("row", name=re.compile("Back Link Bin")).click()

        # Verify we're on detail page
        expect(page.get_by_role("heading", name="Back Link Bin")).to_be_visible()

        # Click back link
        page.get_by_role("link", name="Back to bins").click()

        # Verify we're back on the bins list
        expect(page.get_by_role("heading", name="request-nest")).to_be_visible()


@pytest.mark.ui
@pytest.mark.playwright
class TestUserCopiesIngestUrlFromDetail:
    """User can copy ingest URL from bin detail page."""

    def test_copies_ingest_url_to_clipboard(
        self,
        authenticated_page: Page,
    ) -> None:
        """User clicks copy button and ingest URL is copied to clipboard."""
        page = authenticated_page

        # Create a bin and navigate to detail
        page.get_by_role("button", name="Create Bin").first.click()
        page.get_by_label("Name (optional)").fill("Copy URL Bin")
        page.locator("form").get_by_role("button", name="Create Bin").click()

        expect(page.get_by_role("cell", name="Copy URL Bin")).to_be_visible()
        page.get_by_role("row", name=re.compile("Copy URL Bin")).click()

        # Wait for detail page to load
        expect(page.get_by_role("heading", name="Copy URL Bin")).to_be_visible()

        # Grant clipboard permissions
        page.context.grant_permissions(["clipboard-read", "clipboard-write"])

        # Click copy button in the header section (within the bg-gray-50 div)
        header_section = page.locator(".bg-white.rounded-lg.shadow.p-6")
        copy_button = header_section.get_by_title("Copy to clipboard")
        copy_button.click()

        # Verify clipboard contains an ingest URL (full URL with hostname)
        clipboard_content = page.evaluate("() => navigator.clipboard.readText()")
        assert re.match(r"http://[\w.:]+/b/b_[\w-]+", clipboard_content), (
            f"Expected ingest URL format, got: {clipboard_content}"
        )

    def test_shows_copied_feedback(
        self,
        authenticated_page: Page,
    ) -> None:
        """User sees 'Copied!' feedback after clicking copy button."""
        page = authenticated_page

        # Create a bin and navigate to detail
        page.get_by_role("button", name="Create Bin").first.click()
        page.get_by_label("Name (optional)").fill("Feedback Bin")
        page.locator("form").get_by_role("button", name="Create Bin").click()

        expect(page.get_by_role("cell", name="Feedback Bin")).to_be_visible()
        page.get_by_role("row", name=re.compile("Feedback Bin")).click()

        # Wait for detail page to load
        expect(page.get_by_role("heading", name="Feedback Bin")).to_be_visible()

        # Grant clipboard permissions
        page.context.grant_permissions(["clipboard-read", "clipboard-write"])

        # Click copy button in the header section
        header_section = page.locator(".bg-white.rounded-lg.shadow.p-6")
        copy_button = header_section.get_by_title("Copy to clipboard")
        copy_button.click()

        # Verify feedback
        expect(page.get_by_text("Copied!")).to_be_visible()
