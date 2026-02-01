---
globs: ["tests/**/*.py", "fixtures/**/*.py"]
---

# Testing Guidelines

## Test Doubles: Prefer Fakes Over Mocks
- **Fakes over mocks**: Use in-memory fake implementations instead of unittest.mock
- Fakes are simpler implementations that behave like the real thing (e.g., FakeBinRepository stores data in a dict)
- Fakes catch more bugs because they exercise real behavior, not just call verification
- Mocks are acceptable only for external services (HTTP clients, third-party APIs)
- Place fake implementations in `tests/fakes/` directory

## Protocol Pattern for Testability
- Define Protocol classes in `repositories/protocols.py` for repository interfaces
- Services should type hint with Protocol (e.g., `BinRepositoryProtocol`) not concrete class
- Use `Any` for session parameter in Protocol methods to allow fake sessions
- Both real repository and fake implement the same Protocol interface
- This enables type-safe dependency injection without `# type: ignore` comments

Example:
```python
# repositories/protocols.py
class BinRepositoryProtocol(Protocol):
    async def create(self, session: Any, name: str | None = None) -> Bin: ...

# services/bin_service.py
class BinService:
    def __init__(self, repository: BinRepositoryProtocol) -> None: ...

# tests/fakes/fake_bin_repository.py
class FakeBinRepository:  # Implicitly implements BinRepositoryProtocol
    async def create(self, _session: Any, name: str | None = None) -> Bin: ...
```

## Test Organization
- Unit tests: no DB, use fakes at boundaries
- Use factories for test data generation
- Markers: @pytest.mark.slow, integration, e2e
- Descriptive test classes: class TestUserCreation
- Test business logic, skip testing framework behavior
