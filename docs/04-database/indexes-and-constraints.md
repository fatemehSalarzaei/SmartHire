# Indexes and Constraints

## Unique constraints

- `kando_jobs.kando_job_id`
- `kando_applications.kando_application_id`
- `kando_candidates.kando_candidate_id`
- `kando_cvs.kando_cv_id`
- One active ruleset per `kando_job_id`
- One latest screening application per `kando_application_id`

## Required indexes

- `screening_applications(kando_job_id, internal_status)`
- `screening_applications(priority_bucket, priority_score)`
- `screening_applications(snapshot_hash)`
- `screening_decisions(screening_application_id, created_at)`
- `screening_scores(screening_application_id, created_at)`
- `ai_analysis_runs(screening_application_id, status)`
- `audit_logs(actor_user_id, created_at)`
- `integration_errors(source, created_at)`
- GIN index on `raw_snapshot_json` only if needed after profiling.

## Constraints

- `priority_score` between 0 and 100.
- `confidence` between 0 and 1.
- `ruleset.version` positive integer.
- `message_fa` required for stored user-visible errors.
