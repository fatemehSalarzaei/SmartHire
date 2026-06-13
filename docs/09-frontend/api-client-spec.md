# API Client Spec

## Requirements

- Central API client.
- Attach auth token.
- Parse standard response shape.
- On error, display `error.message_fa`.
- Handle 401 with logout/refresh flow.
- Handle 403 with permission UI.
- Never call Kando directly.
- Use TanStack Query keys from `lib/query-keys.ts`.

## Error mapping

Use backend Persian message. If missing, fallback:

```text
خطای نامشخص رخ داد. لطفاً دوباره تلاش کنید.
```

## Tables

All tables send:

- `page`
- `page_size`
- filters
- `sort`
- `q`

Do not client-side filter full datasets.
