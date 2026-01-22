---
globs: ["tests/**/*.py", "fixtures/**/*.py"]
---

# Testing Guidelines

- Unit tests: no DB, mock at boundaries
- Use factories for test data generation
- Markers: @pytest.mark.slow, integration, e2e
- Descriptive test classes: class TestUserCreation
- Test business logic, skip testing framework behavior
