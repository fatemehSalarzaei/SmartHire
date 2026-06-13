# Operations Runbook

## Common checks

- Backend health endpoint.
- Celery worker status.
- Celery Beat status.
- Redis connectivity.
- PostgreSQL connectivity.
- Last Kando sync time.
- Failed task count.
- Integration error count.

## Common actions

- Retry failed sync run.
- Reprocess one application.
- Re-rank one job.
- Disable AI analysis temporarily.
- Rotate Kando API key.
