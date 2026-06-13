# ADR 0004 — Screening and Ranking are Automatic

## Decision

Screening and ranking run through scheduled/event-driven Celery workers. HR users only review ready queues.

## Manual operations

Manual run endpoints are admin-only and intended for reprocess/debug/retry.

## Consequences

- Celery Beat required.
- Sync state and task logs required.
- Idempotency required.
