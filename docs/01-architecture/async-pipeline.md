# Automatic Async Pipeline

## Queues

| Queue | Purpose |
|---|---|
| `sync` | Kando API sync and snapshot building |
| `ai_analysis` | AI analysis jobs |
| `screening` | Rule Engine jobs |
| `ranking` | Ranking Engine jobs |
| `default` | small internal jobs |

## Pipeline triggers

- Scheduled Kando sync.
- New/changed application snapshot.
- RuleSet activation.
- RuleSet version change.
- Scoring config change.
- Admin retry/reprocess.

## Idempotency keys

- `kando_application_id`
- `kando_cv_id`
- `kando_job_id`
- `snapshot_hash`
- `ruleset_id`
- `ruleset_version`
- `ai_input_hash`
- `scoring_config_hash`

If these are unchanged, do not reprocess unless admin explicitly forces it.

## Failure policy

- Kando temporary errors: retry with exponential backoff.
- AI temporary errors: mark AI failed and continue with structured-data screening unless RuleSet requires AI.
- Schema validation failure: fail fast with Persian error message and audit.
- Worker crash: task must be safe to retry.
