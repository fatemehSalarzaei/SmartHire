# Kando Pagination and Retry

## Pagination

Use `pageNumber` and `pageSize` for Kando endpoints unless real API response requires a different naming.

Default:

```text
pageNumber=1
pageSize=100
```

Store sync cursor/state per endpoint:

- endpoint name
- last_successful_sync_at
- last_page_synced
- total_count if returned
- last_error_code
- last_error_message_fa

## Retry

Retry only retryable errors:

- HTTP 408
- HTTP 429
- HTTP 500/502/503/504
- connection timeout
- read timeout

Do not retry:

- HTTP 400 validation issue
- HTTP 401/403 auth/permission issue
- unexpected schema after validation fails repeatedly

## Backoff

Use exponential backoff:

```text
attempt 1: immediate
attempt 2: +30s
attempt 3: +2m
attempt 4: +10m
```

## Persian errors

All integration errors must map to `message_fa`.
