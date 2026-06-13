# Rollback Plan

## Application rollback

- Roll back backend and worker images together.
- Roll back frontend image separately if API compatible.

## Database rollback

- Prefer forward-fix.
- If downgrade is safe, use Alembic downgrade.
- Do not drop audit or decision data.

## Worker rollback

- Pause Celery Beat before destructive rollback.
- Drain or revoke unsafe tasks.
- Resume after validation.
