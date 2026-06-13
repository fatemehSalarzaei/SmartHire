# Celery Worker Scaling

## Queues

Use logical queues in the same worker codebase. Scale only Celery worker process count if evidence requires it:

- sync
- ai_analysis
- screening
- ranking

## AI queue

Use lower concurrency and rate limits to control cost and provider rate limits.

## Ranking queue

Can be CPU/DB heavy; monitor query time.

## Backpressure

If queue backlog grows, first tune the simple worker setup:

- reduce sync frequency
- increase Celery worker process/concurrency within the same backend codebase
- pause AI
- prioritize screening over AI if needed


## Small-system constraint

This project serves fewer than 100 internal users. Keep the architecture monolith-first and worker-focused. Do not introduce microservices, Kubernetes, event buses, or extra infrastructure. The main capacity lever is Celery worker concurrency and database query/index optimization.
