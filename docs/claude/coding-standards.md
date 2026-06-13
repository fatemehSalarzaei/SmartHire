# Coding Standards

## Backend

- Python 3.12+.
- Type hints required.
- Pydantic schemas for inputs/outputs.
- Service layer for business logic.
- SQLAlchemy models explicit.
- Alembic migrations for schema changes.
- Pytest tests for services.
- No secrets in logs.

## Frontend

- TypeScript strict.
- Component boundaries clear.
- TanStack Query for API state.
- TanStack Table for server tables.
- React Hook Form + Zod for forms.
- Persian copy from `fa-copy-dictionary.md`.

## Naming

- Backend DB/model fields: snake_case.
- API fields: prefer snake_case unless a single frontend-wide camelCase decision is made.
- Enums: UPPER_SNAKE_CASE.
