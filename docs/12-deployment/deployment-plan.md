# Deployment Plan

## Environments

- local
- staging
- production

## Components

- backend
- frontend
- postgres
- redis
- celery_worker
- celery_beat
- nginx

## Production requirements

- HTTPS.
- Secrets outside Git.
- Database backups.
- Centralized logs.
- Error monitoring.
- Migration before app rollout.
- Worker health monitoring.


## Small-system constraint

This project serves fewer than 100 internal users. Keep the architecture monolith-first and worker-focused. Do not introduce microservices, Kubernetes, event buses, or extra infrastructure. The main capacity lever is Celery worker concurrency and database query/index optimization.


## Deployment stance

Docker Compose is acceptable for Production-Ready Phase 1 if it includes secure secrets handling, HTTPS behind Nginx, backups, logs, health checks, controlled migrations, and worker supervision. Do not introduce Kubernetes unless the organization explicitly requests it and operational capacity exists.
