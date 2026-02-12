# E2E Testing

## Infrastructure

- E2E tests use Playwright (Python) with pytest: `tests/e2e/`
- `live_server` session-scoped fixture starts the real backend and yields the base URL
- `authenticated_page` fixture sets admin token in localStorage and reloads
- `clean_authenticated_page` fixture provides a fresh authenticated page with no pre-existing state

## Test Organization

- One file per workflow: `test_auth_workflow.py`, `test_ingest_workflow.py`, etc.
- Test classes named `TestUser<DoesAction>` or `Test<WorkflowScenario>` (e.g., `TestUserSendsWebhook`, `TestAuthWithInvalidToken`)
- Markers: `@pytest.mark.ui` and `@pytest.mark.playwright` on every e2e class

## Data Setup

- Set up test data via API calls (`requests.post`), not UI interactions
- Use `admin_headers = {"Authorization": f"Bearer {settings.admin_token}"}` for authenticated API calls
- Always set `timeout=10` on API requests in tests

## Assertions

- Use Playwright `expect()` for UI assertions: `expect(locator).to_be_visible()`
- Assert on user-visible text and state, not DOM structure
- Use `page.locator("table").get_by_text(...)` for table content assertions
- Use `page.get_by_role()`, `page.get_by_label()`, `page.get_by_text()` over CSS selectors

## Coverage

- Cover both happy paths and key error paths per workflow
- Auth tests: invalid token, empty token, recovery after failure, token expiration
- Ingest tests: different HTTP methods, multiple events, event detail inspection, 404 for nonexistent bins
