# Data Flow

## Primary automatic flow

1. `sync_kando_base_data`
2. `sync_kando_jobs`
3. `sync_kando_applications`
4. `build_application_snapshot`
5. `run_ai_analysis_if_enabled`
6. `run_rule_engine`
7. `run_ranking_engine`
8. `generate_internal_note`
9. `update_recruiter_queues`

## Data lineage

Every `screening_decision` must be traceable to:

- `kando_application_id`
- `kando_cv_id`
- `snapshot_hash`
- `ruleset_id`
- `ruleset_version`
- `ai_analysis_run_id` if used
- `screening_run_id`
- `created_at`

## No direct frontend-to-Kando flow

Frontend must never call Kando directly.
