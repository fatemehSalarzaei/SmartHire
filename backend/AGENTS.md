# backend/AGENTS.md — SmartHire Backend Rules

## Stack

Backend uses:

- Python 3.12+
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Pydantic / pydantic-settings
- Celery
- Redis
- SQLAdmin
- pytest

## Required backend documents

Before backend work, read the relevant files:

- `docs/08-backend/backend-architecture.md`
- `docs/08-backend/backend-folder-structure.md`
- `docs/08-backend/service-layer-spec.md`
- `docs/03-api/error-contract.md`
- `docs/03-api/fa-api-error-messages.md`
- `docs/04-database/database-schema.md`
- `docs/04-database/model-field-spec.md`
- `docs/04-database/migration-policy.md`
- `docs/10-security/permission-matrix.md`

## Backend rules

- Routers must not contain business logic.
- Services must be testable.
- Workers call services.
- External Kando calls must go through a read-only Kando client.
- External AI calls must go through an LLM client abstraction.
- Never log API keys, tokens, phone numbers, emails, or raw sensitive payloads.
- Never add a model change without an Alembic migration.
- Never bypass RuleSet versioning.
- Backend errors must follow the documented response contract and include `message_fa`.

## Checks

When backend changes, run the most relevant available checks:

```bash
pytest
alembic upgrade head
ruff check app tests
```

If Docker is required:

```bash
docker compose exec backend pytest
docker compose exec backend alembic upgrade head
docker compose exec backend ruff check app tests
```
