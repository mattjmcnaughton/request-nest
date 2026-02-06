# request-nest

A FastAPI application scaffold with layered architecture.

## Features

- **FastAPI framework** - Modern async web framework
- **Layered architecture** - Separation of concerns (routes, controllers, services, domain, repositories)
- **Health endpoints** - Basic liveness and readiness checks
- **Structured logging** - JSON logging with structlog
- **Configuration management** - Environment-based settings with pydantic-settings

## Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [just](https://github.com/casey/just) (command runner)

### Development Setup

```bash
# Clone and enter directory
cd request-nest

# Install dependencies
just install

# Run development server
just dev
```

The app will be available at http://localhost:8000

### Environment Variables

All environment variables use the `REQUEST_NEST_` prefix.

| Variable | Default | Description |
|----------|---------|-------------|
| `REQUEST_NEST_ENVIRONMENT` | `development` | Environment: development, test, production |
| `REQUEST_NEST_DATABASE_URL` | (required) | Database URL (asyncpg) |
| `REQUEST_NEST_MIGRATION_DATABASE_URL` | (required) | Migration database URL (psycopg) |
| `REQUEST_NEST_ADMIN_TOKEN` | `dev-token-change-me` | Admin API token |
| `REQUEST_NEST_HOST` | `0.0.0.0` | Server bind address |
| `REQUEST_NEST_PORT` | `8000` | Server port |
| `REQUEST_NEST_BASE_URL` | `http://localhost:8000` | Base URL for ingest links |
| `REQUEST_NEST_LOG_LEVEL` | `INFO` | Logging level |
| `REQUEST_NEST_DEBUG` | `false` | Debug mode |
| `REQUEST_NEST_MAX_BODY_SIZE` | `1048576` | Max request body size (bytes) |

### Docker

```bash
# Build and run manually
docker build -t request-nest .
docker run -p 8000:8000 request-nest
```

## API Endpoints

### Health Check

```bash
# Liveness check
curl http://localhost:8000/api/v1/health

# Readiness check
curl http://localhost:8000/api/v1/ready
```

## Development

```bash
# Run tests
just test

# Run linting
just lint

# Run type checking
just typecheck

# Run all CI checks
just ci

# Format code
just fix
```

## License

MIT
