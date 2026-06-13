# Error Contract

All backend API errors must use this shape:

```json
{
  "success": false,
  "error": {
    "code": "RULESET_NOT_ACTIVE",
    "message_fa": "برای این عنوان شغلی قانون فعال تعریف نشده است.",
    "field_errors": {},
    "retryable": false,
    "request_id": "req_..."
  }
}
```

## Rules

- `message_fa` is required.
- `code` is required and stable.
- `retryable` is required.
- Do not expose stack traces.
- Do not expose secrets.
- Validation errors must include field-level Persian messages when possible.
- Kando errors must be translated to Persian operator-safe messages.
- AI errors must not expose prompt content to HR users.

## HTTP status mapping

| HTTP | Use |
|---|---|
| 400 | invalid request |
| 401 | unauthenticated |
| 403 | permission denied |
| 404 | resource not found |
| 409 | business conflict |
| 422 | validation error |
| 429 | rate limited |
| 500 | unexpected server error |
| 502 | external service failed |
| 503 | service unavailable |
