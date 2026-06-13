# Task 10 — Internal API

## Summary

Implemented the first production-grade internal API layer for SmartHire Phase 1.

## Added areas

- Internal API router under `backend/app/api/v1/internal.py`
- Pydantic request/response helper schemas under `backend/app/schemas/`
- API tests for route registration, pagination response shape, authentication, and RBAC errors

## Implemented endpoint groups

- Jobs
- RuleSets
- Applications
- Application notes
- Recruiter decisions
- AI analysis lookup
- Automation status
- Screening runs
- Admin retry
- Kando connection test request

## Important boundaries

- No Kando write behavior was added.
- No frontend was added.
- No SQLAdmin behavior was changed.
- No database migration was added.
- List endpoints are paginated.
- Mutations require RBAC and create audit logs.
- User-facing errors remain Persian through the shared error contract.

## Notes

The API exposes internal SmartHire state only. It does not make final decisions in the API layer and does not call Kando mutation APIs.
