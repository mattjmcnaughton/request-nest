# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files
COPY README.md pyproject.toml uv.lock* ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy application code
COPY src/ src/

# Install the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Runtime stage
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy virtual environment and application
COPY --from=base /app/.venv /app/.venv
COPY --from=base /app/src /app/src

# Set path to use venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "request_nest.main:app", "--host", "0.0.0.0", "--port", "8000"]
