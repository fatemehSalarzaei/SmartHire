# Frontend Error Handling

## Rules

- Always show Persian message.
- Prefer backend `message_fa`.
- Show retry only if `retryable=true`.
- For form validation, show field-level errors.
- For 403, show permission denial.
- For 401, redirect to login.
- For AI failure, show a non-blocking badge and detail section.
- Never expose raw stack traces or raw AI prompts to HR users.
