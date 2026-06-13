# Scheduled Jobs

| Job | Schedule | Queue |
|---|---|---|
| `sync.kando_base_data` | daily | sync |
| `sync.kando_jobs` | every 6 hours | sync |
| `sync.kando_applications` | every 30 minutes | sync |
| `ai_analysis.retry_failed` | every 15 minutes | ai_analysis |
| `maintenance.cleanup_old_raw_payloads` | nightly | default |

Schedules must be configurable.


## Small-system constraint

This project serves fewer than 100 internal users. Keep the architecture monolith-first and worker-focused. Do not introduce microservices, Kubernetes, event buses, or extra infrastructure. The main capacity lever is Celery worker concurrency and database query/index optimization.
