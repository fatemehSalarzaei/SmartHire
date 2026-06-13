# ADR 0001 — Use FastAPI, PostgreSQL, SQLAdmin and Next.js

## Decision

Use:

- FastAPI + Python for backend.
- SQLAlchemy + Alembic for database access and migrations.
- PostgreSQL as system of record.
- SQLAdmin mounted on `/admin` for technical admin.
- Next.js + TypeScript for HR workflow.
- Celery + Redis for async automation.

## Rationale

The project is integration-heavy, rule-heavy and audit-heavy. Python is suitable for rule execution, AI/NLP and data processing. Next.js is suitable for a custom HR workflow panel.

## Consequences

- SQLAdmin is not HR UI.
- Business logic remains backend-side.
- Frontend consumes stable APIs.
