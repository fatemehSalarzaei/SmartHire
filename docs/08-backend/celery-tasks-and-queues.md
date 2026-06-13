# Celery Tasks and Queues

## Queues

| Queue | Tasks |
|---|---|
| `sync` | Kando sync and snapshot build |
| `ai_analysis` | AI analysis |
| `screening` | Rule Engine |
| `ranking` | Ranking Engine |
| `default` | maintenance |

## Tasks

```text
sync.kando_base_data
sync.kando_jobs
sync.kando_applications
sync.build_application_snapshot
ai_analysis.run_for_application
ai_analysis.run_for_job_batch
ai_analysis.retry_failed
screening.run_for_application
screening.run_for_job
screening.retry_failed
ranking.calculate_for_job
ranking.calculate_for_application
ranking.recalculate_after_ruleset_change
maintenance.cleanup_old_raw_payloads
```

## Celery Beat

- BaseData sync: daily.
- Jobs sync: every 6 hours.
- Applications sync: every 30 minutes.
- AI retry failed: every 15 minutes.
- Cleanup: nightly.

## Retry

- External temporary failures: retry with backoff.
- Validation/business failures: no retry unless explicitly marked retryable.
- Every failed task stores Persian message.
