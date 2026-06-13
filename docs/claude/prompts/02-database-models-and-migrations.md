# Task 02 — Database Models and Migrations

## Goal

Implement SQLAlchemy models and Alembic migrations for core production Phase 1 tables.

## Required reading

- `CLAUDE.md`
- `docs/claude/do-not-violate.md`
- `docs/00-product/decision-invariants.md`
- `docs/04-database/database-schema.md`
- `docs/04-database/model-field-spec.md`
- `docs/04-database/indexes-and-constraints.md`

## Allowed files/directories

- `backend/app/models/`
- `backend/alembic/`
- `backend/app/db/`

## Forbidden changes

- Do not create schema without migration.
- Do not make audit logs editable.
- Do not store secrets plaintext.

## Implementation tasks

1. Create models.
2. Add relationships.
3. Add constraints/indexes.
4. Generate Alembic migration.
5. Add seed roles/permissions.

## Required tests/checks

- alembic upgrade head
- pytest model import tests

## Acceptance criteria

- Migration applies cleanly.
- Models import.
- Core constraints exist.

## Completion report

Use the format required by `CLAUDE.md`.


## Simplicity guardrail for this task

Implement the smallest production-grade solution that satisfies the current task. Keep it inside the modular monolith. Do not add microservices, Kubernetes, event bus, GraphQL, generic plugin frameworks, or extra infrastructure. Optimize for fewer than 100 internal users and background resume processing.
