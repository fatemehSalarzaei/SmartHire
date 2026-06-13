# Performance Baseline

## Targets

- Applications list API: p95 < 800ms for filtered paginated queries.
- Application detail API: p95 < 1200ms.
- Screening single application: < 5s excluding AI.
- Ranking job: acceptable batch job, must not block API.
- AI analysis: async only.

## Rules

- No unpaginated large list endpoints.
- Avoid N+1 queries.
- Add indexes for common filters.
- Use background tasks for expensive work.


## Small-system constraint

This project serves fewer than 100 internal users. Keep the architecture monolith-first and worker-focused. Do not introduce microservices, Kubernetes, event buses, or extra infrastructure. The main capacity lever is Celery worker concurrency and database query/index optimization.
