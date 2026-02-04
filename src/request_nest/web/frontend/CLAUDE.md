# Frontend CLAUDE.md

## Quick Reference

- `just install-fe` - Install dependencies (pnpm)
- `just dev-fe` - Run Vite dev server (port 5173, proxies API to 8000)
- `just build-fe` - Build for production
- `just test-fe` - Run all Vitest tests
- `just test-fe-watch` - Run tests in watch mode
- `just lint-fe` - Run ESLint
- `just fix-fe` - Auto-fix linting and formatting
- `just format-fe` - Run Prettier

## Development Workflow

Run both servers for development:

1. Terminal 1: `just dev` (FastAPI on port 8000)
2. Terminal 2: `just dev-fe` (Vite on port 5173 with proxy)

The Vite dev server proxies `/api` and `/b` routes to FastAPI, enabling hot reload for frontend changes while API requests hit the real backend.

For production, run `just build-fe` then `just dev` - FastAPI serves the built React app from `/`.

## Architecture

The frontend follows the same architectural principles as the backend:

### Directory Structure

```
src/
  api/           # API client layer
    client.ts    # BinApiClient interface
    realClient.ts # Production implementation
    fakeClient.ts # Test implementation
  components/    # Presentational React components
  contexts/      # React Context for dependency injection
  pages/         # Page-level components (route handlers)
  test/          # Test utilities and setup
  types/         # TypeScript interfaces (mirrors backend DTOs)
  utils/         # Pure utility functions
```

### Key Patterns

**Interface-Based API Client**: `BinApiClient` interface defines the contract. `RealBinApiClient` implements it for production, `FakeBinApiClient` for testing.

**Dependency Injection via Context**: Components access the API client through `useApi()` hook, not direct imports. This enables testing with fake clients.

**Separation of Concerns**:
- `components/` - Presentational components (receive data via props)
- `pages/` - Orchestration components (manage state, fetch data)
- `api/` - External integrations (isolated behind interfaces)

## Token Management

Admin token stored in localStorage under `request_nest_admin_token`. Use utilities from `utils/auth.ts`:

```typescript
import { getToken, setToken, clearToken, hasToken } from './utils/auth';
```

## Testing

See `.claude/rules/frontend/testing.md` for testing patterns.

Run all tests: `just test-fe`

## Before Committing

Run `just ci` to verify all checks pass (includes frontend build, tests, and linting).
