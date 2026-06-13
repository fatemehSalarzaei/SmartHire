# Observability Spec

## Logs

Every log event should include:

- request_id
- task_id
- user_id when available
- entity_type
- entity_id
- action
- status
- error_code
- latency_ms

## Metrics

- Kando sync success/failure count.
- Kando sync latency.
- Applications processed.
- AI analysis success/failure count.
- Screening success/failure count.
- Ranking latency.
- Queue depth.
- API error count by code.

## Alerts

- Kando sync failing repeatedly.
- Celery queue backlog.
- AI provider repeated failures.
- Database connection errors.
- High internal server error rate.
