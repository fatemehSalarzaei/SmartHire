# FastAPI Routing Spec

## Router groups

- `/api/v1/auth`
- `/api/v1/jobs`
- `/api/v1/rulesets`
- `/api/v1/applications`
- `/api/v1/screening`
- `/api/v1/ranking`
- `/api/v1/ai-analysis`
- `/api/v1/notes`
- `/api/v1/admin`

## Requirements

- All protected routes require current user.
- All write routes require permission checks.
- All errors use global exception handlers.
- All responses follow `api-response-shapes.md`.
- No Kando calls directly in routers except through service dependency.
