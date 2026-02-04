# CLAUDE.md

## Quick Reference

- `just install` - Install backend dependencies
- `just dev` - Run backend development server
- `just db-up` - Start PostgreSQL database
- `just db-migrate "message"` - Generate new migration
- `just db-upgrade` - Apply pending migrations
- `just db-downgrade` - Revert most recent migration
- `just ci` - Run all CI checks (backend + frontend)
- `just test` - Run backend tests
- `just fix` - Auto-fix backend linting issues

### Frontend Commands

- `just install-fe` - Install frontend dependencies (pnpm)
- `just dev-fe` - Run Vite dev server (port 5173, proxies to backend)
- `just build-fe` - Build frontend for production
- `just test-fe` - Run frontend tests (Vitest)
- `just lint-fe` - Run frontend linting (ESLint)
- `just fix-fe` - Auto-fix frontend linting and formatting

## Project Overview

request-nest is a self-hosted webhook inbox for capturing and inspecting HTTP requests. Users create disposable HTTP endpoints ("bins") that capture inbound requests for inspection via a web UI.

## Architecture

REST API using FastAPI with layered architecture:

- `routes/` - HTTP routing and endpoint definitions
- `controllers/` - Request handlers, validation, orchestration
- `dtos/` - Data Transfer Objects (request/response schemas)
- `services/` - Business logic and workflows
- `domain/` - Core business entities and models
- `repositories/` - Data persistence layer (PostgreSQL via asyncpg)
- `observability/` - Logging with structlog
- `web/frontend/` - React SPA (Vite + TypeScript + Tailwind)
- `config.py` - Application settings (via pydantic-settings)

### Frontend

The web UI is a React single-page application served by FastAPI. See `src/request_nest/web/frontend/CLAUDE.md` for frontend-specific documentation.

## Key Concepts

### Bins
Disposable HTTP endpoints that capture incoming webhooks. Each bin has:
- Unique ID (prefixed with `b_`)
- Name for identification
- Ingest URL path: `/b/{bin_id}/{endpoint_path}`

### Events
Captured HTTP requests. Each event stores:
- HTTP method, headers, query params, body
- Unique ID (prefixed with `e_`)
- Timestamp and associated bin

### Authentication
- Admin API uses bearer token authentication
- Ingest endpoints are public (no auth required)
- Single `REQUEST_NEST_ADMIN_TOKEN` environment variable

## Database

- PostgreSQL 16+ via asyncpg (async connection pool)
- Direct SQL queries (no ORM)
- Repository pattern for data access
- Database migrations via Alembic (uses psycopg for sync operations)
- Database URL: `REQUEST_NEST_DATABASE_URL` environment variable
- Migration URL: `REQUEST_NEST_MIGRATION_DATABASE_URL` environment variable

## Conventions

- Python 3.12+
- Async for all I/O operations
- Pydantic for all data structures
- structlog for logging (snake_case events)
- 100 char line length (project-specific, differs from template's 120)
- Absolute imports only
- All environment variables MUST use `REQUEST_NEST_` prefix (e.g., `REQUEST_NEST_HOST`, `REQUEST_NEST_PORT`)

## Key Patterns

### API Endpoints

Admin API (requires auth):
- `POST /api/bins` - Create new bin
- `GET /api/bins` - List all bins
- `GET /api/bins/{bin_id}/events` - List events for a bin
- `GET /api/events/{event_id}` - Get event details

Ingest endpoints (no auth):
- `ANY /b/{bin_id}/{path:path}` - Capture request to bin

### Repository Pattern

Repositories accept db connection handles for transaction management:
```python
async def save(self, db: Connection, event: Event) -> None:
    ...
```

### Configuration

Application settings in `config.py` using pydantic-settings:
- Environment variables automatically loaded with `REQUEST_NEST_` prefix
- Type-safe configuration with validation
- See `.env.example` for available settings
- **IMPORTANT**: All new environment variables must use the `REQUEST_NEST_` prefix
- Settings class is configured with `env_prefix="REQUEST_NEST_"` to enforce this convention

## Database Migrations

Migrations are managed with Alembic for schema version control.

### Migration Commands

- `just db-migrate "description"` - Generate a new migration file
- `just db-upgrade` - Apply all pending migrations
- `just db-downgrade` - Revert the most recent migration

### Migration Workflow

1. Make changes to your SQLAlchemy models (when models are added to the project)
2. Generate migration: `just db-migrate "add users table"`
3. Review the generated file in `alembic/versions/`
4. Apply migration: `just db-upgrade`
5. Verify with: `uv run alembic current`

### Important Notes

- All migrations must be reversible (implement both upgrade and downgrade)
- This requirement is enforced per `.claude/rules/service/database.md`
- Migrations use psycopg (sync) while the application uses asyncpg (async)
- This separation keeps migration logic simple and maintainable
- CI automatically runs migrations before tests

## Development Workflow

1. Start database: `just db-up`
2. Install dependencies: `just install` and `just install-fe`
3. Apply migrations: `just db-upgrade`
4. Run backend server: `just dev`
5. Run frontend dev server (separate terminal): `just dev-fe`
6. Run tests: `just test` and `just test-fe`
7. Before committing: `just ci`

For frontend development with hot reload, run both servers. Vite (port 5173) proxies API requests to FastAPI (port 8000). For production testing, build frontend (`just build-fe`) then run only FastAPI (`just dev`).

## Docker

Full stack with docker-compose:
- `just up` - Start PostgreSQL + request-nest service
- `just down` - Stop all services
- `just db-logs` - View database logs
- `just db-shell` - Connect to database

## Before Committing

Run `just ci` to verify all checks pass (backend linting, type checking, tests + frontend build, tests, linting).
