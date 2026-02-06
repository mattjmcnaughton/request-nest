# request-nest frontend

React SPA served by FastAPI. Vite dev server proxies `/api` and `/b` to the backend on port 8000.

## Quick Start

```bash
# Install dependencies
just install-fe

# Terminal 1 (backend)
just dev

# Terminal 2 (frontend)
just dev-fe
```

## Common Commands

```bash
just test-fe
just lint-fe
just fix-fe
just build-fe
```

## Architecture

See `src/request_nest/web/frontend/CLAUDE.md` for architecture, patterns, and testing guidance.
