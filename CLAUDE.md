# CLAUDE.md

## Quick Reference

- `just install` - Install dependencies
- `just dev` - Run development server
- `just db-up` - Start PostgreSQL database
- `just ci` - Run all CI checks
- `just test` - Run tests
- `just fix` - Auto-fix linting issues

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
- `web/` - Static assets and templates for web UI
- `config.py` - Application settings (via pydantic-settings)

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
- Single `ADMIN_TOKEN` environment variable

## Database

- PostgreSQL 16+ via asyncpg (async connection pool)
- Direct SQL queries (no ORM)
- Repository pattern for data access
- Database URL: `DATABASE_URL` environment variable

## Conventions

- Python 3.12+
- Async for all I/O operations
- Pydantic for all data structures
- structlog for logging (snake_case events)
- 100 char line length (project-specific, differs from template's 120)
- Absolute imports only

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
- Environment variables automatically loaded
- Type-safe configuration with validation
- See `.env.example` for available settings

## Development Workflow

1. Start database: `just db-up`
2. Install dependencies: `just install`
3. Run development server: `just dev`
4. Run tests: `just test`
5. Before committing: `just ci`

## Docker

Full stack with docker-compose:
- `just up` - Start PostgreSQL + request-nest service
- `just down` - Stop all services
- `just db-logs` - View database logs
- `just db-shell` - Connect to database

## Before Committing

Run `just ci` to verify all checks pass (linting, type checking, tests).
