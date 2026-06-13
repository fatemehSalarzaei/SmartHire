# Model Field Spec

## `screening_applications`

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | yes | internal key |
| `kando_application_id` | integer | yes | unique external key |
| `kando_candidate_id` | integer | yes | external key |
| `kando_cv_id` | integer | no | may be missing |
| `kando_job_id` | integer | yes | external job key |
| `candidate_full_name` | string | no | sensitive-ish |
| `source_name` | string | no | e.g. JobVision |
| `kando_hire_step_id` | integer | no | read-only Kando state |
| `kando_status_id` | integer | no | read-only Kando state |
| `internal_status` | enum | yes | SmartHire status |
| `priority_score` | integer | no | 0-100 |
| `priority_bucket` | enum | no | HIGH/MEDIUM/LOW/REVIEW_UNKNOWN |
| `rank_in_job` | integer | no | per job |
| `snapshot_hash` | string | no | prevents duplicate processing |
| `raw_snapshot_json` | JSONB | yes | canonical snapshot |
| `last_synced_at` | datetime | no | |
| `last_screened_at` | datetime | no | |
| `last_ranked_at` | datetime | no | |

## `screening_rulesets`

| Field | Type | Notes |
|---|---|---|
| `id` UUID | internal key |
| `kando_job_id` integer | job relation |
| `name` string | display |
| `version` integer | immutable decision reference |
| `status` enum | DRAFT/ACTIVE/ARCHIVED |
| `is_active` boolean | one active per job |
| `default_missing_data_policy` enum | NEEDS_REVIEW/REJECT/IGNORE |
| `scoring_enabled` boolean | |
| `max_score` integer | usually 100 |
| `ranking_scope` enum | JOB/JOB_AND_RUN/JOB_AND_RULESET |
| `config_hash` string | change detection |

## `ai_analysis_runs`

| Field | Type | Notes |
|---|---|---|
| `id` UUID | |
| `screening_application_id` UUID | |
| `ruleset_id` UUID nullable | |
| `ruleset_version` integer nullable | |
| `provider` string | |
| `model_name` string | |
| `prompt_version` string | |
| `input_hash` string | idempotency |
| `status` enum | PENDING/RUNNING/SUCCEEDED/FAILED/SKIPPED |
| `error_code` string nullable | |
| `error_message_fa` text nullable | required on failure |
| `retry_count` integer | |

## Required normalized Kando tables

Implement fields required by the mapping document first. Preserve full raw payload in `kando_raw_payloads` for debugging and schema drift analysis.
