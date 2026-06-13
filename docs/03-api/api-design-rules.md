# API Design Rules

## General

- Base path: `/api/v1`.
- Use JSON only.
- Use snake_case in backend DB, camelCase may be exposed only if frontend contract chooses it consistently. Preferred: snake_case for API simplicity.
- All list endpoints must be paginated.
- All filters and sorting must be server-side.
- All mutation endpoints must require permissions.
- All errors must follow `error-contract.md`.
- All user-facing errors must include Persian `message_fa`.

## Mutations

Every mutation must:

- Validate input with Pydantic.
- Check RBAC.
- Record audit log.
- Return updated resource or accepted task id.
- Never mutate Kando.

## Admin-only reprocess

Admin reprocess endpoints must:

- Require `SUPER_ADMIN` or `SYSTEM_ADMIN`.
- Create audit log.
- Return task id.
- Never be presented as primary HR action.
