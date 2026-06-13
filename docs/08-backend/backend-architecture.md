# Backend Architecture

## Stack

- Python 3.12+
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- Celery
- Redis
- SQLAdmin

## Layering

```text
api routers -> service layer -> repositories/db/session -> models
workers -> services -> repositories/db/session -> models
admin -> SQLAdmin views -> models
```

## Rules

- Routers must not hold business logic.
- Services are unit-testable.
- Workers call services.
- SQLAdmin must not bypass invariants for active RuleSet versioning or read-only Kando cache.
- External API calls only through `KandoClient` or `LLMClient`.
