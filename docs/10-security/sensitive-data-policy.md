# Sensitive Data Policy

## Masking examples

| Data | Masked |
|---|---|
| `09123456789` | `0912***6789` |
| `user@example.com` | `u***@example.com` |
| API key | `****last4` |

## AI data minimization

Do not send:

- phone
- email
- exact address
- API keys
- raw full payload
- system logs

## Logging

Logs must not contain:

- full resume text
- raw AI prompts
- candidate contact fields
- secrets
