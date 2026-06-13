from __future__ import annotations

from typing import Any

from fastapi import Request
from sqladmin import ModelView
from sqlalchemy import select

from app.admin.audit import model_snapshot, record_admin_audit
from app.admin.masking import format_masked_json, format_masked_secret
from app.admin.security import request_has_write_access, request_sqladmin_roles
from app.models.ai import AIAnalysisResult, AIAnalysisRun
from app.models.audit import AuditLog, IntegrationError, WorkerTaskLog
from app.models.identity import Permission, Role, RolePermission, User, UserRole
from app.models.kando import (
    KandoApiCallLog,
    KandoApplication,
    KandoApplicationSource,
    KandoBaseDataCache,
    KandoCandidate,
    KandoConnection,
    KandoCv,
    KandoCvLanguageSkill,
    KandoCvUniversityDegree,
    KandoCvWorkExperience,
    KandoHireStep,
    KandoJob,
    KandoRawPayload,
    KandoSyncState,
)
from app.models.notes import RecruiterDecisionRecord, ScreeningNote
from app.models.ranking import RankingResult, ScreeningScore
from app.models.screening import (
    ScreeningApplication,
    ScreeningDecision,
    ScreeningRule,
    ScreeningRuleGroup,
    ScreeningRuleSet,
    ScreeningRuleTerm,
    ScreeningRun,
    ScreeningRunItem,
)


class SmartHireAdminView(ModelView):
    page_size = 50
    page_size_options = [25, 50, 100]
    can_view_details = True
    can_export = False

    async def is_accessible(self, request: Request) -> bool:
        return bool(request_sqladmin_roles(request))


class ReadOnlyAdminView(SmartHireAdminView):
    can_create = False
    can_edit = False
    can_delete = False


class TechnicalEditableAdminView(SmartHireAdminView):
    can_create = True
    can_edit = True
    can_delete = True

    async def is_accessible(self, request: Request) -> bool:
        return request_has_write_access(request)

    async def on_model_change(
        self,
        data: dict[str, Any],
        model: Any,
        is_created: bool,
        request: Request,
    ) -> None:
        action = "SQLADMIN_CREATE" if is_created else "SQLADMIN_UPDATE"
        record_admin_audit(request, action=action, model=model, after_json=model_snapshot(model))

    async def after_model_delete(self, model: Any, request: Request) -> None:
        record_admin_audit(request, action="SQLADMIN_DELETE", model=model, before_json=model_snapshot(model))


class DraftRuleEditableView(TechnicalEditableAdminView):
    async def _is_draft_rule_entity(self, model: Any, request: Request) -> bool:
        if isinstance(model, ScreeningRuleSet):
            return str(model.status) == "DRAFT" and not bool(model.is_active)
        ruleset_id = getattr(model, "ruleset_id", None)
        group_id = getattr(model, "group_id", None)
        rule_id = getattr(model, "rule_id", None)
        session = request.state.session if hasattr(request.state, "session") else None
        if session is None:
            return True
        if ruleset_id:
            ruleset = session.get(ScreeningRuleSet, ruleset_id)
            return ruleset is not None and str(ruleset.status) == "DRAFT" and not ruleset.is_active
        if group_id:
            group = session.get(ScreeningRuleGroup, group_id)
            if group is None:
                return False
            ruleset = session.get(ScreeningRuleSet, group.ruleset_id)
            return ruleset is not None and str(ruleset.status) == "DRAFT" and not ruleset.is_active
        if rule_id:
            rule = session.get(ScreeningRule, rule_id)
            if rule is None:
                return False
            group = session.get(ScreeningRuleGroup, rule.group_id)
            if group is None:
                return False
            ruleset = session.get(ScreeningRuleSet, group.ruleset_id)
            return ruleset is not None and str(ruleset.status) == "DRAFT" and not ruleset.is_active
        return True


class UserAdmin(TechnicalEditableAdminView, model=User):
    name = "User"
    name_plural = "Users"
    column_list = [User.id, User.email, User.full_name, User.is_active, User.last_login_at]
    column_searchable_list = [User.email, User.full_name]
    column_sortable_list = [User.email, User.created_at, User.last_login_at]
    form_excluded_columns = [User.password_hash]


class RoleAdmin(TechnicalEditableAdminView, model=Role):
    column_list = [Role.id, Role.code, Role.name, Role.description]
    column_searchable_list = [Role.code, Role.name]
    column_sortable_list = [Role.code, Role.name, Role.created_at]


class PermissionAdmin(TechnicalEditableAdminView, model=Permission):
    column_list = [Permission.id, Permission.code, Permission.name, Permission.description]
    column_searchable_list = [Permission.code, Permission.name]
    column_sortable_list = [Permission.code, Permission.name]


class UserRoleAdmin(TechnicalEditableAdminView, model=UserRole):
    column_list = [UserRole.user_id, UserRole.role_id, UserRole.created_at]
    column_sortable_list = [UserRole.user_id, UserRole.role_id, UserRole.created_at]


class RolePermissionAdmin(TechnicalEditableAdminView, model=RolePermission):
    column_list = [RolePermission.role_id, RolePermission.permission_id, RolePermission.created_at]
    column_sortable_list = [RolePermission.role_id, RolePermission.permission_id, RolePermission.created_at]


class KandoConnectionAdmin(TechnicalEditableAdminView, model=KandoConnection):
    column_list = [
        KandoConnection.id,
        KandoConnection.name,
        KandoConnection.ats_base_url,
        KandoConnection.basedata_base_url,
        KandoConnection.api_header_key,
        KandoConnection.encrypted_api_key,
        KandoConnection.is_active,
    ]
    column_searchable_list = [KandoConnection.name, KandoConnection.ats_base_url]
    column_sortable_list = [KandoConnection.name, KandoConnection.is_active, KandoConnection.created_at]
    column_formatters = {"encrypted_api_key": format_masked_secret}
    form_excluded_columns = [KandoConnection.encrypted_api_key]
    column_details_exclude_list = [KandoConnection.encrypted_api_key]
    column_export_exclude_list = [KandoConnection.encrypted_api_key]


class ScreeningRuleSetAdmin(DraftRuleEditableView, model=ScreeningRuleSet):
    column_list = [
        ScreeningRuleSet.id,
        ScreeningRuleSet.kando_job_id,
        ScreeningRuleSet.name,
        ScreeningRuleSet.version,
        ScreeningRuleSet.status,
        ScreeningRuleSet.is_active,
    ]
    column_searchable_list = [ScreeningRuleSet.name]
    column_sortable_list = [ScreeningRuleSet.kando_job_id, ScreeningRuleSet.version, ScreeningRuleSet.status]


class ScreeningRuleGroupAdmin(DraftRuleEditableView, model=ScreeningRuleGroup):
    column_list = [
        ScreeningRuleGroup.id,
        ScreeningRuleGroup.ruleset_id,
        ScreeningRuleGroup.group_type,
        ScreeningRuleGroup.name,
        ScreeningRuleGroup.sort_order,
        ScreeningRuleGroup.is_enabled,
    ]
    column_searchable_list = [ScreeningRuleGroup.name]
    column_sortable_list = [ScreeningRuleGroup.ruleset_id, ScreeningRuleGroup.sort_order]


class ScreeningRuleAdmin(DraftRuleEditableView, model=ScreeningRule):
    column_list = [
        ScreeningRule.id,
        ScreeningRule.group_id,
        ScreeningRule.rule_type,
        ScreeningRule.field_path,
        ScreeningRule.operator,
        ScreeningRule.score_delta,
        ScreeningRule.is_enabled,
    ]
    column_searchable_list = [ScreeningRule.field_path, ScreeningRule.reason_code, ScreeningRule.message_fa]
    column_sortable_list = [ScreeningRule.group_id, ScreeningRule.sort_order, ScreeningRule.rule_type]


class ScreeningRuleTermAdmin(DraftRuleEditableView, model=ScreeningRuleTerm):
    column_list = [
        ScreeningRuleTerm.id,
        ScreeningRuleTerm.rule_id,
        ScreeningRuleTerm.field_path,
        ScreeningRuleTerm.operator,
    ]
    column_searchable_list = [ScreeningRuleTerm.field_path]
    column_sortable_list = [ScreeningRuleTerm.rule_id, ScreeningRuleTerm.field_path]


class KandoRawPayloadAdmin(ReadOnlyAdminView, model=KandoRawPayload):
    column_list = [KandoRawPayload.id, KandoRawPayload.source, KandoRawPayload.external_id, KandoRawPayload.received_at]
    column_searchable_list = [KandoRawPayload.source, KandoRawPayload.payload_hash]
    column_sortable_list = [KandoRawPayload.source, KandoRawPayload.external_id, KandoRawPayload.received_at]
    column_formatters = {"payload_json": format_masked_json}
    column_export_exclude_list = [KandoRawPayload.payload_json]


class KandoJobAdmin(ReadOnlyAdminView, model=KandoJob):
    column_list = [KandoJob.id, KandoJob.kando_job_id, KandoJob.title, KandoJob.created_at]
    column_searchable_list = [KandoJob.title]
    column_sortable_list = [KandoJob.kando_job_id, KandoJob.title, KandoJob.created_at]


class KandoApplicationAdmin(ReadOnlyAdminView, model=KandoApplication):
    column_list = [
        KandoApplication.id,
        KandoApplication.kando_application_id,
        KandoApplication.kando_candidate_id,
        KandoApplication.kando_cv_id,
        KandoApplication.kando_job_id,
        KandoApplication.source_name,
        KandoApplication.last_synced_at,
    ]
    column_searchable_list = [KandoApplication.source_name]
    column_sortable_list = [
        KandoApplication.kando_application_id,
        KandoApplication.kando_job_id,
        KandoApplication.last_synced_at,
    ]


class KandoCandidateAdmin(ReadOnlyAdminView, model=KandoCandidate):
    column_list = [KandoCandidate.id, KandoCandidate.kando_candidate_id, KandoCandidate.full_name]
    column_searchable_list = [KandoCandidate.full_name]
    column_sortable_list = [KandoCandidate.kando_candidate_id, KandoCandidate.full_name]


class KandoCvAdmin(ReadOnlyAdminView, model=KandoCv):
    column_list = [KandoCv.id, KandoCv.kando_cv_id, KandoCv.kando_candidate_id]
    column_sortable_list = [KandoCv.kando_cv_id, KandoCv.kando_candidate_id]


class KandoApplicationSourceAdmin(ReadOnlyAdminView, model=KandoApplicationSource):
    column_list = [
        KandoApplicationSource.id,
        KandoApplicationSource.kando_application_source_id,
        KandoApplicationSource.kando_cv_id,
        KandoApplicationSource.name,
        KandoApplicationSource.total_work_experience_months,
    ]
    column_searchable_list = [KandoApplicationSource.name]
    column_sortable_list = [KandoApplicationSource.kando_application_source_id, KandoApplicationSource.kando_cv_id]
    column_formatters = {"cover_letter": format_masked_secret}
    column_export_exclude_list = [KandoApplicationSource.cover_letter]


class KandoHireStepAdmin(ReadOnlyAdminView, model=KandoHireStep):
    column_list = [KandoHireStep.id, KandoHireStep.kando_hire_step_id, KandoHireStep.kando_job_id, KandoHireStep.name]
    column_searchable_list = [KandoHireStep.name]
    column_sortable_list = [KandoHireStep.kando_hire_step_id, KandoHireStep.kando_job_id]


class KandoSyncStateAdmin(ReadOnlyAdminView, model=KandoSyncState):
    column_list = [KandoSyncState.id, KandoSyncState.sync_name, KandoSyncState.last_success_at, KandoSyncState.last_attempt_at]
    column_searchable_list = [KandoSyncState.sync_name]
    column_sortable_list = [KandoSyncState.sync_name, KandoSyncState.last_success_at, KandoSyncState.last_attempt_at]
    column_formatters = {"cursor_json": format_masked_json}


class KandoApiCallLogAdmin(ReadOnlyAdminView, model=KandoApiCallLog):
    column_list = [
        KandoApiCallLog.id,
        KandoApiCallLog.method,
        KandoApiCallLog.endpoint,
        KandoApiCallLog.status_code,
        KandoApiCallLog.retry_count,
        KandoApiCallLog.error_code,
    ]
    column_searchable_list = [KandoApiCallLog.endpoint, KandoApiCallLog.error_code]
    column_sortable_list = [KandoApiCallLog.method, KandoApiCallLog.status_code, KandoApiCallLog.created_at]


class KandoBaseDataCacheAdmin(ReadOnlyAdminView, model=KandoBaseDataCache):
    column_list = [KandoBaseDataCache.id, KandoBaseDataCache.data_type, KandoBaseDataCache.external_id, KandoBaseDataCache.display_name]
    column_searchable_list = [KandoBaseDataCache.data_type, KandoBaseDataCache.display_name]
    column_sortable_list = [KandoBaseDataCache.data_type, KandoBaseDataCache.external_id, KandoBaseDataCache.updated_at]
    column_formatters = {"payload_json": format_masked_json}


class KandoCvWorkExperienceAdmin(ReadOnlyAdminView, model=KandoCvWorkExperience):
    column_list = [KandoCvWorkExperience.id, KandoCvWorkExperience.kando_cv_id, KandoCvWorkExperience.title, KandoCvWorkExperience.company_name]
    column_searchable_list = [KandoCvWorkExperience.title, KandoCvWorkExperience.company_name]
    column_sortable_list = [KandoCvWorkExperience.kando_cv_id, KandoCvWorkExperience.title]
    column_formatters = {"payload_json": format_masked_json}


class KandoCvUniversityDegreeAdmin(ReadOnlyAdminView, model=KandoCvUniversityDegree):
    column_list = [KandoCvUniversityDegree.id, KandoCvUniversityDegree.kando_cv_id, KandoCvUniversityDegree.degree_name, KandoCvUniversityDegree.university_name]
    column_searchable_list = [KandoCvUniversityDegree.degree_name, KandoCvUniversityDegree.university_name]
    column_sortable_list = [KandoCvUniversityDegree.kando_cv_id, KandoCvUniversityDegree.degree_name]
    column_formatters = {"payload_json": format_masked_json}


class KandoCvLanguageSkillAdmin(ReadOnlyAdminView, model=KandoCvLanguageSkill):
    column_list = [
        KandoCvLanguageSkill.id,
        KandoCvLanguageSkill.kando_cv_id,
        KandoCvLanguageSkill.language_id,
        KandoCvLanguageSkill.skill_level_id,
    ]
    column_sortable_list = [KandoCvLanguageSkill.kando_cv_id, KandoCvLanguageSkill.language_id]
    column_formatters = {"payload_json": format_masked_json}


class ScreeningApplicationAdmin(ReadOnlyAdminView, model=ScreeningApplication):
    column_list = [
        ScreeningApplication.id,
        ScreeningApplication.kando_application_id,
        ScreeningApplication.kando_job_id,
        ScreeningApplication.candidate_full_name,
        ScreeningApplication.internal_status,
        ScreeningApplication.priority_bucket,
        ScreeningApplication.priority_score,
        ScreeningApplication.rank_in_job,
        ScreeningApplication.last_screened_at,
    ]
    column_searchable_list = [ScreeningApplication.candidate_full_name, ScreeningApplication.source_name]
    column_sortable_list = [
        ScreeningApplication.kando_job_id,
        ScreeningApplication.internal_status,
        ScreeningApplication.priority_score,
        ScreeningApplication.last_screened_at,
    ]
    column_formatters = {"raw_snapshot_json": format_masked_json}
    column_export_exclude_list = [ScreeningApplication.raw_snapshot_json]


class ScreeningRunAdmin(ReadOnlyAdminView, model=ScreeningRun):
    column_list = [ScreeningRun.id, ScreeningRun.ruleset_id, ScreeningRun.ruleset_version, ScreeningRun.status, ScreeningRun.started_at, ScreeningRun.completed_at]
    column_searchable_list = [ScreeningRun.status]
    column_sortable_list = [ScreeningRun.status, ScreeningRun.started_at, ScreeningRun.completed_at]
    column_formatters = {"run_context_json": format_masked_json}


class ScreeningRunItemAdmin(ReadOnlyAdminView, model=ScreeningRunItem):
    column_list = [ScreeningRunItem.id, ScreeningRunItem.screening_run_id, ScreeningRunItem.screening_application_id, ScreeningRunItem.status]
    column_searchable_list = [ScreeningRunItem.status]
    column_sortable_list = [ScreeningRunItem.screening_run_id, ScreeningRunItem.status]
    column_formatters = {"result_json": format_masked_json}


class ScreeningDecisionAdmin(ReadOnlyAdminView, model=ScreeningDecision):
    column_list = [
        ScreeningDecision.id,
        ScreeningDecision.screening_application_id,
        ScreeningDecision.internal_status,
        ScreeningDecision.ruleset_id,
        ScreeningDecision.ruleset_version,
        ScreeningDecision.created_at,
    ]
    column_searchable_list = [ScreeningDecision.message_fa]
    column_sortable_list = [ScreeningDecision.screening_application_id, ScreeningDecision.internal_status, ScreeningDecision.created_at]
    column_formatters = {"reasons_json": format_masked_json}


class ScreeningScoreAdmin(ReadOnlyAdminView, model=ScreeningScore):
    column_list = [ScreeningScore.id, ScreeningScore.screening_application_id, ScreeningScore.score, ScreeningScore.ruleset_id, ScreeningScore.ruleset_version, ScreeningScore.created_at]
    column_sortable_list = [ScreeningScore.screening_application_id, ScreeningScore.score, ScreeningScore.created_at]
    column_formatters = {"score_breakdown_json": format_masked_json}


class RankingResultAdmin(ReadOnlyAdminView, model=RankingResult):
    column_list = [
        RankingResult.id,
        RankingResult.screening_application_id,
        RankingResult.kando_job_id,
        RankingResult.rank_in_job,
        RankingResult.priority_bucket,
        RankingResult.score,
    ]
    column_sortable_list = [RankingResult.kando_job_id, RankingResult.rank_in_job, RankingResult.score]
    column_formatters = {"score_breakdown_json": format_masked_json}


class AIAnalysisRunAdmin(ReadOnlyAdminView, model=AIAnalysisRun):
    column_list = [
        AIAnalysisRun.id,
        AIAnalysisRun.screening_application_id,
        AIAnalysisRun.provider,
        AIAnalysisRun.model_name,
        AIAnalysisRun.status,
        AIAnalysisRun.error_code,
        AIAnalysisRun.created_at,
    ]
    column_searchable_list = [AIAnalysisRun.provider, AIAnalysisRun.model_name, AIAnalysisRun.error_code]
    column_sortable_list = [AIAnalysisRun.status, AIAnalysisRun.created_at]


class AIAnalysisResultAdmin(ReadOnlyAdminView, model=AIAnalysisResult):
    column_list = [AIAnalysisResult.id, AIAnalysisResult.ai_analysis_run_id, AIAnalysisResult.confidence]
    column_sortable_list = [AIAnalysisResult.ai_analysis_run_id, AIAnalysisResult.confidence]
    column_formatters = {
        "output_json": format_masked_json,
        "normalized_signals_json": format_masked_json,
    }
    column_export_exclude_list = [AIAnalysisResult.output_json]


class ScreeningNoteAdmin(ReadOnlyAdminView, model=ScreeningNote):
    column_list = [ScreeningNote.id, ScreeningNote.screening_application_id, ScreeningNote.note_type, ScreeningNote.author_user_id, ScreeningNote.created_at]
    column_searchable_list = [ScreeningNote.note_fa]
    column_sortable_list = [ScreeningNote.screening_application_id, ScreeningNote.note_type, ScreeningNote.created_at]
    column_formatters = {"note_metadata_json": format_masked_json}


class RecruiterDecisionRecordAdmin(ReadOnlyAdminView, model=RecruiterDecisionRecord):
    column_list = [
        RecruiterDecisionRecord.id,
        RecruiterDecisionRecord.screening_application_id,
        RecruiterDecisionRecord.recruiter_user_id,
        RecruiterDecisionRecord.decision,
        RecruiterDecisionRecord.created_at,
    ]
    column_searchable_list = [RecruiterDecisionRecord.note_fa]
    column_sortable_list = [RecruiterDecisionRecord.screening_application_id, RecruiterDecisionRecord.decision, RecruiterDecisionRecord.created_at]
    column_formatters = {"reason_json": format_masked_json}


class AuditLogAdmin(ReadOnlyAdminView, model=AuditLog):
    column_list = [AuditLog.id, AuditLog.actor_user_id, AuditLog.actor_type, AuditLog.action, AuditLog.entity_type, AuditLog.entity_id, AuditLog.created_at]
    column_searchable_list = [AuditLog.action, AuditLog.entity_type, AuditLog.request_id]
    column_sortable_list = [AuditLog.actor_user_id, AuditLog.created_at, AuditLog.action]
    column_formatters = {"before_json": format_masked_json, "after_json": format_masked_json}
    column_export_exclude_list = [AuditLog.before_json, AuditLog.after_json]


class IntegrationErrorAdmin(ReadOnlyAdminView, model=IntegrationError):
    column_list = [IntegrationError.id, IntegrationError.source, IntegrationError.error_code, IntegrationError.retryable, IntegrationError.created_at]
    column_searchable_list = [IntegrationError.source, IntegrationError.error_code, IntegrationError.message_fa]
    column_sortable_list = [IntegrationError.source, IntegrationError.error_code, IntegrationError.retryable, IntegrationError.created_at]
    column_formatters = {"context_json": format_masked_json}


class WorkerTaskLogAdmin(ReadOnlyAdminView, model=WorkerTaskLog):
    column_list = [WorkerTaskLog.id, WorkerTaskLog.task_name, WorkerTaskLog.task_id, WorkerTaskLog.status, WorkerTaskLog.queue_name, WorkerTaskLog.created_at]
    column_searchable_list = [WorkerTaskLog.task_name, WorkerTaskLog.task_id, WorkerTaskLog.status]
    column_sortable_list = [WorkerTaskLog.task_name, WorkerTaskLog.status, WorkerTaskLog.created_at]
    column_formatters = {"payload_json": format_masked_json}


ADMIN_VIEWS: tuple[type[ModelView], ...] = (
    UserAdmin,
    RoleAdmin,
    PermissionAdmin,
    UserRoleAdmin,
    RolePermissionAdmin,
    KandoConnectionAdmin,
    ScreeningRuleSetAdmin,
    ScreeningRuleGroupAdmin,
    ScreeningRuleAdmin,
    ScreeningRuleTermAdmin,
    KandoRawPayloadAdmin,
    KandoJobAdmin,
    KandoApplicationAdmin,
    KandoApplicationSourceAdmin,
    KandoCandidateAdmin,
    KandoCvAdmin,
    KandoHireStepAdmin,
    KandoSyncStateAdmin,
    KandoApiCallLogAdmin,
    KandoBaseDataCacheAdmin,
    KandoCvWorkExperienceAdmin,
    KandoCvUniversityDegreeAdmin,
    KandoCvLanguageSkillAdmin,
    ScreeningApplicationAdmin,
    ScreeningRunAdmin,
    ScreeningRunItemAdmin,
    ScreeningDecisionAdmin,
    ScreeningScoreAdmin,
    RankingResultAdmin,
    AIAnalysisRunAdmin,
    AIAnalysisResultAdmin,
    ScreeningNoteAdmin,
    RecruiterDecisionRecordAdmin,
    AuditLogAdmin,
    IntegrationErrorAdmin,
    WorkerTaskLogAdmin,
)
