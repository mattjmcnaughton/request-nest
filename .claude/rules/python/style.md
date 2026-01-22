---
globs: ["*.py"]
---

# Python Style

- Python 3.13+, use modern syntax
- `X | None` not `Optional[X]`
- Absolute imports only
- No lazy/local imports inside functions or methods. All imports at module top. Exceptions only for: circular import resolution, or imports with significant startup cost (e.g., heavy ML libraries)
- `__all__` for public API exports
- 120 char line length
- Google-style docstrings for public functions
