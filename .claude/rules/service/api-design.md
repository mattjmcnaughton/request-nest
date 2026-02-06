---
globs: ["**/routes/**/*.py", "**/controllers/**/*.py", "**/dtos/**/*.py"]
---

# API Design

- Version routes: /api/v1/, /api/v2/
- Use DTOs for request/response, domain models internally
- Return consistent error format: {"detail": {"error": {"code": "...", "message": "..."}}}
- Health endpoints: /health (liveness), /ready (readiness)
- Pagination: cursor-based preferred, offset for simple cases
