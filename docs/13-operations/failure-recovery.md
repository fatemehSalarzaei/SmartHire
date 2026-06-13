# Failure Recovery

## Kando unavailable

- Mark sync failed.
- Keep existing data.
- Retry with backoff.
- Show Persian warning in admin dashboard.

## AI unavailable

- Continue structured screening.
- Mark AI run failed.
- Retry if retryable.

## Worker crash

- Tasks must be idempotent.
- Use task state and hashes to prevent duplicate decisions.

## Database unavailable

- API returns service unavailable with Persian message.
- Workers retry later.
