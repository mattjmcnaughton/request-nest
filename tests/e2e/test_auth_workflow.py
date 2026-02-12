"""E2E tests for authentication workflow.

These tests cover Workflow 1 (Authenticate) error and re-auth paths:
- Invalid token shows auth prompt again after first API call fails
- Re-authentication after 401 response

Note: Basic auth (token prompt on first visit, successful auth with valid token)
is already covered in test_bins_workflows.py::TestAdminTokenAuthentication.
These tests focus on the error paths not covered there.
"""

import pytest
from playwright.sync_api import Page, expect

from request_nest.config import settings


@pytest.mark.ui
@pytest.mark.playwright
class TestAuthWithInvalidToken:
    """User is re-prompted when providing an invalid token."""

    def test_invalid_token_triggers_reauth_on_api_call(
        self,
        page: Page,
        live_server: str,
    ) -> None:
        """User enters an invalid token, first API call returns 401, and auth prompt reappears."""
        # Navigate to the app
        page.goto(live_server)

        # Should see auth prompt
        expect(page.get_by_text("auth required")).to_be_visible()

        # Enter an invalid token
        page.get_by_label("token").fill("invalid-token-value")
        page.get_by_role("button", name="authenticate").click()

        # The token is saved to localStorage, the app tries to load bins,
        # gets a 401, clears the token, and re-shows the auth prompt.
        expect(page.get_by_text("auth required")).to_be_visible()

        # Verify the invalid token was cleared from localStorage
        stored_token = page.evaluate("() => localStorage.getItem('request_nest_admin_token')")
        assert stored_token is None, f"Expected token to be cleared, got: {stored_token}"

    def test_empty_token_shows_validation_error(
        self,
        page: Page,
        live_server: str,
    ) -> None:
        """User submits empty token and sees a validation error."""
        # Navigate to the app
        page.goto(live_server)

        # Should see auth prompt
        expect(page.get_by_text("auth required")).to_be_visible()

        # Submit without entering a token
        page.get_by_role("button", name="authenticate").click()

        # Should see client-side validation error
        expect(page.get_by_text("Please enter your admin token")).to_be_visible()

    def test_can_recover_with_valid_token_after_invalid_attempt(
        self,
        page: Page,
        live_server: str,
    ) -> None:
        """User enters invalid token, gets re-prompted, then enters valid token successfully."""
        # Navigate to the app
        page.goto(live_server)

        # Enter an invalid token first
        page.get_by_label("token").fill("wrong-token")
        page.get_by_role("button", name="authenticate").click()

        # Should be re-prompted after 401
        expect(page.get_by_text("auth required")).to_be_visible()

        # Now enter the valid token
        page.get_by_label("token").fill(settings.admin_token)
        page.get_by_role("button", name="authenticate").click()

        # Should now see the bins page
        expect(page.get_by_role("heading", name="$ bins")).to_be_visible()


@pytest.mark.ui
@pytest.mark.playwright
class TestReauthOnExpiredToken:
    """User is re-prompted when a previously valid token becomes invalid."""

    def test_clearing_token_from_localstorage_triggers_reauth(
        self,
        authenticated_page: Page,
    ) -> None:
        """Simulates token invalidation by clearing localStorage and reloading."""
        page = authenticated_page

        # Verify we're authenticated and see the bins page
        expect(page.get_by_role("heading", name="$ bins")).to_be_visible()

        # Clear the token from localStorage (simulates token expiration/invalidation)
        page.evaluate("() => localStorage.removeItem('request_nest_admin_token')")

        # Reload the page
        page.reload()

        # Should see auth prompt again
        expect(page.get_by_text("auth required")).to_be_visible()

    def test_corrupted_token_triggers_reauth_on_api_call(
        self,
        page: Page,
        live_server: str,
    ) -> None:
        """A corrupted token in localStorage triggers re-auth when an API call is made."""
        # Set a corrupted token directly in localStorage
        page.goto(live_server)
        page.evaluate("() => localStorage.setItem('request_nest_admin_token', 'corrupted-token')")
        page.reload()

        # The app tries to load bins with the corrupted token, gets 401,
        # clears the token, and re-shows the auth prompt.
        expect(page.get_by_text("auth required")).to_be_visible()
