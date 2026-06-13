# Docker Compose Spec

Use top-level `docker-compose.yml` for local and staging-like deployment.

Production may use managed PostgreSQL/Redis and separate deployment units.

Required services:

- backend
- frontend
- postgres
- redis
- celery_worker
- celery_beat
- nginx

Rules:

- No secrets hardcoded.
- Health checks should be added.
- Backend waits for DB readiness.
- Workers use same image as backend.


## Small-system constraint

This project serves fewer than 100 internal users. Keep the architecture monolith-first and worker-focused. Do not introduce microservices, Kubernetes, event buses, or extra infrastructure. The main capacity lever is Celery worker concurrency and database query/index optimization.
