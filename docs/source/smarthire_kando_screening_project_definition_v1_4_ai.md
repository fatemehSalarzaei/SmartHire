# SmartHire Kando Screening & Ranking Assistant — Project Definition

**Document status:** Production-Ready Phase 1 / V1 scope  
**Language:** English  
**Primary source:** SmartHire Kando Screening Project Definition v1.4 AI  
**Implementation target:** Claude-assisted implementation  
**Product type:** Internal HR screening, ranking, and recruiter review platform  
**Kando integration mode:** Read-only in Phase 1  
**Screening execution model:** Automatic, scheduled, and event-driven  
**AI role:** AI-assisted analysis only; final decisions remain governed by auditable Rule Engine and Ranking Engine  

---

## 1. Executive Summary

SmartHire Kando Screening & Ranking Assistant is a production-ready Phase 1 system that connects to Kando ATS as a read-only data source, imports structured resume/application data, builds internal application snapshots, runs AI-assisted resume analysis, executes configurable screening rules, calculates candidate ranking scores, stores internal notes, and prepares ranked recruiter queues inside SmartHire.

In Phase 1, SmartHire does **not** modify any real state inside Kando. It does not reject candidates in Kando, move candidates between Kando hiring steps, add notes in Kando, or write tags/statuses back to Kando. All screening statuses, notes, scores, ranks, recruiter decisions, audit logs, and operational queues live inside SmartHire.

The system is not a prototype or Production-Ready Phase 1. It must be implemented as a production-ready Phase 1 release with secure authentication, RBAC, auditability, structured errors with Persian user-facing messages, automated workers, retry policies, testing, observability, and deployment discipline.

---

## 2. Core Product Decisions

The following decisions are non-negotiable for Phase 1:

1. **Kando is read-only.**
   SmartHire may call Kando GET/read APIs only.

2. **No Kando write operations.**
   SmartHire must not change Kando status, reject candidates in Kando, move hiring steps in Kando, add notes in Kando, or add tags in Kando.

3. **SmartHire owns internal workflow state.**
   Internal status, notes, scores, rankings, and recruiter review decisions are stored in SmartHire.

4. **Screening and ranking are automatic.**
   Recruiters do not manually start daily screening/ranking. Workers and scheduled jobs handle sync, snapshot building, AI analysis, rule evaluation, scoring, ranking, and queue preparation.

5. **Manual execution is admin-only.**
   Manual rerun, rescreen, rerank, and retry actions are limited to technical/admin roles for debugging, recovery, or controlled reprocessing.

6. **Language assessment is based on skill level, not percentage.**
   Kando currently provides language and skill level IDs, not 90% or 100% English percentages. English is evaluated through Kando language and skill-level Base Data.

7. **AI assists; Rule Engine decides.**
   AI can summarize resumes, extract signals, detect semantic relevance, and suggest score reasons. It cannot be the sole basis for final pass/reject decisions.

8. **All decisions must be auditable.**
   Every screening decision and ranking score must include matched rules, missing fields, reasons, ruleset version, and relevant AI signals when used.

9. **Rules must not be hardcoded.**
   Customer Support rules are initial templates only. Users must be able to create, clone, version, activate, deactivate, and customize rules per job.

10. **All backend API errors must include Persian user-facing messages.**
    English-only API errors are not acceptable for user-facing flows.

---

## 3. Project Goals

The project aims to build a production-grade internal platform that can:

1. Connect securely to Kando ATS using the company API key.
2. Sync jobs, applications, candidates, CVs, work experiences, education records, language skills, and Base Data from Kando.
3. Build complete internal application snapshots for screening and audit.
4. Allow HR/admin users to define job-specific screening and ranking rules through a flexible Rule Builder.
5. Automatically run AI-assisted resume analysis where enabled.
6. Automatically run screening based on active RuleSets.
7. Automatically calculate candidate priority scores and job-level rankings.
8. Store internal SmartHire statuses and notes.
9. Present recruiters with ranked queues of candidates to review.
10. Preserve full audit trails for decisions, rule changes, AI analysis, admin actions, and recruiter decisions.
11. Avoid false hard rejects caused by missing data by routing ambiguous or incomplete cases to human review.
12. Provide production-grade deployment, monitoring, backup, security, and operational workflows.

---

## 4. Phase 1 Scope

### 4.1 In Scope

Phase 1 includes:

- Read-only connection to Kando ATS APIs.
- Kando API key configuration and secure storage.
- Kando IP whitelist readiness.
- Sync of Kando Base Data.
- Sync of Kando jobs and hiring steps.
- Sync of Kando applications, application sources, candidates, CVs, work experiences, education records, language skills, and software skills where available.
- Internal normalized tables and raw JSON snapshots.
- Application snapshot builder.
- Text normalization for Persian and English.
- RuleSet management per Kando job.
- Flexible Rule Builder.
- Rule versioning and activation workflow.
- AI-assisted resume analysis.
- Automatic screening pipeline.
- Automatic ranking pipeline.
- Internal status management.
- Internal note generation.
- Recruiter review queues.
- Recruiter notes and recruiter decisions.
- SQLAdmin internal technical admin panel on `/admin`.
- Next.js HR operational panel.
- RBAC and permission matrix.
- Audit logging.
- Persian API error contract.
- Production-ready tests and fixtures.
- Docker-based local and deployment baseline.
- Observability, runbooks, backup/restore, and operational documentation.

### 4.2 Out of Scope for Phase 1

Phase 1 does not include:

- Changing application status in Kando.
- Rejecting candidates in Kando.
- Moving candidates between Kando hiring steps.
- Adding notes to Kando.
- Adding tags to Kando.
- Reading raw PDF/Word resume files from Kando, unless Kando provides a future file API.
- OCR or parsing raw resume files.
- Screening based on English percentage values.
- Fully autonomous hiring decisions.
- AI-only reject/pass decisions.
- Candidate messaging.
- Interview scheduling automation.
- Replacing human recruiter judgment.
- Using SQLAdmin as the daily HR operational panel.

---

## 5. User Roles

Recommended roles:

| Role | Description |
|---|---|
| `SUPER_ADMIN` | Full system access, including sensitive settings and emergency actions. |
| `SYSTEM_ADMIN` | Technical administration, integration settings, retries, SQLAdmin access. |
| `HR_MANAGER` | Manages jobs, rulesets, recruiter review workflow, reports. |
| `RECRUITER` | Reviews candidate queues, reads decisions, adds notes, records recruiter decisions. |
| `REVIEWER` | Read/review access without system administration privileges. |
| `READ_ONLY_AUDITOR` | Read-only audit and reporting access. |

SQLAdmin access must be limited to `SUPER_ADMIN` and `SYSTEM_ADMIN` unless explicitly extended.

---

## 6. System Architecture

High-level flow:

```text
Kando ATS APIs
    ↓
Kando Integration Service
    ↓
Raw Payload Storage + Normalized PostgreSQL Tables
    ↓
Application Snapshot Builder
    ↓
AI-Assisted Resume Analysis
    ↓
Rule Engine
    ↓
Ranking Engine
    ↓
Internal Status + Notes + Audit
    ↓
SmartHire HR Panel
```

Technical stack:

```text
Backend: Python + FastAPI
ORM: SQLAlchemy
Database: PostgreSQL
Migrations: Alembic
Admin: SQLAdmin mounted on /admin
Frontend: Next.js + TypeScript
Workers: Celery + Redis
Deployment baseline: Docker Compose + production-ready environment separation
```

---

## 7. Kando Integration

### 7.1 Base URLs

```env
KANDO_ATS_BASE_URL=https://atsedgeapi.hrcando.ir
KANDO_BASEDATA_BASE_URL=https://basedataapinew.hrcando.ir
```

### 7.2 Authentication

Kando requests must include:

```http
CompanyApiKey: <secret-api-key>
```

Recommended environment variables:

```env
KANDO_API_HEADER_KEY=CompanyApiKey
KANDO_API_KEY=<secret>
KANDO_DEFAULT_PAGE_SIZE=100
KANDO_TIMEOUT_SECONDS=30
KANDO_MAX_RETRIES=3
```

### 7.3 Connection Rules

- SmartHire server IP must be whitelisted by Kando.
- Kando API key must never be exposed in frontend, logs, Git, error traces, or public files.
- API key must be stored in a secure secret mechanism or encrypted configuration.
- Kando client must support timeout, retry, backoff, pagination, and structured integration errors.
- All Kando API calls must be logged safely without sensitive headers.

---

## 8. Kando APIs Used in Phase 1

### 8.1 ATS Edge APIs

| Need | Endpoint | Usage |
|---|---|---|
| Jobs | `GET /api/v1/Job/GetJobs` | Sync job IDs, titles, descriptions, conditions, requirements. |
| Hire steps | `GET /api/v1/Job/GetHireSteps` | Sync hiring step IDs and titles. |
| Applications | `GET /api/v1/Application/GetApplications` | Sync application IDs, job IDs, candidate IDs, status/hire step metadata. |
| Application sources | `GET /api/v1/Application/GetApplicationSources` | Sync source, CV ID, cover letter, job board data, work experience summary. |
| Candidates | `GET /api/v1/Candidate/GetCandidates` | Sync candidate profile, name, email, phone, birth date, city. |
| CVs | `GET /api/v1/Cv/GetCvs` | Sync structured CV data, about me, skills, work type, salary fields. |
| Work experiences | `GET /api/v1/CV/GetCvWorkExperiences` | Sync role title, company, industry, job category, dates, descriptions. |
| Education | `GET /api/v1/Cv/GetCvUniversityDegrees` | Sync university, field, degree, GPA, years. |
| Language skills | `GET /api/v1/CV/GetCvLanguageSkills` | Sync language ID and skill level ID. |
| Software skills | `GET /api/v1/Cv/GetCvSoftwareSkills` | Sync software skill data if present. |
| Application state history | `GET /api/v1/Application/GetApplicationChangeStates` | Audit and future comparison. |
| Reject reasons | `GET /api/v1/Company/GetRejectReasons` | Read-only lookup for display/future integration. |
| Candidate tags | `GET /api/v1/Candidate/GetCandidateTags` | Read-only lookup for audit/future use. |
| Company tags | `GET /api/v1/Company/GetTags` | Read-only lookup for audit/future use. |

### 8.2 Base Data APIs

| Need | Endpoint | Usage |
|---|---|---|
| Languages | `GET /api/v1/languages` | Map `languageId` to English/Persian language title. |
| Skill levels | `GET /api/v1/skill-levels` | Map `skillLevelId` to Advanced/Intermediate/Beginner. |
| Academic fields | `GET /api/v1/academic-fields` | Map academic field IDs to field names. |
| Degree levels | `GET /api/v1/university-degree-levels` | Map degree level IDs. |
| Job categories | `GET /api/v1/job-categories` | Map work experience job categories. |
| Industries | `GET /api/v1/industries` | Map work experience industries. |
| Seniority levels | `GET /api/v1/seniority-levels` | Optional experience scoring. |
| Cities | `GET /api/v1/cities` | Optional display/filtering. |

---

## 9. Resume File Limitation

Current Kando documentation does not provide a field or endpoint for downloading raw resume files such as PDF, Word, attachment URLs, base64 content, or original resume files.

SmartHire Phase 1 must therefore rely on structured Kando CV data only.

The system must not assume the presence of:

```text
resumeFileUrl
cvFileUrl
attachmentUrl
downloadUrl
pdfUrl
base64
originalResumeFile
```

Internal metadata should include:

```text
original_resume_file_available = false
```

---

## 10. Internal SmartHire Statuses

SmartHire stores its own internal status for each synced application.

| Status | Meaning |
|---|---|
| `NOT_REVIEWED` | Application has not yet been processed internally. |
| `SMART_REJECTED` | Application was rejected by SmartHire internal rules. |
| `SMART_NOT_REJECTED` | Application was not rejected and should be reviewed by recruiter. |
| `NEEDS_HUMAN_REVIEW` | Data is missing, ambiguous, or requires human judgment. |
| `UNSUPPORTED_SOURCE` | Application source or CV structure cannot be processed. |
| `SYNC_ERROR` | Error occurred while syncing from Kando. |
| `ERROR` | General processing error. |

These statuses do not change Kando.

---

## 11. Rule Builder

### 11.1 Purpose

Rule Builder allows authorized users to define job-specific screening and ranking behavior without hardcoding conditions in Python or frontend code.

Every Kando job can have one active RuleSet.

### 11.2 RuleSet Concepts

```text
RuleSet
  ├── RuleGroup
  │     ├── Rule
  │     ├── Rule
  │     └── Rule
  └── RuleGroup
        ├── Rule
        └── Rule
```

### 11.3 Rule Types

| Rule Type | Purpose |
|---|---|
| `REJECT_GATE` | If matched, can reject unless overridden or configured otherwise. |
| `PASS_GATE` | Confirms required condition. |
| `OVERRIDE_PASS` | Allows specific strong signals to compensate for a missing condition. |
| `NEEDS_REVIEW_GATE` | Routes ambiguous/missing data to human review. |
| `SCORE_BONUS` | Adds positive score. |
| `SCORE_PENALTY` | Adds negative score. |
| `INFO_ONLY` | Only records information, no decision impact. |

### 11.4 Rule Targets

Supported targets include:

```text
candidate.age
candidate.city
candidate.birth_date
application.source
application.total_work_experience
application.current_kando_status
application.current_kando_hire_step
cv.about_me
cv.skills
language.english_level
language.any_language_level
education.university_name
education.field_name
education.degree_level
education.gpa
work.role_title
work.company_name
work.job_category
work.industry
work.description
work.duration_months
ai.related_experience.is_related
ai.related_experience.confidence
ai.positive_signals.code
ai.negative_signals.code
ai.ambiguities.code
```

### 11.5 Operators

Supported operators:

```text
EXISTS
NOT_EXISTS
EQUALS
NOT_EQUALS
IN
NOT_IN
CONTAINS
NOT_CONTAINS
CONTAINS_ANY
FUZZY_MATCH
FUZZY_IN
REGEX_MATCH
GREATER_THAN
GREATER_THAN_OR_EQUAL
LESS_THAN
LESS_THAN_OR_EQUAL
BETWEEN
DURATION_AT_LEAST
```

### 11.6 Rule Safety

- Active RuleSets must not be overwritten in place.
- Important RuleSet changes must create a new version.
- Reject rules must require explanation.
- High-impact reject rules should require preview before activation.
- Sensitive attributes must require higher permissions.
- AI-based hard reject must be disabled by default.

---

## 12. Default Customer Support Rules Template

The following are initial templates only. They must not be hardcoded.

### 12.1 English Language

Default interpretation:

```text
English + Advanced => acceptable
English + Intermediate => reject or lower score depending on policy
English + Beginner => reject by default
Missing English => NEEDS_HUMAN_REVIEW by default
```

### 12.2 Age

Default age rule:

```text
age <= 21 => SMART_REJECTED
22 <= age <= 35 => age condition passed
age >= 36 => SMART_REJECTED
missing age => NEEDS_HUMAN_REVIEW
```

### 12.3 Related Experience

Default related experience terms include:

```text
Sales
Account Management
Account Manager
Account Executive
English Teacher
Customer Support
Support Specialist
Customer Service
Customer Relations
Call Center
Contact Center
Translator
Customer Success
Customer Retention
Customer Experience
After Sales
Content Specialist
Content Creator
```

### 12.4 Education Override

Missing related work experience may be compensated by selected universities or academic fields if the RuleSet allows override behavior.

Suggested universities:

```text
Sharif University of Technology
University of Tehran
Iran University of Science and Technology
Amirkabir University of Technology
Isfahan University of Technology
K. N. Toosi University of Technology
Shahid Beheshti University
Allameh Tabataba'i University
Kharazmi University
```

Suggested academic fields:

```text
International Business
ECO Insurance
Politics and International Relations
English Translation
English Language Teaching
English Language
Foreign Languages
Other language-related programs
```

---

## 13. Ranking and Prioritization

Ranking runs after screening.

```text
Step 1: Determine internal screening status
Step 2: Calculate score
Step 3: Assign priority bucket
Step 4: Calculate rank within job
```

Operational ranking applies mainly to:

```text
SMART_NOT_REJECTED
NEEDS_HUMAN_REVIEW
```

`SMART_REJECTED` applications are not part of recruiter priority queues, except for reporting and audit.

### 13.1 Score Model

Recommended conceptual formula:

```text
Total Score = Base Score + Positive Scores + Bonus Scores - Negative Scores
```

Recommended score range:

```text
0 to 100
```

### 13.2 Priority Buckets

| Bucket | Suggested Rule | Meaning |
|---|---:|---|
| `HIGH` | `score >= 75` | High-priority recruiter review. |
| `MEDIUM` | `50 <= score < 75` | Normal review. |
| `LOW` | `score < 50` | Lower-priority review. |
| `REVIEW_UNKNOWN` | insufficient data | Human review required. |

### 13.3 Rank Calculation

Rank must be calculated per Kando job.

Tie-breakers:

1. Higher score.
2. More passed gates.
3. More positive matched reasons.
4. Fewer missing fields.
5. Configurable received date ordering.

---

## 14. AI-Assisted Resume Analysis

### 14.1 Purpose

AI analysis is a supporting layer that extracts semantic signals from structured resume data.

It may:

- Summarize the resume in Persian.
- Detect semantically related work experience.
- Extract positive signals.
- Extract negative signals or ambiguities.
- Support fuzzy/semantic matching.
- Suggest score reasons.
- Generate recruiter-friendly Persian explanations.

It must not:

- Make final pass/reject decisions by itself.
- Reject candidates without Rule Engine validation.
- Change SmartHire or Kando status directly.
- Use hallucinated content as factual resume evidence.
- Infer sensitive or irrelevant candidate attributes.
- Receive unnecessary personal data.

### 14.2 Pipeline Position

```text
Kando Structured Data
    ↓
Normalization + Snapshot Builder
    ↓
AI-Assisted Resume Analysis
    ↓
Rule Engine
    ↓
Ranking Engine
    ↓
Internal Status + Score + Rank + Notes
```

### 14.3 AI Input

AI input must be minimized and job-relevant.

Allowed input:

```json
{
  "job": {
    "title": "Customer Support Specialist",
    "requirements": "...",
    "ruleset_summary": "..."
  },
  "candidate_cv": {
    "about_me": "...",
    "skills": ["..."],
    "work_experiences": [
      {
        "role_title": "...",
        "company_name": "...",
        "industry": "...",
        "description": "...",
        "duration_months": 18
      }
    ],
    "education": [
      {
        "university_name": "...",
        "field_name": "...",
        "degree_level": "..."
      }
    ],
    "language_skills": [
      {
        "language": "English",
        "level": "Advanced"
      }
    ],
    "cover_letter": "..."
  }
}
```

Forbidden input unless explicitly approved:

```text
phone
email
exact address
Kando API key
raw full payload
unnecessary personal data
```

### 14.4 AI Output

AI output must be valid JSON and schema-validated.

Example:

```json
{
  "summary_fa": "کاندیدا سابقه پشتیبانی مشتری و مهارت زبان انگلیسی پیشرفته دارد.",
  "related_experience": {
    "is_related": true,
    "confidence": 0.82,
    "matched_categories": ["customer_support", "sales"],
    "evidence": ["عنوان شغلی شامل Customer Support است"]
  },
  "positive_signals": [
    {
      "code": "SUPPORT_EXPERIENCE",
      "label_fa": "سابقه پشتیبانی مشتری",
      "confidence": 0.86,
      "evidence": "..."
    }
  ],
  "negative_signals": [],
  "ambiguities": [],
  "suggested_score_reasons": [
    {
      "reason_code": "RELATED_SUPPORT_EXPERIENCE",
      "suggested_score_delta": 15,
      "explanation_fa": "سابقه مرتبط با پشتیبانی مشتری شناسایی شد"
    }
  ]
}
```

### 14.5 AI Failure Handling

If AI fails:

- Screening must not stop.
- Rule Engine should continue with structured Kando data.
- AI run status must be saved as failed/skipped.
- Persian error message must be stored.
- Retry should follow policy.
- If a RuleSet explicitly requires AI, output should become `NEEDS_HUMAN_REVIEW`, not hard reject.

---

## 15. Automatic Screening Pipeline

Screening and ranking are automatic.

Primary pipeline:

```text
Scheduled Sync / Change Detection
    ↓
Build or Update Application Snapshot
    ↓
Run AI Analysis if Enabled
    ↓
Run Rule Engine
    ↓
Run Ranking Engine
    ↓
Generate Internal Notes
    ↓
Update Recruiter Queues
```

### 15.1 Recommended Schedule

Production-ready default:

```text
Base Data sync: daily
Jobs sync: every 6 hours
Applications sync: every 30 minutes
Screening: automatically after snapshot change
Ranking: automatically after screening/scoring changes
Retry failed tasks: according to retry policy
```

### 15.2 Automatic Triggers

| Trigger | Behavior |
|---|---|
| New Kando application | Build snapshot, run AI if enabled, screen, rank. |
| Changed application/CV data | Compare snapshot hash and rerun if changed. |
| New active RuleSet | Rescreen related job applications. |
| Changed scoring weights | Rerank related applications. |
| Failed retryable task | Retry with backoff. |

### 15.3 Idempotency Keys

Use these to avoid duplicate processing:

```text
kando_application_id
kando_cv_id
kando_job_id
ruleset_id
ruleset_version
snapshot_hash
scoring_config_hash
ai_input_hash
```

---

## 16. Internal Notes

Internal notes are stored in SmartHire only.

Note types:

```text
AI_SCREENING_NOTE
RECRUITER_NOTE
SYSTEM_NOTE
```

### 16.1 Not-Rejected Note Template

```text
Automatic review by SmartHire was completed.
Result: The resume was not rejected under the current rules and requires recruiter review.
Priority: {priority_bucket}
Score: {priority_score}/100
Rank in this job: {rank_in_job}
Passed reasons: {matched_reasons}
Score reasons: {score_reasons}
Rule version: {ruleset_name} v{version}
```

### 16.2 Rejected Note Template

```text
Automatic review by SmartHire was completed.
Result: The resume was rejected in internal screening.
Reject reasons: {reject_reasons}
Rule version: {ruleset_name} v{version}
```

### 16.3 Needs-Review Note Template

```text
Automatic review by SmartHire was completed.
Result: A final decision could not be made and human review is required.
Reason: {missing_or_ambiguous_fields}
Optional helper score: {priority_score}/100
Rule version: {ruleset_name} v{version}
```

Persian equivalents must be used for user-facing UI and API messages where required.

---

## 17. Data Model Overview

Core tables:

```text
users
roles
permissions
user_roles
kando_connections
kando_base_data_cache
kando_jobs
kando_hire_steps
kando_applications
kando_application_sources
kando_candidates
kando_cvs
kando_cv_work_experiences
kando_cv_university_degrees
kando_cv_language_skills
kando_raw_payloads
screening_rulesets
screening_rule_groups
screening_rules
screening_rule_terms
screening_applications
screening_runs
screening_run_items
screening_decisions
screening_scores
screening_notes
recruiter_decisions
ai_analysis_runs
ai_analysis_results
integration_errors
audit_logs
worker_task_logs
```

Important requirements:

- Raw Kando payloads should be read-only after ingestion.
- Active RuleSets must be versioned.
- Screening decisions must store ruleset version.
- AI runs must store provider, model name, prompt version, input hash, status, and Persian error message if failed.
- Audit logs must be immutable.
- Sensitive data must be masked where appropriate.

---

## 18. SmartHire Internal APIs

API groups:

```text
Auth
Users/Roles/Permissions
Kando Settings
Jobs
RuleSets
Rule Builder
Applications
Application Details
AI Analysis
Screening Runs
Ranking
Notes
Recruiter Decisions
Audit Logs
Integration Errors
Automation Status
Admin Reprocess
```

API rules:

- All list endpoints must support pagination.
- List endpoints should support server-side filtering and sorting.
- All errors must use structured error shape.
- All user-facing error messages must include Persian text.
- Sensitive data must be hidden unless user has permission.
- Admin-only rerun endpoints must be protected and audited.

---

## 19. Error Contract

All API errors must use a consistent structure:

```json
{
  "success": false,
  "error": {
    "code": "RULESET_NOT_ACTIVE",
    "message_fa": "برای این عنوان شغلی قانون فعال تعریف نشده است.",
    "message_en": "No active ruleset exists for this job.",
    "details": {},
    "retryable": false
  },
  "request_id": "..."
}
```

Persian `message_fa` is mandatory.

Example error codes:

```text
KANDO_CONNECTION_FAILED
KANDO_AUTH_FAILED
KANDO_RATE_LIMITED
RULESET_NOT_ACTIVE
RULESET_VERSION_CONFLICT
APPLICATION_NOT_FOUND
AI_ANALYSIS_UNAVAILABLE
AI_SCHEMA_VALIDATION_FAILED
PERMISSION_DENIED
VALIDATION_ERROR
INTERNAL_SERVER_ERROR
```

---

## 20. Frontend Requirements

The main HR panel must be built with Next.js and TypeScript.

Required pages:

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

Required UI capabilities:

- Server-side pagination.
- Server-side filtering.
- Server-side sorting.
- Candidate search.
- Filters by job, internal status, priority bucket, source, language level, university, academic field.
- Candidate detail page.
- Rule Builder UI.
- AI analysis card/tab.
- Decision reasons and score breakdown.
- Internal note management.
- Recruiter decision actions.
- Persian error display.
- Empty states.
- Permission-aware UI.
- Loading and retry states.

Recruiters must not start the primary screening workflow manually. They only review prepared queues.

---

## 21. SQLAdmin Requirements

SQLAdmin is mounted on:

```text
/admin
```

It is for technical/internal use only.

Editable models:

```text
User
Role
Permission
UserRole
KandoConnection
SystemSetting
ScreeningRuleSet
ScreeningRuleGroup
ScreeningRule
ScreeningRuleTerm
```

Read-only models:

```text
KandoJob
KandoApplication
KandoCandidate
KandoCv
KandoRawPayload
ScreeningRun
ScreeningDecision
RankingResult
AIAnalysisRun
AIAnalysisResult
IntegrationError
AuditLog
```

Rules:

- HR users must not use SQLAdmin for daily work.
- Kando synced data should be read-only.
- Audit logs must not be editable or deletable.
- API keys must be masked.
- Sensitive candidate fields must be permission-controlled.
- SQLAdmin actions must be audited.

---

## 22. Security and Privacy

Security requirements:

- JWT authentication for Phase 1.
- RBAC for all sensitive operations.
- SQLAdmin access limited to technical/admin roles.
- Kando API key never exposed in frontend/logs.
- Candidate email/phone/birth date access controlled.
- Raw Kando payload access restricted.
- Sensitive admin actions audited.
- AI input minimized.
- AI provider configuration secured.
- Raw AI prompt/output access restricted.
- HTTPS required in production.
- Environment separation required for local/staging/production.

---

## 23. Observability and Operations

Production-ready Phase 1 requires:

- Structured logs.
- Request IDs.
- Worker task logs.
- Integration error logs.
- Celery monitoring readiness.
- Sync status dashboard.
- AI run status dashboard.
- Retry visibility.
- Backup and restore process.
- Migration policy.
- Release checklist.
- Rollback plan.
- Incident response runbook.
- Data retention policy.

---

## 24. Reporting and Metrics

Reports should include:

- Total synced applications.
- Total screened applications.
- Rejected count.
- Not-rejected count.
- Needs-human-review count.
- Error count.
- Rejection rate by RuleSet.
- Top rejection reasons.
- Average score by job.
- Priority bucket distribution.
- Top candidates by job.
- Missing-data cases.
- AI analysis success/failure rate.
- Comparison of SmartHire recommendations with recruiter decisions.

Quality metrics:

| Metric | Meaning |
|---|---|
| False Reject Rate | Cases SmartHire rejected but recruiter would accept. |
| Human Review Rate | Cases routed to human review. |
| Rule Coverage | Percentage of applications resolved by current rules. |
| Ranking Usefulness | Alignment between ranking and recruiter approval. |
| Sync Failure Rate | Kando integration failures. |
| AI Failure Rate | Failed or invalid AI analysis rate. |
| High Bucket Conversion | Percentage of high-priority candidates approved by recruiter. |

---

## 25. Acceptance Criteria

Production-Ready Phase 1 is acceptable only when:

1. Kando connection works with secure API key handling.
2. Base Data sync works and is cached.
3. Jobs sync and display correctly.
4. Applications, candidates, CVs, work experiences, education, and language skills sync correctly.
5. Application snapshots are built and hashed.
6. RuleSets can be created, cloned, versioned, activated, and archived.
7. Rule Builder supports custom user-defined rules.
8. Screening runs automatically after sync or relevant data changes.
9. Ranking runs automatically after screening/scoring changes.
10. AI analysis runs as an independent optional step.
11. AI output is JSON-schema validated.
12. AI cannot independently hard reject or final-pass candidates.
13. Missing important data defaults to human review unless policy says otherwise.
14. Internal statuses are stored in SmartHire only.
15. Internal notes are generated and stored.
16. Recruiter queues display ranked candidates.
17. Candidate detail page shows decision reasons, score breakdown, AI analysis, notes, and recruiter actions.
18. All backend API errors include Persian messages.
19. SQLAdmin is protected, audited, and not used as HR workflow UI.
20. Sensitive data is masked or permission-controlled.
21. All schema changes have Alembic migrations.
22. Tests cover rule engine, ranking engine, AI schema validation, Kando client mock behavior, API errors, permissions, and frontend critical flows.
23. Deployment, rollback, backup/restore, observability, and runbooks are documented.
24. No Kando write API is called.

---

## 26. Future Kando Requests

For later phases, request these APIs/capabilities from Kando:

1. Change application status.
2. Reject application with reject reason.
3. Add note/comment to application or candidate.
4. Add tag to candidate/application.
5. Retrieve status definitions with human-readable titles.
6. Retrieve changed applications from a specific timestamp.
7. Download original resume file if available.
8. Retrieve English percentage if available from source job board.
9. Official rate limit and pagination documentation.
10. Webhook for new/updated applications.

---

## 27. Final Product Principle

```text
Kando provides data.
SmartHire builds snapshots.
AI assists analysis.
Rule Engine makes auditable screening decisions.
Ranking Engine prioritizes candidates.
SmartHire stores internal statuses, notes, scores, ranks, and audit.
Recruiters review prepared queues and make final human decisions.
```
