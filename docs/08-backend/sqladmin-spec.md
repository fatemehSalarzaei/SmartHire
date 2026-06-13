# SQLAdmin Spec

## Purpose

SQLAdmin mounted on `/admin` is for technical administration only.

## Access

Allowed roles:

- `SUPER_ADMIN`
- `SYSTEM_ADMIN`
- `TECH_SUPPORT` read-only limited
- `READ_ONLY_AUDITOR` audit-only

HR roles must not access `/admin`.

## Views

Editable with permission:

- User
- Role
- Permission
- KandoConnection / KandoApiSetting
- SystemSetting
- Draft RuleSet/RuleGroup/Rule/RuleTerm

Read-only:

- Kando cached data
- Raw payloads
- Screening runs
- Screening decisions
- Ranking results
- AI runs/results
- Audit logs
- Integration errors

## Search/filter/sort

Every view must define useful search/filter/sort.

Examples:

- Applications: search candidate name/external id, filter job/status/source, sort synced/screened dates.
- AI runs: filter status/provider/model/error, sort created date.
- Decisions: filter decision/ruleset/version/job, sort created date.
- Errors: filter source/error_code/retryable/date.

## Security

- API keys masked.
- Sensitive candidate contact fields masked unless permission allows.
- Audit every sensitive view/export.
