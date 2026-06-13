# Backend Error Handling

## Global handlers

Implement handlers for:

- `HTTPException`
- `RequestValidationError`
- domain exceptions
- external integration exceptions
- unhandled exceptions

## Domain exception fields

```python
code: str
message_fa: str
retryable: bool
field_errors: dict[str, list[str]]
http_status: int
```

## Requirements

- Never return English-only user messages.
- Never expose stack trace.
- Never expose secrets.
- Always include `request_id`.
- Log internal details separately with masked sensitive data.
