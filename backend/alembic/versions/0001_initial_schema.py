"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-13 00:00:00
"""

from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import UUID

from alembic import op
import sqlalchemy as sa
from sqlalchemy import column, table
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

internal_status_enum = postgresql.ENUM('NOT_REVIEWED', 'SMART_REJECTED', 'SMART_NOT_REJECTED', 'NEEDS_HUMAN_REVIEW', 'UNSUPPORTED_SOURCE', 'ERROR', 'SYNC_ERROR', name='internal_status', create_type=False)
priority_bucket_enum = postgresql.ENUM('HIGH', 'MEDIUM', 'LOW', 'REVIEW_UNKNOWN', name='priority_bucket', create_type=False)
ruleset_status_enum = postgresql.ENUM('DRAFT', 'ACTIVE', 'ARCHIVED', name='ruleset_status', create_type=False)
missing_data_policy_enum = postgresql.ENUM('NEEDS_REVIEW', 'REJECT', 'IGNORE', name='missing_data_policy', create_type=False)
ranking_scope_enum = postgresql.ENUM('JOB', 'JOB_AND_RUN', 'JOB_AND_RULESET', name='ranking_scope', create_type=False)
ai_analysis_status_enum = postgresql.ENUM('PENDING', 'RUNNING', 'SUCCEEDED', 'FAILED', 'SKIPPED', 'FAILED_SCHEMA_VALIDATION', 'FAILED_FINAL', name='ai_analysis_status', create_type=False)
actor_type_enum = postgresql.ENUM('USER', 'SYSTEM', 'WORKER', name='actor_type', create_type=False)
recruiter_decision_enum = postgresql.ENUM('RECRUITER_APPROVED_FOR_NEXT_STEP', 'RECRUITER_REJECTED', 'RECRUITER_NEEDS_MORE_INFO', 'RECRUITER_CONTACT_CANDIDATE', name='recruiter_decision', create_type=False)
note_type_enum = postgresql.ENUM('AI_SCREENING_NOTE', 'RECRUITER_NOTE', 'SYSTEM_NOTE', name='note_type', create_type=False)
rule_group_type_enum = postgresql.ENUM('GATE', 'OVERRIDE', 'SCORING', 'REVIEW', 'INFO', name='rule_group_type', create_type=False)
rule_type_enum = postgresql.ENUM('REJECT_GATE', 'PASS_GATE', 'OVERRIDE_PASS', 'NEEDS_REVIEW_GATE', 'SCORE_BONUS', 'SCORE_PENALTY', 'INFO_ONLY', name='rule_type', create_type=False)
rule_operator_enum = postgresql.ENUM('EXISTS', 'NOT_EXISTS', 'EQUALS', 'NOT_EQUALS', 'IN', 'NOT_IN', 'CONTAINS', 'NOT_CONTAINS', 'CONTAINS_ANY', 'FUZZY_MATCH', 'FUZZY_IN', 'REGEX_MATCH', 'GREATER_THAN', 'GREATER_THAN_OR_EQUAL', 'LESS_THAN', 'LESS_THAN_OR_EQUAL', 'BETWEEN', 'DURATION_AT_LEAST', name='rule_operator', create_type=False)

SEED_TIMESTAMP = datetime(2026, 6, 13, tzinfo=timezone.utc)
ROLE_ROWS = [
    {
        "id": UUID('9c2cf985-5410-5f97-84e0-052903ad85fc'),
        "code": 'SUPER_ADMIN',
        "name": 'Super Admin',
        "description": "Stable system role",
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "id": UUID('6c3c1b8f-e582-5fda-93ba-8830a34c8f7d'),
        "code": 'SYSTEM_ADMIN',
        "name": 'System Admin',
        "description": "Stable system role",
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "id": UUID('ffc8f043-c451-519f-93bd-1a7d51517267'),
        "code": 'HR_MANAGER',
        "name": 'Hr Manager',
        "description": "Stable system role",
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "id": UUID('17defcfb-06b5-50a6-9960-5e198e1f3b8d'),
        "code": 'RECRUITER',
        "name": 'Recruiter',
        "description": "Stable system role",
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "id": UUID('a4b9f076-c7df-5562-aae1-2cbaa273bf66'),
        "code": 'REVIEWER',
        "name": 'Reviewer',
        "description": "Stable system role",
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "id": UUID('486c5594-f1da-5221-bfaf-1938eb7c7d7d'),
        "code": 'READ_ONLY_AUDITOR',
        "name": 'Read Only Auditor',
        "description": "Stable system role",
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
]
PERMISSION_ROWS = [
    {
        "id": UUID('2ac3eb02-e868-5a99-8ba7-4877a9c33e34'),
        "code": 'view_applications',
        "name": 'View Applications',
        "description": "Stable system permission",
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "id": UUID('97e12c3e-d1ae-5273-b934-05a95397cac9'),
        "code": 'view_sensitive_contact',
        "name": 'View Sensitive Contact',
        "description": "Stable system permission",
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "id": UUID('d3c34988-c2aa-5264-a577-7d85b2b906dd'),
        "code": 'create_recruiter_note',
        "name": 'Create Recruiter Note',
        "description": "Stable system permission",
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "id": UUID('53d6867c-aedf-5929-b2b9-efdc6362392b'),
        "code": 'create_recruiter_decision',
        "name": 'Create Recruiter Decision',
        "description": "Stable system permission",
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "id": UUID('3047e47d-7242-5f6f-bf9d-41266ff72233'),
        "code": 'manage_ruleset_draft',
        "name": 'Manage Ruleset Draft',
        "description": "Stable system permission",
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "id": UUID('170c9e24-5ab9-5597-804e-014b5b7c94fc'),
        "code": 'activate_ruleset',
        "name": 'Activate Ruleset',
        "description": "Stable system permission",
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "id": UUID('0d24b7d6-c3b3-5faa-a59e-28aaf448f1bc'),
        "code": 'admin_reprocess',
        "name": 'Admin Reprocess',
        "description": "Stable system permission",
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "id": UUID('b40d7496-4929-52a5-a1ee-d4e1a48a6d0b'),
        "code": 'access_sqladmin',
        "name": 'Access Sqladmin',
        "description": "Stable system permission",
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "id": UUID('09bd416e-d6ca-57d7-99cf-e38d583354e4'),
        "code": 'view_raw_payload',
        "name": 'View Raw Payload',
        "description": "Stable system permission",
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "id": UUID('9b696f37-2d2c-54d3-8979-eaafb90eb234'),
        "code": 'view_ai_raw_output',
        "name": 'View Ai Raw Output',
        "description": "Stable system permission",
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "id": UUID('d72ff562-445f-5f14-bf4d-e9d34b0361d7'),
        "code": 'change_kando_settings',
        "name": 'Change Kando Settings',
        "description": "Stable system permission",
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
]
ROLE_PERMISSION_ROWS = [
    {
        "role_id": UUID('9c2cf985-5410-5f97-84e0-052903ad85fc'),
        "permission_id": UUID('2ac3eb02-e868-5a99-8ba7-4877a9c33e34'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('9c2cf985-5410-5f97-84e0-052903ad85fc'),
        "permission_id": UUID('97e12c3e-d1ae-5273-b934-05a95397cac9'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('9c2cf985-5410-5f97-84e0-052903ad85fc'),
        "permission_id": UUID('d3c34988-c2aa-5264-a577-7d85b2b906dd'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('9c2cf985-5410-5f97-84e0-052903ad85fc'),
        "permission_id": UUID('53d6867c-aedf-5929-b2b9-efdc6362392b'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('9c2cf985-5410-5f97-84e0-052903ad85fc'),
        "permission_id": UUID('3047e47d-7242-5f6f-bf9d-41266ff72233'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('9c2cf985-5410-5f97-84e0-052903ad85fc'),
        "permission_id": UUID('170c9e24-5ab9-5597-804e-014b5b7c94fc'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('9c2cf985-5410-5f97-84e0-052903ad85fc'),
        "permission_id": UUID('0d24b7d6-c3b3-5faa-a59e-28aaf448f1bc'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('9c2cf985-5410-5f97-84e0-052903ad85fc'),
        "permission_id": UUID('b40d7496-4929-52a5-a1ee-d4e1a48a6d0b'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('9c2cf985-5410-5f97-84e0-052903ad85fc'),
        "permission_id": UUID('09bd416e-d6ca-57d7-99cf-e38d583354e4'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('9c2cf985-5410-5f97-84e0-052903ad85fc'),
        "permission_id": UUID('9b696f37-2d2c-54d3-8979-eaafb90eb234'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('9c2cf985-5410-5f97-84e0-052903ad85fc'),
        "permission_id": UUID('d72ff562-445f-5f14-bf4d-e9d34b0361d7'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('6c3c1b8f-e582-5fda-93ba-8830a34c8f7d'),
        "permission_id": UUID('2ac3eb02-e868-5a99-8ba7-4877a9c33e34'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('6c3c1b8f-e582-5fda-93ba-8830a34c8f7d'),
        "permission_id": UUID('97e12c3e-d1ae-5273-b934-05a95397cac9'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('6c3c1b8f-e582-5fda-93ba-8830a34c8f7d'),
        "permission_id": UUID('d3c34988-c2aa-5264-a577-7d85b2b906dd'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('6c3c1b8f-e582-5fda-93ba-8830a34c8f7d'),
        "permission_id": UUID('53d6867c-aedf-5929-b2b9-efdc6362392b'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('6c3c1b8f-e582-5fda-93ba-8830a34c8f7d'),
        "permission_id": UUID('3047e47d-7242-5f6f-bf9d-41266ff72233'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('6c3c1b8f-e582-5fda-93ba-8830a34c8f7d'),
        "permission_id": UUID('170c9e24-5ab9-5597-804e-014b5b7c94fc'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('6c3c1b8f-e582-5fda-93ba-8830a34c8f7d'),
        "permission_id": UUID('0d24b7d6-c3b3-5faa-a59e-28aaf448f1bc'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('6c3c1b8f-e582-5fda-93ba-8830a34c8f7d'),
        "permission_id": UUID('b40d7496-4929-52a5-a1ee-d4e1a48a6d0b'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('6c3c1b8f-e582-5fda-93ba-8830a34c8f7d'),
        "permission_id": UUID('09bd416e-d6ca-57d7-99cf-e38d583354e4'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('6c3c1b8f-e582-5fda-93ba-8830a34c8f7d'),
        "permission_id": UUID('9b696f37-2d2c-54d3-8979-eaafb90eb234'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('6c3c1b8f-e582-5fda-93ba-8830a34c8f7d'),
        "permission_id": UUID('d72ff562-445f-5f14-bf4d-e9d34b0361d7'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('ffc8f043-c451-519f-93bd-1a7d51517267'),
        "permission_id": UUID('2ac3eb02-e868-5a99-8ba7-4877a9c33e34'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('ffc8f043-c451-519f-93bd-1a7d51517267'),
        "permission_id": UUID('97e12c3e-d1ae-5273-b934-05a95397cac9'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('ffc8f043-c451-519f-93bd-1a7d51517267'),
        "permission_id": UUID('d3c34988-c2aa-5264-a577-7d85b2b906dd'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('ffc8f043-c451-519f-93bd-1a7d51517267'),
        "permission_id": UUID('53d6867c-aedf-5929-b2b9-efdc6362392b'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('ffc8f043-c451-519f-93bd-1a7d51517267'),
        "permission_id": UUID('3047e47d-7242-5f6f-bf9d-41266ff72233'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('ffc8f043-c451-519f-93bd-1a7d51517267'),
        "permission_id": UUID('170c9e24-5ab9-5597-804e-014b5b7c94fc'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('17defcfb-06b5-50a6-9960-5e198e1f3b8d'),
        "permission_id": UUID('2ac3eb02-e868-5a99-8ba7-4877a9c33e34'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('17defcfb-06b5-50a6-9960-5e198e1f3b8d'),
        "permission_id": UUID('d3c34988-c2aa-5264-a577-7d85b2b906dd'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('17defcfb-06b5-50a6-9960-5e198e1f3b8d'),
        "permission_id": UUID('53d6867c-aedf-5929-b2b9-efdc6362392b'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('a4b9f076-c7df-5562-aae1-2cbaa273bf66'),
        "permission_id": UUID('2ac3eb02-e868-5a99-8ba7-4877a9c33e34'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('a4b9f076-c7df-5562-aae1-2cbaa273bf66'),
        "permission_id": UUID('d3c34988-c2aa-5264-a577-7d85b2b906dd'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('a4b9f076-c7df-5562-aae1-2cbaa273bf66'),
        "permission_id": UUID('53d6867c-aedf-5929-b2b9-efdc6362392b'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
    {
        "role_id": UUID('486c5594-f1da-5221-bfaf-1938eb7c7d7d'),
        "permission_id": UUID('2ac3eb02-e868-5a99-8ba7-4877a9c33e34'),
        "created_at": SEED_TIMESTAMP,
        "updated_at": SEED_TIMESTAMP,
    },
]

def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    internal_status_enum.create(op.get_bind(), checkfirst=True)
    priority_bucket_enum.create(op.get_bind(), checkfirst=True)
    ruleset_status_enum.create(op.get_bind(), checkfirst=True)
    missing_data_policy_enum.create(op.get_bind(), checkfirst=True)
    ranking_scope_enum.create(op.get_bind(), checkfirst=True)
    ai_analysis_status_enum.create(op.get_bind(), checkfirst=True)
    actor_type_enum.create(op.get_bind(), checkfirst=True)
    recruiter_decision_enum.create(op.get_bind(), checkfirst=True)
    note_type_enum.create(op.get_bind(), checkfirst=True)
    rule_group_type_enum.create(op.get_bind(), checkfirst=True)
    rule_type_enum.create(op.get_bind(), checkfirst=True)
    rule_operator_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'integration_errors',
        sa.Column('source', sa.String(length=80), nullable=False),
        sa.Column('error_code', sa.String(length=120), nullable=False),
        sa.Column('message_fa', sa.Text(), nullable=False),
        sa.Column('retryable', sa.Boolean(), nullable=False),
        sa.Column('context_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_integration_errors'),
    )
    op.create_index('ix_integration_errors_source_created', 'integration_errors', ['source', 'created_at'])

    op.create_table(
        'kando_api_call_logs',
        sa.Column('method', sa.String(length=12), nullable=False),
        sa.Column('endpoint', sa.String(length=500), nullable=False),
        sa.Column('status_code', sa.Integer()),
        sa.Column('duration_ms', sa.Integer()),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('error_code', sa.String(length=120)),
        sa.Column('message_fa', sa.Text()),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_kando_api_call_logs'),
    )

    op.create_table(
        'kando_application_sources',
        sa.Column('kando_application_source_id', sa.Integer()),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_kando_application_sources'),
        sa.UniqueConstraint('kando_application_source_id', name='uq_kando_application_sources_kando_application_source_id'),
    )

    op.create_table(
        'kando_base_data_cache',
        sa.Column('data_type', sa.String(length=120), nullable=False),
        sa.Column('external_id', sa.Integer(), nullable=False),
        sa.Column('display_name', sa.String(length=255)),
        sa.Column('payload_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_kando_base_data_cache'),
        sa.UniqueConstraint('data_type', 'external_id', name='uq_kando_base_data_type_id'),
    )

    op.create_table(
        'kando_connections',
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('ats_base_url', sa.String(length=500), nullable=False),
        sa.Column('basedata_base_url', sa.String(length=500)),
        sa.Column('api_header_key', sa.String(length=120)),
        sa.Column('encrypted_api_key', sa.Text()),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_kando_connections'),
    )

    op.create_table(
        'kando_hire_steps',
        sa.Column('kando_hire_step_id', sa.Integer(), nullable=False),
        sa.Column('kando_job_id', sa.Integer()),
        sa.Column('name', sa.String(length=255)),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_kando_hire_steps'),
        sa.UniqueConstraint('kando_hire_step_id', name='uq_kando_hire_steps_kando_hire_step_id'),
    )

    op.create_table(
        'kando_raw_payloads',
        sa.Column('source', sa.String(length=80), nullable=False),
        sa.Column('external_id', sa.Integer()),
        sa.Column('payload_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('payload_hash', sa.String(length=128)),
        sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_kando_raw_payloads'),
    )

    op.create_table(
        'kando_sync_states',
        sa.Column('sync_name', sa.String(length=120), nullable=False),
        sa.Column('last_success_at', sa.DateTime(timezone=True)),
        sa.Column('last_attempt_at', sa.DateTime(timezone=True)),
        sa.Column('cursor_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_kando_sync_states'),
        sa.UniqueConstraint('sync_name', name='uq_kando_sync_states_sync_name'),
    )

    op.create_table(
        'permissions',
        sa.Column('code', sa.String(length=120), nullable=False),
        sa.Column('name', sa.String(length=160), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_permissions'),
        sa.UniqueConstraint('code', name='uq_permissions_code'),
    )

    op.create_table(
        'roles',
        sa.Column('code', sa.String(length=80), nullable=False),
        sa.Column('name', sa.String(length=160), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_roles'),
        sa.UniqueConstraint('code', name='uq_roles_code'),
    )

    op.create_table(
        'screening_applications',
        sa.Column('kando_application_id', sa.Integer(), nullable=False),
        sa.Column('kando_candidate_id', sa.Integer(), nullable=False),
        sa.Column('kando_cv_id', sa.Integer()),
        sa.Column('kando_job_id', sa.Integer(), nullable=False),
        sa.Column('candidate_full_name', sa.String(length=255)),
        sa.Column('source_name', sa.String(length=255)),
        sa.Column('kando_hire_step_id', sa.Integer()),
        sa.Column('kando_status_id', sa.Integer()),
        sa.Column('internal_status', internal_status_enum, nullable=False),
        sa.Column('priority_score', sa.Integer()),
        sa.Column('priority_bucket', priority_bucket_enum),
        sa.Column('rank_in_job', sa.Integer()),
        sa.Column('snapshot_hash', sa.String(length=128)),
        sa.Column('raw_snapshot_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('last_synced_at', sa.DateTime(timezone=True)),
        sa.Column('last_screened_at', sa.DateTime(timezone=True)),
        sa.Column('last_ranked_at', sa.DateTime(timezone=True)),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('priority_score IS NULL OR (priority_score >= 0 AND priority_score <= 100)', name='ck_screening_applications_priority_score_range'),
        sa.PrimaryKeyConstraint('id', name='pk_screening_applications'),
    )
    op.create_index('ix_screening_applications_bucket_score', 'screening_applications', ['priority_bucket', 'priority_score'])
    op.create_index('ix_screening_applications_job_status', 'screening_applications', ['kando_job_id', 'internal_status'])
    op.create_index('ix_screening_applications_snapshot_hash', 'screening_applications', ['snapshot_hash'])
    op.create_index('uq_screening_applications_latest_kando_application', 'screening_applications', ['kando_application_id'], unique=True)

    op.create_table(
        'screening_rulesets',
        sa.Column('kando_job_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', ruleset_status_enum, nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('default_missing_data_policy', missing_data_policy_enum, nullable=False),
        sa.Column('scoring_enabled', sa.Boolean(), nullable=False),
        sa.Column('max_score', sa.Integer(), nullable=False),
        sa.Column('ranking_scope', ranking_scope_enum, nullable=False),
        sa.Column('config_hash', sa.String(length=128)),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('max_score > 0', name='ck_screening_rulesets_ruleset_max_score_positive'),
        sa.CheckConstraint('version > 0', name='ck_screening_rulesets_ruleset_version_positive'),
        sa.PrimaryKeyConstraint('id', name='pk_screening_rulesets'),
    )
    op.create_index('uq_screening_rulesets_active_per_job', 'screening_rulesets', ['kando_job_id'], unique=True, postgresql_where=sa.text('is_active'))

    op.create_table(
        'users',
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255)),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True)),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_users'),
        sa.UniqueConstraint('email', name='uq_users_email'),
    )

    op.create_table(
        'worker_task_logs',
        sa.Column('task_name', sa.String(length=160), nullable=False),
        sa.Column('task_id', sa.String(length=160)),
        sa.Column('status', sa.String(length=80), nullable=False),
        sa.Column('queue_name', sa.String(length=80)),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('error_code', sa.String(length=120)),
        sa.Column('message_fa', sa.Text()),
        sa.Column('payload_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_worker_task_logs'),
    )

    op.create_table(
        'ai_analysis_runs',
        sa.Column('screening_application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ruleset_id', postgresql.UUID(as_uuid=True)),
        sa.Column('ruleset_version', sa.Integer()),
        sa.Column('provider', sa.String(length=120), nullable=False),
        sa.Column('model_name', sa.String(length=160), nullable=False),
        sa.Column('prompt_version', sa.String(length=80), nullable=False),
        sa.Column('input_hash', sa.String(length=128), nullable=False),
        sa.Column('status', ai_analysis_status_enum, nullable=False),
        sa.Column('error_code', sa.String(length=120)),
        sa.Column('error_message_fa', sa.Text()),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('error_code IS NULL OR error_message_fa IS NOT NULL', name='ck_ai_analysis_runs_ai_error_message_fa_required'),
        sa.ForeignKeyConstraint(['screening_application_id'], ['screening_applications.id'], name='fk_ai_analysis_runs_screening_application_id_screening_c15aa031', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_ai_analysis_runs'),
    )
    op.create_index('ix_ai_analysis_runs_application_status', 'ai_analysis_runs', ['screening_application_id', 'status'])

    op.create_table(
        'audit_logs',
        sa.Column('actor_user_id', postgresql.UUID(as_uuid=True)),
        sa.Column('actor_type', actor_type_enum, nullable=False),
        sa.Column('action', sa.String(length=160), nullable=False),
        sa.Column('entity_type', sa.String(length=160), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True)),
        sa.Column('before_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('after_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('ip_address', sa.String(length=80)),
        sa.Column('user_agent', sa.Text()),
        sa.Column('request_id', sa.String(length=80)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['actor_user_id'], ['users.id'], name='fk_audit_logs_actor_user_id_users'),
        sa.PrimaryKeyConstraint('id', name='pk_audit_logs'),
    )
    op.create_index('ix_audit_logs_actor_created', 'audit_logs', ['actor_user_id', 'created_at'])

    op.create_table(
        'kando_applications',
        sa.Column('kando_application_id', sa.Integer(), nullable=False),
        sa.Column('kando_candidate_id', sa.Integer(), nullable=False),
        sa.Column('kando_cv_id', sa.Integer()),
        sa.Column('kando_job_id', sa.Integer(), nullable=False),
        sa.Column('kando_hire_step_id', sa.Integer()),
        sa.Column('kando_status_id', sa.Integer()),
        sa.Column('source_name', sa.String(length=255)),
        sa.Column('raw_payload_id', postgresql.UUID(as_uuid=True)),
        sa.Column('last_synced_at', sa.DateTime(timezone=True)),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['raw_payload_id'], ['kando_raw_payloads.id'], name='fk_kando_applications_raw_payload_id_kando_raw_payloads'),
        sa.PrimaryKeyConstraint('id', name='pk_kando_applications'),
        sa.UniqueConstraint('kando_application_id', name='uq_kando_applications_kando_application_id'),
    )

    op.create_table(
        'kando_candidates',
        sa.Column('kando_candidate_id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(length=255)),
        sa.Column('raw_payload_id', postgresql.UUID(as_uuid=True)),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['raw_payload_id'], ['kando_raw_payloads.id'], name='fk_kando_candidates_raw_payload_id_kando_raw_payloads'),
        sa.PrimaryKeyConstraint('id', name='pk_kando_candidates'),
        sa.UniqueConstraint('kando_candidate_id', name='uq_kando_candidates_kando_candidate_id'),
    )

    op.create_table(
        'kando_cvs',
        sa.Column('kando_cv_id', sa.Integer(), nullable=False),
        sa.Column('kando_candidate_id', sa.Integer()),
        sa.Column('raw_payload_id', postgresql.UUID(as_uuid=True)),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['raw_payload_id'], ['kando_raw_payloads.id'], name='fk_kando_cvs_raw_payload_id_kando_raw_payloads'),
        sa.PrimaryKeyConstraint('id', name='pk_kando_cvs'),
        sa.UniqueConstraint('kando_cv_id', name='uq_kando_cvs_kando_cv_id'),
    )

    op.create_table(
        'kando_jobs',
        sa.Column('kando_job_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255)),
        sa.Column('raw_payload_id', postgresql.UUID(as_uuid=True)),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['raw_payload_id'], ['kando_raw_payloads.id'], name='fk_kando_jobs_raw_payload_id_kando_raw_payloads'),
        sa.PrimaryKeyConstraint('id', name='pk_kando_jobs'),
        sa.UniqueConstraint('kando_job_id', name='uq_kando_jobs_kando_job_id'),
    )

    op.create_table(
        'ranking_results',
        sa.Column('screening_application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('kando_job_id', sa.Integer(), nullable=False),
        sa.Column('rank_in_job', sa.Integer()),
        sa.Column('priority_bucket', priority_bucket_enum),
        sa.Column('score', sa.Integer()),
        sa.Column('ranking_scope', sa.String(length=80)),
        sa.Column('score_breakdown_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['screening_application_id'], ['screening_applications.id'], name='fk_ranking_results_screening_application_id_screening__8b136967', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_ranking_results'),
    )

    op.create_table(
        'recruiter_decisions',
        sa.Column('screening_application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recruiter_user_id', postgresql.UUID(as_uuid=True)),
        sa.Column('decision', recruiter_decision_enum, nullable=False),
        sa.Column('note_fa', sa.Text()),
        sa.Column('reason_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['screening_application_id'], ['screening_applications.id'], name='fk_recruiter_decisions_screening_application_id_screen_bdb595f8', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_recruiter_decisions'),
    )

    op.create_table(
        'role_permissions',
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('permission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], name='fk_role_permissions_permission_id_permissions', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name='fk_role_permissions_role_id_roles', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id', name='pk_role_permissions'),
        sa.UniqueConstraint('role_id', 'permission_id', name='uq_role_permissions_role_permission'),
    )

    op.create_table(
        'screening_decisions',
        sa.Column('screening_application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('internal_status', internal_status_enum, nullable=False),
        sa.Column('ruleset_id', postgresql.UUID(as_uuid=True)),
        sa.Column('ruleset_version', sa.Integer()),
        sa.Column('reasons_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('message_fa', sa.Text()),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['screening_application_id'], ['screening_applications.id'], name='fk_screening_decisions_screening_application_id_screen_2aeb8f01', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_screening_decisions'),
    )
    op.create_index('ix_screening_decisions_application_created', 'screening_decisions', ['screening_application_id', 'created_at'])

    op.create_table(
        'screening_notes',
        sa.Column('screening_application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('note_type', note_type_enum, nullable=False),
        sa.Column('note_fa', sa.Text(), nullable=False),
        sa.Column('author_user_id', postgresql.UUID(as_uuid=True)),
        sa.Column('note_metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['screening_application_id'], ['screening_applications.id'], name='fk_screening_notes_screening_application_id_screening__53f26eb7', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_screening_notes'),
    )

    op.create_table(
        'screening_rule_groups',
        sa.Column('ruleset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('group_type', rule_group_type_enum, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['ruleset_id'], ['screening_rulesets.id'], name='fk_screening_rule_groups_ruleset_id_screening_rulesets', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_screening_rule_groups'),
    )

    op.create_table(
        'screening_runs',
        sa.Column('ruleset_id', postgresql.UUID(as_uuid=True)),
        sa.Column('ruleset_version', sa.Integer()),
        sa.Column('status', sa.String(length=80), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('run_context_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['ruleset_id'], ['screening_rulesets.id'], name='fk_screening_runs_ruleset_id_screening_rulesets'),
        sa.PrimaryKeyConstraint('id', name='pk_screening_runs'),
    )

    op.create_table(
        'screening_scores',
        sa.Column('screening_application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('score_breakdown_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('ruleset_id', postgresql.UUID(as_uuid=True)),
        sa.Column('ruleset_version', sa.Integer()),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('score >= 0 AND score <= 100', name='ck_screening_scores_screening_score_range'),
        sa.ForeignKeyConstraint(['screening_application_id'], ['screening_applications.id'], name='fk_screening_scores_screening_application_id_screening_d382e4ce', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_screening_scores'),
    )
    op.create_index('ix_screening_scores_application_created', 'screening_scores', ['screening_application_id', 'created_at'])

    op.create_table(
        'user_roles',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name='fk_user_roles_role_id_roles', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_roles_user_id_users', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role_id', name='pk_user_roles'),
        sa.UniqueConstraint('user_id', 'role_id', name='uq_user_roles_user_role'),
    )

    op.create_table(
        'ai_analysis_results',
        sa.Column('ai_analysis_run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('output_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('normalized_signals_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('confidence', sa.Float()),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('confidence IS NULL OR (confidence >= 0 AND confidence <= 1)', name='ck_ai_analysis_results_confidence_range'),
        sa.ForeignKeyConstraint(['ai_analysis_run_id'], ['ai_analysis_runs.id'], name='fk_ai_analysis_results_ai_analysis_run_id_ai_analysis_runs', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_ai_analysis_results'),
    )

    op.create_table(
        'kando_cv_language_skills',
        sa.Column('kando_cv_id', sa.Integer(), nullable=False),
        sa.Column('cv_id', postgresql.UUID(as_uuid=True)),
        sa.Column('language_id', sa.Integer()),
        sa.Column('skill_level_id', sa.Integer()),
        sa.Column('payload_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['cv_id'], ['kando_cvs.id'], name='fk_kando_cv_language_skills_cv_id_kando_cvs', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_kando_cv_language_skills'),
    )

    op.create_table(
        'kando_cv_university_degrees',
        sa.Column('kando_cv_id', sa.Integer(), nullable=False),
        sa.Column('cv_id', postgresql.UUID(as_uuid=True)),
        sa.Column('degree_name', sa.String(length=255)),
        sa.Column('university_name', sa.String(length=255)),
        sa.Column('payload_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['cv_id'], ['kando_cvs.id'], name='fk_kando_cv_university_degrees_cv_id_kando_cvs', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_kando_cv_university_degrees'),
    )

    op.create_table(
        'kando_cv_work_experiences',
        sa.Column('kando_cv_id', sa.Integer(), nullable=False),
        sa.Column('cv_id', postgresql.UUID(as_uuid=True)),
        sa.Column('title', sa.String(length=255)),
        sa.Column('company_name', sa.String(length=255)),
        sa.Column('payload_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['cv_id'], ['kando_cvs.id'], name='fk_kando_cv_work_experiences_cv_id_kando_cvs', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_kando_cv_work_experiences'),
    )

    op.create_table(
        'screening_rules',
        sa.Column('group_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rule_type', rule_type_enum, nullable=False),
        sa.Column('field_path', sa.String(length=255), nullable=False),
        sa.Column('operator', rule_operator_enum, nullable=False),
        sa.Column('value_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('score_delta', sa.Integer()),
        sa.Column('reason_code', sa.String(length=120)),
        sa.Column('message_fa', sa.Text()),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['screening_rule_groups.id'], name='fk_screening_rules_group_id_screening_rule_groups', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_screening_rules'),
    )

    op.create_table(
        'screening_run_items',
        sa.Column('screening_run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('screening_application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=80), nullable=False),
        sa.Column('result_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['screening_application_id'], ['screening_applications.id'], name='fk_screening_run_items_screening_application_id_screen_d601abca', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['screening_run_id'], ['screening_runs.id'], name='fk_screening_run_items_screening_run_id_screening_runs', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_screening_run_items'),
    )

    op.create_table(
        'screening_rule_terms',
        sa.Column('rule_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('field_path', sa.String(length=255), nullable=False),
        sa.Column('operator', rule_operator_enum, nullable=False),
        sa.Column('value_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['rule_id'], ['screening_rules.id'], name='fk_screening_rule_terms_rule_id_screening_rules', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_screening_rule_terms'),
    )

    _seed_roles_permissions()


def downgrade() -> None:
    _delete_seed_roles_permissions()

    op.drop_table('screening_rule_terms')
    op.drop_table('screening_run_items')
    op.drop_table('screening_rules')
    op.drop_table('kando_cv_work_experiences')
    op.drop_table('kando_cv_university_degrees')
    op.drop_table('kando_cv_language_skills')
    op.drop_table('ai_analysis_results')
    op.drop_table('user_roles')
    op.drop_table('screening_scores')
    op.drop_table('screening_runs')
    op.drop_table('screening_rule_groups')
    op.drop_table('screening_notes')
    op.drop_table('screening_decisions')
    op.drop_table('role_permissions')
    op.drop_table('recruiter_decisions')
    op.drop_table('ranking_results')
    op.drop_table('kando_jobs')
    op.drop_table('kando_cvs')
    op.drop_table('kando_candidates')
    op.drop_table('kando_applications')
    op.drop_table('audit_logs')
    op.drop_table('ai_analysis_runs')
    op.drop_table('worker_task_logs')
    op.drop_table('users')
    op.drop_table('screening_rulesets')
    op.drop_table('screening_applications')
    op.drop_table('roles')
    op.drop_table('permissions')
    op.drop_table('kando_sync_states')
    op.drop_table('kando_raw_payloads')
    op.drop_table('kando_hire_steps')
    op.drop_table('kando_connections')
    op.drop_table('kando_base_data_cache')
    op.drop_table('kando_application_sources')
    op.drop_table('kando_api_call_logs')
    op.drop_table('integration_errors')

    op.execute("DROP TYPE IF EXISTS rule_operator")
    op.execute("DROP TYPE IF EXISTS rule_type")
    op.execute("DROP TYPE IF EXISTS rule_group_type")
    op.execute("DROP TYPE IF EXISTS note_type")
    op.execute("DROP TYPE IF EXISTS recruiter_decision")
    op.execute("DROP TYPE IF EXISTS actor_type")
    op.execute("DROP TYPE IF EXISTS ai_analysis_status")
    op.execute("DROP TYPE IF EXISTS ranking_scope")
    op.execute("DROP TYPE IF EXISTS missing_data_policy")
    op.execute("DROP TYPE IF EXISTS ruleset_status")
    op.execute("DROP TYPE IF EXISTS priority_bucket")
    op.execute("DROP TYPE IF EXISTS internal_status")


def _seed_roles_permissions() -> None:
    roles_table = table(
        "roles",
        column('id', postgresql.UUID(as_uuid=True)),
        column('code', sa.String()),
        column('name', sa.String()),
        column('description', sa.Text()),
        column('created_at', sa.DateTime(timezone=True)),
        column('updated_at', sa.DateTime(timezone=True)),
    )
    permissions_table = table(
        "permissions",
        column('id', postgresql.UUID(as_uuid=True)),
        column('code', sa.String()),
        column('name', sa.String()),
        column('description', sa.Text()),
        column('created_at', sa.DateTime(timezone=True)),
        column('updated_at', sa.DateTime(timezone=True)),
    )
    role_permissions_table = table(
        "role_permissions",
        column('role_id', postgresql.UUID(as_uuid=True)),
        column('permission_id', postgresql.UUID(as_uuid=True)),
        column('created_at', sa.DateTime(timezone=True)),
        column('updated_at', sa.DateTime(timezone=True)),
    )
    op.bulk_insert(roles_table, ROLE_ROWS)
    op.bulk_insert(permissions_table, PERMISSION_ROWS)
    op.bulk_insert(role_permissions_table, ROLE_PERMISSION_ROWS)


def _delete_seed_roles_permissions() -> None:
    op.execute(
        "DELETE FROM role_permissions "
        "WHERE role_id IN (SELECT id FROM roles WHERE code IN "
        "('SUPER_ADMIN', 'SYSTEM_ADMIN', 'HR_MANAGER', 'RECRUITER', 'REVIEWER', 'READ_ONLY_AUDITOR')) "
        "OR permission_id IN (SELECT id FROM permissions WHERE code IN "
        "('view_applications', 'view_sensitive_contact', 'create_recruiter_note', 'create_recruiter_decision', 'manage_ruleset_draft', 'activate_ruleset', 'admin_reprocess', 'access_sqladmin', 'view_raw_payload', 'view_ai_raw_output', 'change_kando_settings'))"
    )
    op.execute("DELETE FROM permissions WHERE code IN ('view_applications', 'view_sensitive_contact', 'create_recruiter_note', 'create_recruiter_decision', 'manage_ruleset_draft', 'activate_ruleset', 'admin_reprocess', 'access_sqladmin', 'view_raw_payload', 'view_ai_raw_output', 'change_kando_settings')")
    op.execute("DELETE FROM roles WHERE code IN ('SUPER_ADMIN', 'SYSTEM_ADMIN', 'HR_MANAGER', 'RECRUITER', 'REVIEWER', 'READ_ONLY_AUDITOR')")

