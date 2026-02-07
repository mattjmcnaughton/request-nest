"""E2E tests for bins index page user workflows.

These tests represent core user journeys through the bins index page:
- Viewing the list of existing bins
- Creating a new bin
- Copying an ingest URL to clipboard
"""

import re

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.ui
@pytest.mark.playwright
class TestUserViewsBinsList:
    """User can view the list of existing bins."""

    def test_displays_empty_state_when_no_bins_exist(
        self,
        clean_authenticated_page: Page,
    ) -> None:
        """User sees empty state message when no bins have been created."""
        # The page should show the empty state
        expect(clean_authenticated_page.get_by_text("No bins yet")).to_be_visible()

    def test_displays_bins_after_creation(
        self,
        clean_authenticated_page: Page,
    ) -> None:
        """User sees bins in the list after creating them."""
        page = clean_authenticated_page

        # Create a bin first
        page.get_by_role("button", name="Create Bin").first.click()
        page.get_by_label("Name (optional)").fill("Test Bin")
        page.locator("form").get_by_role("button", name="Create Bin").click()

        # Wait for modal to close and bin to appear in the table
        expect(page.get_by_role("cell", name="Test Bin")).to_be_visible()

        # Verify bin ID is shown in a table cell (format: b_...)
        expect(page.get_by_role("cell").filter(has_text=re.compile(r"^b_")).first).to_be_visible()


@pytest.mark.ui
@pytest.mark.playwright
class TestUserCreatesNewBin:
    """User can create a new bin via the UI."""

    def test_creates_bin_with_name(
        self,
        authenticated_page: Page,
    ) -> None:
        """User creates a bin with a custom name."""
        page = authenticated_page

        # Open create modal
        page.get_by_role("button", name="Create Bin").first.click()

        # Fill in the name
        page.get_by_label("Name (optional)").fill("My Webhook Bin")

        # Submit (use the form's submit button)
        page.locator("form").get_by_role("button", name="Create Bin").click()

        # Verify the bin appears in the table
        expect(page.get_by_role("cell", name="My Webhook Bin")).to_be_visible()

    def test_creates_bin_without_name(
        self,
        authenticated_page: Page,
    ) -> None:
        """User creates a bin without providing a name."""
        page = authenticated_page

        # Open create modal
        page.get_by_role("button", name="Create Bin").first.click()

        # Submit without filling name
        page.locator("form").get_by_role("button", name="Create Bin").click()

        # Verify a bin was created (should show bin ID in table cell)
        expect(page.get_by_role("cell").filter(has_text=re.compile(r"^b_")).first).to_be_visible()

    def test_can_cancel_bin_creation(
        self,
        clean_authenticated_page: Page,
    ) -> None:
        """User can cancel bin creation without creating a bin."""
        page = clean_authenticated_page

        # Wait for page to fully load (empty state with clean database)
        expect(page.get_by_text("No bins yet")).to_be_visible()

        # Open create modal
        page.get_by_role("button", name="Create Bin").first.click()

        # Verify modal is open
        expect(page.get_by_text("Create New Bin")).to_be_visible()

        # Cancel
        page.get_by_role("button", name="Cancel").click()

        # Modal should be closed
        expect(page.get_by_text("Create New Bin")).not_to_be_visible()

        # Empty state should still be shown (no new bin created)
        expect(page.get_by_text("No bins yet")).to_be_visible()


@pytest.mark.ui
@pytest.mark.playwright
class TestUserCopiesIngestUrl:
    """User can copy ingest URLs to clipboard."""

    def test_copies_ingest_url_to_clipboard(
        self,
        authenticated_page: Page,
    ) -> None:
        """User clicks copy button and ingest URL is copied to clipboard."""
        page = authenticated_page

        # First create a bin with a unique name
        page.get_by_role("button", name="Create Bin").first.click()
        page.get_by_label("Name (optional)").fill("Copy Test Bin")
        page.locator("form").get_by_role("button", name="Create Bin").click()

        # Wait for bin to appear in the table
        expect(page.get_by_role("cell", name="Copy Test Bin")).to_be_visible()

        # Grant clipboard permissions and click copy
        page.context.grant_permissions(["clipboard-read", "clipboard-write"])

        # Find and click the copy button in the row containing our bin
        bin_row = page.get_by_role("row", name=re.compile("Copy Test Bin"))
        copy_button = bin_row.get_by_title("Copy to clipboard")
        copy_button.click()

        # Verify clipboard contains an ingest URL in the correct format
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

        # First create a bin with a unique name
        page.get_by_role("button", name="Create Bin").first.click()
        page.get_by_label("Name (optional)").fill("Feedback Test Bin")
        page.locator("form").get_by_role("button", name="Create Bin").click()

        # Wait for bin to appear in the table
        expect(page.get_by_role("cell", name="Feedback Test Bin")).to_be_visible()

        # Grant clipboard permissions
        page.context.grant_permissions(["clipboard-read", "clipboard-write"])

        # Click copy button in the row containing our bin
        bin_row = page.get_by_role("row", name=re.compile("Feedback Test Bin"))
        bin_row.get_by_title("Copy to clipboard").click()

        # Should show "Copied!" feedback
        expect(page.get_by_text("Copied!")).to_be_visible()


@pytest.mark.ui
@pytest.mark.playwright
class TestAdminTokenAuthentication:
    """User must provide admin token to access the app."""

    def test_prompts_for_token_on_first_visit(
        self,
        page: Page,
        live_server: str,
    ) -> None:
        """User is prompted for admin token when localStorage is empty."""
        # Navigate without setting token
        page.goto(live_server)

        # Should see auth prompt
        expect(page.get_by_text("Authentication Required")).to_be_visible()
        expect(page.get_by_label("Admin Token")).to_be_visible()

    def test_can_authenticate_with_valid_token(
        self,
        page: Page,
        live_server: str,
    ) -> None:
        """User can enter valid token and access the app."""
        from request_nest.config import settings

        # Navigate without token
        page.goto(live_server)

        # Enter valid token
        page.get_by_label("Admin Token").fill(settings.admin_token)
        page.get_by_role("button", name="Authenticate").click()

        # Should now see the main page header
        expect(page.get_by_role("heading", name="request-nest")).to_be_visible()
