# Small-System Architecture Guardrails for Claude

SmartHire is production-ready Phase 1 for fewer than 100 internal users. The system must be safe, audited, tested, and observable, but not architecturally heavy.

## Build this

- Modular monolith backend with FastAPI.
- SQLAlchemy models and Alembic migrations.
- PostgreSQL as source of truth.
- Redis + Celery for background sync, AI analysis, screening, and ranking.
- SQLAdmin mounted on `/admin` for technical administration.
- Next.js frontend for HR workflow.

## Do not build this

- Microservices.
- Kubernetes.
- Kafka/event bus.
- RabbitMQ as default.
- Separate AI service.
- Separate ranking/screening service.
- GraphQL.
- CQRS/event sourcing.
- Plugin architecture.
- Multi-tenant platform.

## Review standard

A solution is acceptable only if it is simple, testable, production-safe, and directly traceable to current requirements.
