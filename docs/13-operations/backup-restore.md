# Backup and Restore

## Backup

- Daily PostgreSQL backup.
- Retain at least 30 days unless policy differs.
- Verify backup restore periodically.

## Restore

1. Stop workers.
2. Restore database.
3. Run migration compatibility check.
4. Start backend.
5. Start workers.
6. Validate queues and latest decisions.
