---
globs: ["**/repositories/**/*.py", "alembic/**/*.py"]
---

# Database

- Repositories accept db/tx handle for transaction injection
- Migrations: one change per migration, always reversible
- Use alembic autogenerate, review before committing
- Index foreign keys and frequently filtered columns
