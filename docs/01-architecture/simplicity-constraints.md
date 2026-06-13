# Simplicity Constraints

## Purpose

This file prevents Claude from overengineering SmartHire.

The project must be production-ready, but it serves fewer than 100 internal users. The primary load is background resume processing. Therefore, the correct design is a simple modular monolith plus background workers.

## Required architecture

```text
Next.js HR Panel
        ↓
FastAPI Backend + SQLAdmin /admin
        ↓
PostgreSQL
        ↓
Celery Workers + Redis
        ↓
Kando read-only APIs / AI provider
```

## Hard constraints

- One backend codebase.
- One frontend codebase.
- One database.
- One Redis instance.
- Celery workers may use multiple logical queues but must stay in the same backend worker codebase.
- No microservices.
- No Kubernetes.
- No Kafka/event bus.
- No RabbitMQ by default.
- No service mesh.
- No separate AI microservice.
- No separate screening/ranking microservice.
- No GraphQL.
- No custom workflow engine.
- No generic plugin architecture.
- No multi-tenant platform.

## Correct scaling strategy

Because UI users are limited, scaling should focus on:

1. Paginated and indexed list APIs.
2. Idempotent Celery tasks.
3. Controlled AI queue concurrency.
4. Retry/backoff for Kando and AI calls.
5. Snapshot hashing to avoid repeated processing.
6. PostgreSQL indexes for common filters.
7. Avoiding N+1 queries.

## What production-ready means here

Production-ready means:

- Secure authentication and RBAC.
- SQLAdmin restricted to technical roles.
- Immutable audit logs.
- Persian user-facing API errors.
- Alembic migrations.
- Fixture-based tests.
- Observability and operational logs.
- Backup and restore process.
- Safe AI fallback.
- Clear deployment and runbooks.

Production-ready does not mean enterprise-distributed architecture.

## Review rule

If Claude proposes a new infrastructure component, it must justify why PostgreSQL, Redis, Celery, or FastAPI cannot meet the requirement. Without evidence, do not add the component.
