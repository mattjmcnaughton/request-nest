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

- Python 3.12+
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

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level |

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
