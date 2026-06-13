# Staging and Production Plan

## Staging

- Uses staging Kando credentials.
- Mirrors production variables.
- Runs full migrations and worker pipeline.
- Used for release validation.

## Production

- Uses production Kando credentials.
- Requires whitelist/IP confirmation.
- Requires backup configured.
- Requires rollback plan.
- Requires observability enabled.

## Release sequence

1. Deploy DB migration.
2. Deploy backend.
3. Deploy workers.
4. Deploy frontend.
5. Verify health and queue processing.
