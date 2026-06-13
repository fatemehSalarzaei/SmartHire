# Security and Privacy

## Required controls

- JWT authentication.
- RBAC on every protected endpoint.
- SQLAdmin restricted to technical roles.
- API key encryption or secret reference.
- Mask API keys in UI/logs.
- Mask candidate contact data unless permitted.
- Audit sensitive views/exports.
- HTTPS in staging/production.
- Secure headers through proxy.
- No secrets in Git.
- No raw payload exposure to HR.

## Sensitive data

- Candidate name
- Candidate phone
- Candidate email
- Birth date
- Resume data
- Raw Kando payload
- AI prompt/output
- Kando API key
