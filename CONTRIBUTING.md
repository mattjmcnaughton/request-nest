# Contributing to request-nest

## Development Setup

1. Install prerequisites:
   - Python 3.13+
   - [uv](https://docs.astral.sh/uv/)
   - [just](https://just.systems/)
   - Docker (for PostgreSQL)

2. Clone and setup the project:
   ```bash
   git clone <repository-url>
   cd request-nest
   just install
   just db-up
   ```

3. Start the development server:
   ```bash
   just dev
   ```

## Development Workflow

### Running the Server

```bash
# Development with hot reload
just dev

# Production mode
just serve
```

### Before Committing

Always run the full CI checks:

```bash
just ci
```

### Testing

```bash
# All tests
just test

# Unit tests only (fast)
just test-unit

# Integration tests
just test-integration

# End-to-end tests
just test-e2e

# With coverage
just test-cov
```

### Database

```bash
# Start PostgreSQL
just db-up

# Stop PostgreSQL
just db-down

# Connect to database
just db-shell

# View logs
just db-logs
```

## Code Style

- **Python version**: 3.13+
- **Line length**: 120 characters
- **Formatting**: Handled by ruff
- **Type hints**: Required for all public APIs
- **Docstrings**: Google style for public functions

### Architecture

Follow the layered architecture:

1. **routes/** - HTTP routing, no business logic
2. **controllers/** - Request handling, validation, orchestration
3. **services/** - Business logic, transaction boundaries
4. **repositories/** - Data persistence
5. **domain/** - Pure business entities

### API Design

- Version routes: `/api/v1/`, `/api/v2/` (when needed)
- Use DTOs for request/response validation
- Return consistent error format: `{"detail": {"error": {"code": "...", "message": "..."}}}`

## Commit Guidelines

Use conventional commits:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `chore:` - Maintenance tasks
- `refactor:` - Code refactoring
- `test:` - Test additions/changes

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Ensure `just ci` passes
4. Submit a pull request
5. Address review feedback
