# Migration Policy

- Use Alembic for every schema change.
- No direct production schema edits.
- Migration file must include safe upgrade and, when possible, downgrade.
- Add indexes separately when they may lock large tables.
- Do not drop columns without retention/migration plan.
- For enum changes, document compatibility with running workers.
- Run migrations before application deploy.
- Run migration tests in CI.
