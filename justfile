# request-nest justfile
# Run `just` to see available recipes

set dotenv-load := true

# Default recipe: show help
default:
    @just --list

# Install dependencies
install:
    uv sync --group dev

# Run the development server
dev:
    uv run uvicorn request_nest.main:app --reload --host 0.0.0.0 --port 8000

# Run the production server
serve:
    uv run uvicorn request_nest.main:app --host 0.0.0.0 --port 8000

# Run tests
test *args:
    uv run pytest {{ args }}

# Run unit tests
test-unit:
    uv run pytest tests/unit/

# Run integration tests
test-integration:
    uv run pytest tests/integration/

# Run end-to-end tests
test-e2e:
    uv run pytest tests/e2e/

# Run tests with coverage
test-cov:
    uv run pytest --cov --cov-report=term-missing --cov-report=html

# Run linting
lint:
    uv run ruff check src tests

# Run type checking
typecheck:
    uv run ty check src/

# Format code
format:
    uv run ruff format src tests

# Check formatting
format-check:
    uv run ruff format --check src tests

# Fix linting issues
fix:
    uv run ruff check --fix src tests
    uv run ruff format src tests

# Quick check (lint + typecheck, no tests)
check: lint format-check typecheck

# Run all CI checks
ci: lint format-check typecheck test

# Start PostgreSQL (via docker-compose)
db-up:
    docker compose up -d db

# Stop PostgreSQL
db-down:
    docker compose down

# View database logs
db-logs:
    docker compose logs -f db

# Connect to database
db-shell:
    docker compose exec db psql -U request_nest -d request_nest

# Build Docker image
docker-build:
    docker build -t request-nest .

# Run full stack via docker-compose
up:
    docker compose up -d

# Stop full stack
down:
    docker compose down

# Clean build artifacts
clean:
    rm -rf .pytest_cache .ruff_cache .coverage htmlcov dist
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
