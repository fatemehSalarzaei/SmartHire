# Database Schema

The database is PostgreSQL. Use SQLAlchemy models and Alembic migrations.

## Main table groups

- Identity and access: `users`, `roles`, `permissions`, `user_roles`.
- Kando integration: `kando_connections`, `kando_sync_states`, `kando_raw_payloads`, `kando_api_call_logs`.
- Kando cache: `kando_jobs`, `kando_hire_steps`, `kando_applications`, `kando_application_sources`, `kando_candidates`, `kando_cvs`, `kando_cv_work_experiences`, `kando_cv_university_degrees`, `kando_cv_language_skills`, `kando_base_data_cache`.
- Screening: `screening_rulesets`, `screening_rule_groups`, `screening_rules`, `screening_rule_terms`, `screening_runs`, `screening_run_items`, `screening_decisions`.
- AI: `ai_analysis_runs`, `ai_analysis_results`.
- Ranking: `screening_scores`, `ranking_results`.
- Notes and review: `screening_notes`, `recruiter_decisions`.
- Audit and errors: `audit_logs`, `integration_errors`, `worker_task_logs`.

## Conventions

- Primary keys: UUID except external Kando IDs.
- External IDs stored as integers when provided.
- Timestamps: timezone-aware UTC.
- JSONB for snapshots, raw payloads, reasons, score breakdowns and dynamic rule values.
- Do not store secrets in plaintext.
