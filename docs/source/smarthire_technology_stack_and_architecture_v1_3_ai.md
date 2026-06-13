# SmartHire / Kando ATS Screening & Ranking — Technology Stack and Implementation Architecture

**Document status:** Production-Ready Phase 1 / V1 architecture baseline  
**Language:** English  
**Primary source:** SmartHire Kando Screening Project Definition v1.4 AI  
**Implementation target:** Claude-assisted implementation  
**Architecture decision:** FastAPI + SQLAlchemy + PostgreSQL + SQLAdmin + Next.js + Celery/Redis  
**Kando integration mode:** Read-only in Phase 1  
**Screening execution model:** Automatic, scheduled, and event-driven; manual execution is admin-only reprocessing  
**AI role:** AI-assisted analysis only; final decisions remain governed by auditable Rule Engine and Ranking Engine  

---

## 1. Purpose

This document defines the production-ready technology stack, implementation architecture, backend structure, frontend structure, internal admin approach, workers, deployment model, security baseline, and operational requirements for the SmartHire / Kando ATS Screening & Ranking platform.

This document replaces separate technology and internal-admin notes. All implementation decisions about backend, frontend, database, Celery, SQLAdmin, deployment, and the `/admin` path should be read from this document unless a later ADR explicitly supersedes it.

---

## 2. Final Technology Decision

The approved implementation structure is:

```text
FastAPI + SQLAlchemy + PostgreSQL
+
SQLAdmin mounted on /admin
+
Next.js SmartHire Panel for actual HR workflow
```

| Layer | Technology | Role |
|---|---|---|
| Backend API | Python 3.12+ + FastAPI | Internal APIs, Kando integration, Rule Engine, Ranking Engine, AI Analysis orchestration |
| ORM | SQLAlchemy | Database modeling and data access |
| Migration | Alembic | Database schema versioning |
| Database | PostgreSQL | Kando cache, snapshots, RuleSets, decisions, scores, notes, audit |
| Internal Admin | SQLAdmin | Technical/admin database management on `/admin` |
| HR Panel | Next.js + TypeScript | Operational recruiter and HR workflow |
| Background Jobs | Celery + Redis | Kando sync, AI analysis, screening, ranking, retries |
| Reverse Proxy | Nginx | Routing, HTTPS termination, production proxy |
| Deployment | Docker Compose for Phase 1 production-ready deployment | Backend, frontend, db, redis, workers, beat, nginx |

---

## 3. Why This Architecture

This project is not a simple CRUD panel. The core requirements include:

1. Reliable read-only integration with Kando APIs.
2. Structured and raw data storage for audit.
3. Automatic sync, snapshot building, screening, AI analysis, scoring, and ranking.
4. A deterministic and auditable Rule Engine.
5. A Ranking Engine with traceable score breakdowns.
6. A protected internal admin for technical operations.
7. A dedicated HR panel with strong UX for review workflows.
8. Production-ready security, RBAC, audit, Persian API error messages, observability, CI/CD, and operational runbooks.

Python/FastAPI is selected for backend because the system is integration-heavy, worker-heavy, data-processing-heavy, and may later need more advanced AI/NLP capabilities. Next.js/TypeScript is selected for the HR panel because the UI requires advanced tables, filters, Rule Builder flows, dashboards, API state handling, and controlled UX.

---

## 4. Backend Language and Libraries

Main backend language:

```text
Python 3.12+
```

Core backend libraries:

```text
FastAPI
Pydantic / pydantic-settings
SQLAlchemy
Alembic
httpx
Celery
Redis
SQLAdmin
python-jose or PyJWT
passlib / bcrypt
structlog or standard structured logging
pytest
pytest-asyncio
```

Backend responsibilities:

- Authentication and RBAC.
- Kando read-only integration.
- BaseData sync.
- Application snapshot building.
- Normalization.
- AI-assisted analysis orchestration.
- Rule Engine execution.
- Ranking Engine execution.
- Internal notes generation.
- Audit logging.
- Internal API for the Next.js panel.
- SQLAdmin mount on `/admin`.
- Worker and scheduler orchestration.

---

## 5. Frontend Language and Libraries

Main frontend language:

```text
TypeScript
```

Framework:

```text
Next.js App Router
```

Recommended frontend libraries:

```text
React
TanStack Query
TanStack Table
React Hook Form
Zod
Tailwind CSS
shadcn/ui or MUI
Playwright
Vitest
React Testing Library
```

Frontend responsibilities:

- HR login and authenticated app shell.
- Dashboard.
- Jobs list and job detail.
- RuleSet management and user-friendly Rule Builder.
- Applications list with server-side filtering, sorting, and pagination.
- Application detail view.
- AI Analysis tab/card.
- Decision and ranking explanation.
- Internal notes.
- Recruiter decision actions.
- Screening/ranking run visibility.
- Error and empty state handling using Persian user-facing copy where required.

---

## 6. High-Level System Architecture

```text
Kando ATS API
    ↓
Kando Integration Service
    ↓
Raw Kando Payloads + Normalized PostgreSQL Tables
    ↓
Application Snapshot Builder
    ↓
AI-Assisted Resume Analysis
    ↓
Rule Engine
    ↓
Ranking Engine
    ↓
Internal Status + Score + Rank + Notes + Audit
    ↓
Next.js SmartHire HR Panel

Internal Technical Admin: /admin via SQLAdmin
```

Core invariant:

```text
Kando is the read-only source.
SmartHire is the internal decision, note, ranking, queue, and audit system.
```

---

## 7. Backend Project Structure

Recommended backend structure:

```text
backend/
  app/
    main.py
    core/
      config.py
      security.py
      logging.py
      exceptions.py
      error_codes.py
      permissions.py
    db/
      session.py
      base.py
      seed.py
    models/
      user.py
      role.py
      permission.py
      kando_connection.py
      kando_base_data.py
      kando_job.py
      kando_application.py
      kando_candidate.py
      kando_cv.py
      kando_raw_payload.py
      screening_ruleset.py
      screening_rule_group.py
      screening_rule.py
      screening_rule_term.py
      screening_run.py
      screening_decision.py
      screening_score.py
      screening_note.py
      ai_analysis.py
      audit_log.py
      integration_error.py
      worker_task_log.py
    schemas/
      auth.py
      common.py
      errors.py
      kando.py
      snapshots.py
      rules.py
      screening.py
      ranking.py
      notes.py
      ai_analysis.py
    api/
      v1/
        auth.py
        users.py
        jobs.py
        applications.py
        rulesets.py
        screening.py
        ranking.py
        notes.py
        ai_analysis.py
        runs.py
        admin_tools.py
    services/
      kando_client.py
      kando_sync_service.py
      snapshot_builder.py
      normalization_service.py
      llm_client.py
      prompt_builder.py
      ai_analysis_service.py
      rule_engine.py
      ranking_engine.py
      note_generator.py
      audit_service.py
      permission_service.py
      error_service.py
    workers/
      celery_app.py
      sync_tasks.py
      ai_analysis_tasks.py
      screening_tasks.py
      ranking_tasks.py
      maintenance_tasks.py
    admin/
      setup.py
      auth.py
      views.py
    tests/
      unit/
      integration/
      fixtures/
  alembic/
  pyproject.toml
  Dockerfile
```

---

## 8. Database Model Families

The database must be normalized enough for querying and audit, while using JSONB for raw snapshots and flexible rule/AI output structures.

Main model groups:

1. **Auth and RBAC**
   - `users`
   - `roles`
   - `permissions`
   - `user_roles`
   - `role_permissions`

2. **Kando integration**
   - `kando_connections`
   - `kando_base_data_cache`
   - `kando_jobs`
   - `kando_hire_steps`
   - `kando_applications`
   - `kando_application_sources`
   - `kando_candidates`
   - `kando_cvs`
   - `kando_cv_work_experiences`
   - `kando_cv_university_degrees`
   - `kando_cv_language_skills`
   - `kando_raw_payloads`
   - `kando_api_call_logs`

3. **Screening and rules**
   - `screening_rulesets`
   - `screening_rule_groups`
   - `screening_rules`
   - `screening_rule_terms`
   - `screening_runs`
   - `screening_run_items`
   - `screening_decisions`
   - `screening_scores`
   - `screening_notes`

4. **AI-assisted analysis**
   - `ai_analysis_runs`
   - `ai_analysis_results`
   - `ai_prompt_versions` if prompt versions are DB-managed

5. **Audit and operations**
   - `audit_logs`
   - `integration_errors`
   - `worker_task_logs`
   - `system_settings`

All schema changes require Alembic migrations. Direct production schema changes are forbidden.

---

## 9. Key Data Model Requirements

### 9.1 `screening_applications`

Must store:

```text
id
kando_application_id
kando_candidate_id
kando_cv_id
kando_job_id
candidate_full_name
source_name
kando_hire_step_id
kando_status_id
internal_status
priority_score
priority_bucket
rank_in_job
snapshot_hash
ruleset_id
ruleset_version
last_synced_at
last_screened_at
last_ranked_at
raw_snapshot_json
created_at
updated_at
```

### 9.2 `screening_decisions`

Must store:

```text
id
screening_application_id
ruleset_id
ruleset_version
decision
confidence
reasons_json
matched_rules_json
missing_fields_json
ai_used
created_at
```

### 9.3 `ai_analysis_runs`

Must store:

```text
id
screening_application_id
ruleset_id
ruleset_version
provider
model_name
prompt_version
input_hash
status
started_at
finished_at
error_code
error_message_fa
retry_count
created_at
```

### 9.4 `audit_logs`

Must be immutable. Must store:

```text
id
actor_user_id
action
entity_type
entity_id
before_json
after_json
ip_address
user_agent
request_id
created_at
```

---

## 10. Kando Integration

### 10.1 Base URLs

```env
KANDO_ATS_BASE_URL=https://atsedgeapi.hrcando.ir
KANDO_BASEDATA_BASE_URL=https://basedataapinew.hrcando.ir
```

### 10.2 Authentication Header

```http
CompanyApiKey: <KANDO_COMPANY_API_KEY>
```

The Kando API key must never be exposed in frontend, logs, raw error messages, or SQLAdmin UI. Display only masked values.

### 10.3 Read-Only Boundary

Phase 1 must not call Kando write endpoints.

Forbidden in Phase 1:

```text
Kando status update
Kando note creation
Kando rejection action
Kando step transition
Kando tag mutation
```

### 10.4 Required Kando Read Endpoints

ATS Edge:

```text
GET /api/v1/Job/GetJobs
GET /api/v1/Job/GetHireSteps
GET /api/v1/Application/GetApplications
GET /api/v1/Application/GetApplicationSources
GET /api/v1/Candidate/GetCandidates
GET /api/v1/Cv/GetCvs
GET /api/v1/CV/GetCvWorkExperiences
GET /api/v1/Cv/GetCvUniversityDegrees
GET /api/v1/CV/GetCvLanguageSkills
GET /api/v1/Cv/GetCvSoftwareSkills
GET /api/v1/Application/GetApplicationChangeStates
GET /api/v1/Company/GetRejectReasons
GET /api/v1/Candidate/GetCandidateTags
GET /api/v1/Company/GetTags
```

BaseData:

```text
GET /api/v1/languages
GET /api/v1/skill-levels
GET /api/v1/academic-fields
GET /api/v1/university-degree-levels
GET /api/v1/job-categories
GET /api/v1/industries
GET /api/v1/seniority-levels
GET /api/v1/cities
```

### 10.5 Kando Client Requirements

The backend service `kando_client.py` must handle:

- Header injection.
- Timeouts.
- Controlled retry.
- Pagination.
- Response validation.
- Raw payload persistence.
- Integration error persistence.
- Sensitive data masking in logs.
- Kando schema change detection.

---

## 11. Automatic Worker Pipeline

The production Phase 1 pipeline is automatic:

```text
sync_kando_applications
    ↓
build_application_snapshot
    ↓
run_ai_analysis_if_enabled
    ↓
run_rule_engine
    ↓
run_ranking_engine
    ↓
generate_internal_notes
    ↓
update_recruiter_queues
```

Recruiters do not start routine screening manually. Manual execution is allowed only for `SUPER_ADMIN` and `SYSTEM_ADMIN` as reprocess/retry/debug.

### 11.1 Celery Queues

Recommended queues:

```text
sync
ai_analysis
screening
ranking
notifications
maintenance
```

### 11.2 Core Celery Tasks

```text
sync.base_data
sync.jobs
sync.hire_steps
sync.applications
sync.application_details
snapshot.build_for_application
ai_analysis.run_for_application
ai_analysis.run_for_job_batch
screening.run_for_application
screening.run_for_job
ranking.recalculate_for_job
notes.generate_for_application
maintenance.cleanup_old_raw_payloads
```

### 11.3 Scheduling

Recommended schedule:

```text
base data sync: daily
jobs sync: every 6 hours
application sync: every 30 minutes
failed retry sweep: every 15 minutes
ranking refresh: after screening, or on scoring config changes
```

All schedules must be configurable.

### 11.4 Idempotency Keys

To avoid duplicate processing, every run must account for:

```text
kando_application_id
kando_cv_id
kando_job_id
ruleset_id
ruleset_version
snapshot_hash
ai_input_hash
scoring_config_hash
```

---

## 12. AI Analysis Service

AI is a helper layer, not the final decision maker.

```text
AI assists. Rule Engine decides. Ranking Engine scores and orders.
```

AI may:

- Summarize structured resume data.
- Extract positive signals.
- Extract negative or ambiguous signals.
- Assist semantic/fuzzy matching.
- Generate Persian explanations where required.
- Suggest score reasons.

AI must not:

- Hard reject a candidate by itself.
- Pass a candidate by itself.
- Mutate Kando or SmartHire statuses directly.
- Use sensitive attributes or unrelated inferred traits.
- Send API keys, contact data, full raw payloads, or unnecessary personal data to an external model.

### 12.1 AI Provider Abstraction

The backend must not be locked to a single vendor.

Recommended services:

```text
llm_client.py
prompt_builder.py
ai_analysis_service.py
ai_analysis_tasks.py
```

Environment variables:

```env
AI_ANALYSIS_ENABLED=true
AI_PROVIDER=openai_compatible
AI_MODEL_NAME=
AI_API_BASE_URL=
AI_API_KEY=
AI_TIMEOUT_SECONDS=60
AI_MAX_RETRIES=2
AI_PROMPT_VERSION=v1
AI_MIN_CONFIDENCE=0.70
AI_STORE_RAW_OUTPUT=true
```

### 12.2 AI Output Validation

AI output must be JSON and must pass Pydantic validation. Free-form text is not acceptable as a stored AI result.

Invalid schema must produce a failed AI run with Persian `error_message_fa`.

---

## 13. Rule Engine

Rule Engine is deterministic and auditable.

It must support:

- RuleSets per Kando job.
- Versioned active RuleSets.
- Rule groups.
- `ALL` / `ANY` group logic.
- Reject gates.
- Pass gates.
- Override pass rules.
- Needs-review gates.
- Score bonuses and penalties.
- Info-only rules.
- AI signal targets with confidence thresholds.
- Missing data policy.
- Explanation templates.

AI-derived fields may be used as rule targets, but AI alone must not create final hard rejects by default.

---

## 14. Ranking Engine

Ranking Engine runs after Rule Engine.

Operational ranking applies only to:

```text
SMART_NOT_REJECTED
NEEDS_HUMAN_REVIEW
```

Ranking output must include:

```text
priority_score
priority_bucket
rank_in_job
score_reasons_json
matched_positive_rules
matched_negative_rules
```

Default buckets:

```text
HIGH
MEDIUM
LOW
REVIEW_UNKNOWN
```

Score and ranking reasons must be explainable in the application detail page.

---

## 15. Internal Statuses

SmartHire internal statuses:

```text
NOT_REVIEWED
SMART_REJECTED
SMART_NOT_REJECTED
NEEDS_HUMAN_REVIEW
UNSUPPORTED_SOURCE
SYNC_ERROR
ERROR
```

These statuses are stored only in SmartHire. They do not change Kando status.

---

## 16. Internal Notes

Notes are stored in SmartHire, not in Kando.

Note types:

```text
AI_SCREENING_NOTE
RECRUITER_NOTE
SYSTEM_NOTE
```

System-generated notes must include:

- Decision.
- Decision reasons.
- Score summary.
- Priority bucket.
- Rank in job.
- RuleSet name and version.
- AI signal summary if used.

The user-facing note text is intentionally Persian where required by the HR workflow.

---

## 17. Internal API

All internal APIs must follow the shared response and error contract.

Primary API families:

```text
/auth
/users
/jobs
/rulesets
/rule-groups
/rules
/applications
/applications/{id}/decision
/applications/{id}/ranking
/applications/{id}/notes
/applications/{id}/ai-analysis
/screening/runs
/ranking
/admin-tools
/audit-logs
/integration-errors
```

Manual force rerun endpoints are admin-only. They must not be visible as primary recruiter workflow actions.

---

## 18. Persian API Error Requirement

All backend API errors must include a Persian user-facing message:

```json
{
  "success": false,
  "error": {
    "code": "RULESET_NOT_ACTIVE",
    "message_fa": "برای این عنوان شغلی قانون فعال تعریف نشده است.",
    "details": {},
    "retryable": false
  }
}
```

English-only error responses are not acceptable.

---

## 19. SQLAdmin on `/admin`

SQLAdmin is for technical administration only.

Allowed audiences:

```text
SUPER_ADMIN
SYSTEM_ADMIN
TECH_SUPPORT
READ_ONLY_AUDITOR
```

Recruiters and HR users must not use SQLAdmin for daily workflow.

### 19.1 Editable Models

```text
User
Role
Permission
UserRole
KandoApiSetting
SystemSetting
ScreeningRuleSet
ScreeningRuleGroup
ScreeningRule
ScreeningRuleTerm
```

### 19.2 Read-Only Models

```text
KandoJob
KandoApplication
KandoCandidate
KandoCv
KandoRawPayload
KandoApiCallLog
ScreeningRun
ScreeningDecision
RankingResult
AIAnalysisRun
AIAnalysisResult
IntegrationError
AuditLog
```

### 19.3 SQLAdmin Requirements

- `/admin` must require authentication.
- `/admin` must enforce RBAC.
- Sensitive fields must be masked.
- Kando API key must never be shown in plain text.
- Kando cache data should be read-only.
- Audit logs must not be editable or deletable.
- Admin actions must be audited.

---

## 20. Next.js HR Panel

Core pages:

```text
/login
/dashboard
/jobs
/jobs/[jobId]
/jobs/[jobId]/rulesets
/jobs/[jobId]/rulesets/[rulesetId]
/jobs/[jobId]/applications
/applications
/applications/[applicationId]
/screening-runs
/screening-runs/[runId]
/ranking
/settings
```

Key UI requirements:

- Server-side pagination.
- Server-side sorting.
- Server-side filtering.
- Search by candidate/job/source where permitted.
- Priority bucket filters.
- Internal status filters.
- Rule Builder UI.
- Application detail with decision, ranking, notes, AI analysis, and source data.
- Permission-aware UI.
- Persian user-facing copy where required.

---

## 21. Security and Privacy

Mandatory requirements:

- RBAC for backend and frontend.
- SQLAdmin restricted to technical roles.
- Kando API key encrypted or secret-managed.
- Kando API key masked everywhere.
- Contact info access restricted.
- Raw payload access restricted.
- AI input minimization.
- No sensitive data in logs.
- Audit for sensitive reads and all mutations.
- Immutable audit logs.
- HTTPS in production.
- Separate staging and production environments.
- Backups and restore plan.
- Data retention policy.

---

## 22. Observability

Production Phase 1 must include:

- Structured logs.
- Request IDs.
- Worker task logs.
- Integration error logs.
- Kando sync status.
- AI run status.
- Screening/ranking run status.
- Celery queue monitoring.
- Health endpoints.
- Readiness endpoints.
- Error tracking.

---

## 23. Deployment

Production-ready Phase 1 uses Docker Compose with separated services:

```text
backend
frontend
postgres
redis
celery_worker
celery_beat
nginx
```

Required deployment files:

```text
docker-compose.yml
.env.example
nginx config
backend Dockerfile
frontend Dockerfile
migration command
backup script or runbook
release checklist
rollback plan
```

---

## 24. Testing Strategy

Backend tests:

- Unit tests for normalization.
- Unit tests for snapshot building.
- Unit tests for Rule Engine.
- Unit tests for Ranking Engine.
- Unit tests for AI output validation.
- Integration tests for Kando client with fixtures.
- API tests for error contract and RBAC.
- SQLAdmin access tests.
- Migration tests.

Frontend tests:

- API client tests.
- Rule Builder form validation tests.
- Applications table filtering/sorting tests.
- Application detail rendering tests.
- Error and empty state tests.
- Playwright workflow tests.

Fixture-based expected outputs are required to reduce human review.

---

## 25. Non-Goals for Phase 1

Phase 1 does not include:

- Mutating Kando statuses.
- Creating Kando notes.
- Rejecting directly in Kando.
- Moving Kando application steps.
- Reading original PDF/Word resume files unless Kando provides a new endpoint.
- Percentage-based English scoring.
- Final decisions made solely by AI.
- Replacing the recruiter.
- Using SQLAdmin as the HR workflow panel.

---

## 26. Implementation Guardrails for Claude

Claude must not:

- Invent Kando write integrations.
- Implement manual screening as the primary workflow.
- Hardcode customer support rules in Python.
- Use AI as final decision maker.
- Return English-only API errors.
- Modify active RuleSets in place.
- Expose Kando API keys.
- Skip migrations.
- Skip tests.
- Treat this as an Production-Ready Phase 1.

Claude must implement:

- Production-ready Phase 1.
- Automatic worker-based screening and ranking.
- Read-only Kando integration.
- Auditable decisions.
- Persian API error messages.
- RBAC, audit, logging, and operational safety.
