# Audit Log Contract

Every important action must produce an immutable audit log.

## Schema

```json
{
  "id": "uuid",
  "actor_user_id": "uuid-or-null",
  "actor_type": "USER|SYSTEM|WORKER",
  "action": "RULESET_ACTIVATED",
  "entity_type": "ScreeningRuleSet",
  "entity_id": "uuid",
  "before_json": {},
  "after_json": {},
  "ip_address": "x.x.x.x",
  "user_agent": "...",
  "request_id": "req_...",
  "created_at": "2026-06-10T00:00:00Z"
}
```

## Must audit

- Login/logout.
- RuleSet create/update/activate/archive.
- Admin reprocess/retry.
- Kando settings changes.
- SQLAdmin sensitive changes.
- Recruiter notes.
- Recruiter decisions.
- Screening/ranking run completion.
- AI analysis run failure.
- Sensitive data view/export.
