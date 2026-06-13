# File Inventory

```text
smarthire_claude_implementation_pack/
├── .env.example
├── .gitignore
├── CLAUDE.md
├── Makefile
├── README.md
├── backend
│   ├── app
│   │   └── .gitkeep
│   └── tests
│       └── .gitkeep
├── docker-compose.yml
├── docs
│   ├── 00-product
│   │   ├── decision-invariants.md
│   │   ├── glossary.md
│   │   ├── project-definition.md
│   │   └── scope-and-non-goals.md
│   ├── 01-architecture
│   │   ├── adr
│   │   │   ├── 0001-use-fastapi-postgresql-nextjs.md
│   │   │   ├── 0002-kando-readonly-phase-one.md
│   │   │   ├── 0003-ai-assisted-not-final-decision.md
│   │   │   └── 0004-automatic-screening-worker-based.md
│   │   ├── architecture-baseline.md
│   │   ├── async-pipeline.md
│   │   ├── data-flow.md
│   │   └── module-boundaries.md
│   ├── 02-integrations
│   │   ├── kando-api-contract.md
│   │   ├── kando-field-mapping.md
│   │   ├── kando-pagination-and-retry.md
│   │   └── kando-readonly-boundary.md
│   ├── 03-api
│   │   ├── api-design-rules.md
│   │   ├── error-contract.md
│   │   ├── fa-api-error-messages.md
│   │   ├── internal-openapi.yaml
│   │   └── pagination-filter-sort-contract.md
│   ├── 04-database
│   │   ├── database-schema.md
│   │   ├── erd.md
│   │   ├── indexes-and-constraints.md
│   │   ├── migration-policy.md
│   │   ├── model-field-spec.md
│   │   └── seed-data-policy.md
│   ├── 05-contracts
│   │   ├── api-response-shapes.md
│   │   ├── audit-log-contract.md
│   │   ├── enums.md
│   │   ├── snapshot-contract.md
│   │   └── status-lifecycle.md
│   ├── 06-domain
│   │   ├── normalization-spec.md
│   │   ├── note-generation-spec.md
│   │   ├── ranking-engine-spec.md
│   │   ├── recruiter-decision-spec.md
│   │   ├── rule-engine-spec.md
│   │   └── screening-pipeline-spec.md
│   ├── 07-ai
│   │   ├── ai-assisted-analysis-spec.md
│   │   ├── ai-fallback-policy.md
│   │   ├── ai-output-schema.md
│   │   ├── ai-safety-and-privacy.md
│   │   └── prompt-library.md
│   ├── 08-backend
│   │   ├── backend-architecture.md
│   │   ├── backend-error-handling.md
│   │   ├── backend-folder-structure.md
│   │   ├── backend-testing-spec.md
│   │   ├── celery-tasks-and-queues.md
│   │   ├── fastapi-routing-spec.md
│   │   ├── service-layer-spec.md
│   │   └── sqladmin-spec.md
│   ├── 09-frontend
│   │   ├── api-client-spec.md
│   │   ├── fa-copy-dictionary.md
│   │   ├── frontend-architecture.md
│   │   ├── frontend-error-handling.md
│   │   ├── frontend-folder-structure.md
│   │   ├── page-specs.md
│   │   ├── rule-builder-ui-spec.md
│   │   ├── table-filter-sort-spec.md
│   │   └── ui-state-matrix.md
│   ├── 10-security
│   │   ├── audit-policy.md
│   │   ├── permission-matrix.md
│   │   ├── security-privacy.md
│   │   └── sensitive-data-policy.md
│   ├── 11-quality
│   │   ├── acceptance-criteria.md
│   │   ├── definition-of-done.md
│   │   ├── fixture-strategy.md
│   │   ├── production-quality-gates.md
│   │   ├── review-checklist.md
│   │   └── test-strategy.md
│   ├── 12-deployment
│   │   ├── ci-cd-pipeline.md
│   │   ├── deployment-plan.md
│   │   ├── docker-compose-spec.md
│   │   ├── environment-variables.md
│   │   ├── release-checklist.md
│   │   ├── rollback-plan.md
│   │   └── staging-production-plan.md
│   ├── 13-operations
│   │   ├── backup-restore.md
│   │   ├── data-retention-policy.md
│   │   ├── failure-recovery.md
│   │   ├── incident-response.md
│   │   ├── observability-spec.md
│   │   ├── runbook.md
│   │   └── scheduled-jobs.md
│   ├── 14-performance
│   │   ├── celery-worker-scaling.md
│   │   ├── database-indexing-policy.md
│   │   ├── pagination-and-query-performance.md
│   │   └── performance-baseline.md
│   ├── 15-compliance
│   │   ├── ai-data-handling-policy.md
│   │   ├── audit-retention-policy.md
│   │   ├── privacy-policy.md
│   │   └── sensitive-data-masking.md
│   ├── claude
│   │   ├── coding-standards.md
│   │   ├── context-index.md
│   │   ├── do-not-violate.md
│   │   ├── implementation-roadmap.md
│   │   ├── prompts
│   │   │   ├── 00-bootstrap-repository.md
│   │   │   ├── 01-backend-foundation.md
│   │   │   ├── 02-database-models-and-migrations.md
│   │   │   ├── 03-auth-rbac-and-audit.md
│   │   │   ├── 04-kando-read-only-integration.md
│   │   │   ├── 05-snapshot-and-normalization.md
│   │   │   ├── 06-ai-analysis-layer.md
│   │   │   ├── 07-rule-engine-and-ranking-engine.md
│   │   │   ├── 08-celery-automation.md
│   │   │   ├── 09-sqladmin.md
│   │   │   ├── 10-internal-api.md
│   │   │   ├── 11-frontend-foundation.md
│   │   │   ├── 12-frontend-pages.md
│   │   │   ├── 13-tests-and-fixtures.md
│   │   │   ├── 14-observability-security-and-hardening.md
│   │   │   └── 15-final-review-and-release-readiness.md
│   │   ├── review-protocol.md
│   │   └── task-breakdown.md
│   └── source
│       ├── kando
│       │   ├── AtsEdgeApi_SecondDocument_Version1.0.0.pdf
│       │   ├── AtsEdgeApi_Version1.pdf
│       │   ├── Cando Base Data - Postman Collection.json
│       │   └── Cando-AtsEdge-postman-collection-v001.json
│       ├── smarthire_kando_screening_project_definition_v1_4_ai.md
│       └── smarthire_technology_stack_and_architecture_v1_3_ai.md
├── frontend
│   ├── app
│   │   └── .gitkeep
│   ├── components
│   │   └── .gitkeep
│   └── lib
│       └── .gitkeep
├── infra
│   ├── nginx
│   │   ├── .gitkeep
│   │   └── default.conf
│   └── scripts
│       └── .gitkeep
└── tests
    ├── .gitkeep
    └── fixtures
        ├── ai
        │   ├── ai_invalid_schema_output.json
        │   ├── ai_timeout_error.json
        │   └── ai_valid_output.json
        ├── expected
        │   ├── api_error_responses.json
        │   ├── generated_notes.json
        │   ├── ranking_results.json
        │   └── screening_decisions.json
        ├── kando
        │   ├── application_sources.json
        │   ├── applications.json
        │   ├── base_data
        │   │   ├── academic_fields.json
        │   │   ├── industries.json
        │   │   ├── job_categories.json
        │   │   ├── languages.json
        │   │   └── skill_levels.json
        │   ├── candidates.json
        │   ├── cvs.json
        │   ├── jobs.json
        │   ├── language_skills.json
        │   ├── university_degrees.json
        │   └── work_experiences.json
        ├── rulesets
        │   ├── customer_support_ruleset_v1.json
        │   └── customer_support_ruleset_with_ai_signals.json
        └── snapshots
            ├── application_snapshot_missing_birthdate.json
            ├── application_snapshot_missing_language.json
            ├── application_snapshot_unsupported_source.json
            └── application_snapshot_valid.json
```
