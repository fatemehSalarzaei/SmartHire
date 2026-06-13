# Architecture Baseline

## Approved stack

```text
FastAPI + SQLAlchemy + PostgreSQL
+
SQLAdmin mounted on /admin
+
Next.js SmartHire Panel for actual HR workflow
+
Celery + Redis for background automation
```

## Scale assumptions and architecture style

This project is a production-ready **modular monolith**, not a distributed platform.

Assumptions:

- Fewer than 100 internal users.
- Low concurrent UI traffic.
- Main load comes from scheduled Kando sync, AI analysis, screening, and ranking.
- Scaling should focus on Celery worker concurrency, queue scheduling, database indexes, pagination, and idempotent jobs.

Allowed deployment components only:

- FastAPI backend including SQLAdmin mounted on `/admin`.
- Next.js frontend.
- PostgreSQL.
- Redis.
- Celery worker(s).
- Celery Beat.
- Nginx reverse proxy.

Not allowed unless explicitly approved:

- Microservices.
- Kubernetes.
- Kafka/event bus.
- RabbitMQ as default broker.
- Service mesh.
- CQRS/event sourcing.
- Separate AI service.
- Separate screening/ranking service.
- GraphQL.

Production-ready means: secure RBAC, audit logs, tests, backups, observability, predictable migrations, Persian API errors, and operational runbooks. It does not mean distributed architecture.

## System boundaries

```text
Kando ATS API
  ↓ read-only
Kando Integration Service
  ↓ raw payload + normalized records
Snapshot Builder
  ↓ canonical application snapshot
AI Analysis Service
  ↓ assistive JSON signals
Rule Engine
  ↓ internal decision
Ranking Engine
  ↓ score/rank/bucket
Note Generator
  ↓ Persian note
SmartHire HR Panel
```

## Deployment components

- `backend`: FastAPI application and SQLAdmin mount.
- `postgres`: main database.
- `redis`: Celery broker/result backend.
- `celery_worker`: sync, AI, screening and ranking worker.
- `celery_beat`: schedules automatic jobs.
- `frontend`: Next.js HR panel.
- `nginx`: reverse proxy.

## Production-ready expectation

Every module must be independently testable and observable inside the modular monolith. No hidden business logic in frontend. Keep modules simple and explicit.
