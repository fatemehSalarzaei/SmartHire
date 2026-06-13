# Task 09 — SQLAdmin Technical Admin

## Summary

Task 09 mounts SQLAdmin at `/admin` for technical administration only. It adds RBAC-aware authentication, editable/read-only model boundaries, masking helpers for secrets and sensitive JSON payloads, and audit hooks for sensitive admin mutations.

## Files Added or Changed

- `backend/app/admin/__init__.py`
- `backend/app/admin/audit.py`
- `backend/app/admin/masking.py`
- `backend/app/admin/security.py`
- `backend/app/admin/setup.py`
- `backend/app/admin/views.py`
- `backend/app/main.py`
- `backend/pyproject.toml`
- `backend/tests/test_sqladmin.py`
- `docs/codex/task-09-sqladmin.md`

## What the Module Does

### Admin Mounting

`backend/app/admin/setup.py` mounts SQLAdmin on the configured `settings.sqladmin_path`, which defaults to `/admin`. The application calls `mount_sqladmin(application)` from `create_app()` when `settings.enable_sqladmin` is enabled.

### Authentication and RBAC

`backend/app/admin/security.py` reuses the internal SmartHire user table and password verification flow. SQLAdmin access is limited to technical roles:

- `SUPER_ADMIN`
- `SYSTEM_ADMIN`
- `TECH_SUPPORT` as read-only
- `READ_ONLY_AUDITOR` as read-only/audit-oriented

Operational HR roles are denied SQLAdmin access:

- `HR_MANAGER`
- `RECRUITER`
- `REVIEWER`

### Editable Boundaries

Editable technical views are limited to technical configuration and draft rule configuration:

- Users, roles, permissions, role mappings
- Kando connection settings
- Draft RuleSet / RuleGroup / Rule / RuleTerm records

Read-only views protect operational/cache/history records:

- Kando cached entities
- Raw payloads
- Screening applications, runs, decisions and scores
- Ranking results
- AI analysis runs/results
- Notes and recruiter decisions
- Audit logs
- Integration errors
- Worker task logs

### Masking

`backend/app/admin/masking.py` masks sensitive scalar and nested JSON keys such as:

- API keys
- tokens
- authorization headers
- passwords/password hashes
- mobile/phone/email/address fields

The admin views exclude full raw payloads, raw AI output and API keys from export where applicable.

### Audit

`backend/app/admin/audit.py` records admin create/update/delete actions through the existing `AuditService`. Sensitive snapshots are masked before persistence.

## Explicit Non-Goals

Task 09 does not add:

- HR-facing admin access
- Kando write behavior
- SQLAdmin editing for Kando cache, AI results, screening decisions or ranking results
- Internal API endpoints
- Frontend changes
- New migrations
