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

# Run tests (excludes performance and E2E tests)
test *args:
    uv run pytest -m "not perf" --ignore=tests/e2e/ {{ args }}

# Run performance tests
perf-test:
    uv run pytest -m perf --tb=short -v

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

# Run all CI checks (excludes E2E - run separately with `just test-e2e`)
ci: lint format-check typecheck test build-fe test-fe lint-fe

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

# Generate a new migration
db-migrate message:
    uv run alembic revision --autogenerate -m "{{ message }}"

# Apply pending migrations
db-upgrade:
    uv run alembic upgrade head

# Revert the most recent migration
db-downgrade:
    uv run alembic downgrade -1

# Build Docker image
docker-build:
    docker build -t request-nest .

# Run full stack via docker-compose
up:
    docker compose up -d

# Stop full stack
down:
    docker compose down

# Frontend directory
frontend_dir := "src/request_nest/web/frontend"

# Install frontend dependencies
install-fe:
    cd {{ frontend_dir }} && pnpm install

# Run frontend dev server (with proxy to FastAPI on port 8000)
dev-fe:
    cd {{ frontend_dir }} && pnpm run dev

# Build frontend for production
build-fe:
    cd {{ frontend_dir }} && pnpm run build

# Run frontend tests (Vitest)
test-fe:
    cd {{ frontend_dir }} && pnpm test

# Run frontend tests in watch mode
test-fe-watch:
    cd {{ frontend_dir }} && pnpm run test:watch

# Run frontend linting (ESLint)
lint-fe:
    cd {{ frontend_dir }} && pnpm run lint

# Fix frontend linting issues
fix-fe:
    cd {{ frontend_dir }} && pnpm run lint:fix && pnpm run format

# Format frontend code (Prettier)
format-fe:
    cd {{ frontend_dir }} && pnpm run format

# Check frontend formatting
format-fe-check:
    cd {{ frontend_dir }} && pnpm run format:check

# Clean build artifacts
clean:
    rm -rf .pytest_cache .ruff_cache .coverage htmlcov dist
    rm -rf {{ frontend_dir }}/dist {{ frontend_dir }}/node_modules/.vite
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
