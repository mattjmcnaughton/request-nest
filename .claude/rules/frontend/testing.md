# Frontend Testing

## Testing Pyramid

Tests follow a layered approach matching the backend:

**Unit Tests** (Vitest):
- Pure functions and utilities
- Tests in `src/**/*.test.ts`

**Component Tests** (Vitest + React Testing Library + FakeApiClient):
- Components tested in isolation with fake API client
- Tests in `src/**/*.test.tsx`

**Integration Tests** (Vitest + MSW):
- Real API client with MSW intercepting network requests
- Tests actual fetch code paths

**E2E Tests** (Playwright - Python):
- Real browser, real backend
- Tests in `tests/e2e/`

## FakeApiClient Pattern

Mirrors the backend's `FakeBinRepository` pattern. Use `FakeBinApiClient` for component tests:

```typescript
import { FakeBinApiClient, createFakeClientWithBins } from '../api';
import { renderWithProviders, createTestBin } from '../test/utils';

describe('BinsTable', () => {
  it('displays bins', () => {
    const bins = [createTestBin({ name: 'Test' })];
    const client = createFakeClientWithBins(bins);

    renderWithProviders(<BinsTable bins={bins} />, { apiClient: client });

    expect(screen.getByText('Test')).toBeInTheDocument();
  });
});
```

## Test Utilities

Located in `src/test/utils.tsx`:

- `renderWithProviders(ui, options)` - Render with ApiProvider (uses FakeBinApiClient by default)
- `createTestBin(overrides)` - Factory for test bin data

## When to Use Which

**FakeApiClient** (component tests):
- Testing component behavior and rendering
- Fast, no network, deterministic
- Use for most component tests

**MSW** (integration tests):
- Testing real API client implementation
- Verifying fetch/error handling code paths
- Use sparingly for API client tests

**Playwright** (E2E tests):
- Full user workflow validation
- Real browser, real backend
- Use for critical user journeys

## Assertions

Use `@testing-library/jest-dom` matchers:

```typescript
expect(element).toBeInTheDocument();
expect(element).toHaveTextContent('text');
expect(element).toBeVisible();
expect(element).toBeDisabled();
```

## User Interactions

Use `@testing-library/user-event` for realistic interactions:

```typescript
import userEvent from '@testing-library/user-event';

const user = userEvent.setup();
await user.click(button);
await user.type(input, 'text');
```

## Async Testing

Use `waitFor` and `findBy` queries for async operations:

```typescript
// Wait for element to appear
const element = await screen.findByText('Loaded');

// Wait for condition
await waitFor(() => {
  expect(mockFn).toHaveBeenCalled();
});
```

## Test Organization

- Group related tests in `describe` blocks
- Test names describe behavior: "displays bins when loaded"
- One assertion per test when possible
- Clean up state between tests (FakeBinApiClient has `clear()` method)
