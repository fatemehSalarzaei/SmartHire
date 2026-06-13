from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy import Select, String, asc, desc, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.auth import CurrentUser, require_permission
from app.core.config import settings
from app.core.errors import AppError, ErrorCode
from app.core.responses import success_response
from app.db.session import get_db_session
from app.models.ai import AIAnalysisResult, AIAnalysisRun
from app.models.audit import IntegrationError, WorkerTaskLog
from app.models.enums import (
    ActorType,
    InternalStatus,
    MissingDataPolicy,
    NoteType,
    PriorityBucket,
    RankingScope,
    RuleGroupType,
    RuleOperator,
    RuleSetStatus,
    RuleType,
)
from app.models.kando import KandoJob
from app.models.notes import RecruiterDecisionRecord, ScreeningNote
from app.models.ranking import RankingResult, ScreeningScore
from app.models.screening import (
    ScreeningApplication,
    ScreeningDecision,
    ScreeningRule,
    ScreeningRuleGroup,
    ScreeningRuleSet,
    ScreeningRun,
)
from app.schemas.common import PaginationMeta, PaginationParams, paginated_response
from app.schemas.internal_api import (
    AcceptedTaskResponse,
    CreateNoteRequest,
    CreateRulesetRequest,
    RecruiterDecisionRequest,
    RetryRunRequest,
)
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/v1", tags=["internal"])

VIEW_APPLICATIONS = "view_applications"
CREATE_RECRUITER_NOTE = "create_recruiter_note"
CREATE_RECRUITER_DECISION = "create_recruiter_decision"
MANAGE_RULESET_DRAFT = "manage_ruleset_draft"
ACTIVATE_RULESET = "activate_ruleset"
ADMIN_REPROCESS = "admin_reprocess"
CHANGE_KANDO_SETTINGS = "change_kando_settings"


@router.get("/jobs")
def list_jobs(
    db: Annotated[Session, Depends(get_db_session)],
    _current_user: Annotated[CurrentUser, Depends(require_permission(VIEW_APPLICATIONS))],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    q: str | None = Query(default=None, max_length=200),
    sort: str = Query(default="title"),
) -> dict[str, Any]:
    params = PaginationParams(page=page, page_size=page_size)
    statement = select(KandoJob)
    if q:
        pattern = f"%{q.strip()}%"
        statement = statement.where(
            or_(KandoJob.title.ilike(pattern), KandoJob.kando_job_id.cast(String).ilike(pattern)),
        )
    total = _count(db, statement, KandoJob.id)
    statement = _apply_sort(
        statement,
        sort,
        allowed={
            "title": KandoJob.title,
            "kando_job_id": KandoJob.kando_job_id,
            "created_at": KandoJob.created_at,
        },
        default=[asc(KandoJob.title), asc(KandoJob.kando_job_id)],
    )
    rows = db.execute(statement.offset(params.offset).limit(params.page_size)).scalars().all()
    return paginated_response(
        [_job_dict(row) for row in rows],
        PaginationMeta.from_params(params, total=total),
    )


@router.get("/jobs/{job_id}")
def get_job(
    job_id: int,
    db: Annotated[Session, Depends(get_db_session)],
    _current_user: Annotated[CurrentUser, Depends(require_permission(VIEW_APPLICATIONS))],
) -> dict[str, Any]:
    job = db.execute(select(KandoJob).where(KandoJob.kando_job_id == job_id)).scalar_one_or_none()
    if job is None:
        raise AppError(code=ErrorCode.NOT_FOUND, status_code=404)
    applications_count = db.execute(
        select(func.count(ScreeningApplication.id)).where(ScreeningApplication.kando_job_id == job_id),
    ).scalar_one()
    ruleset = _active_ruleset_for_job(db, job_id)
    data = _job_dict(job)
    data.update(
        {
            "applications_count": int(applications_count),
            "active_ruleset": _ruleset_summary(ruleset) if ruleset else None,
        },
    )
    return success_response(data)


@router.get("/rulesets")
def list_rulesets(
    db: Annotated[Session, Depends(get_db_session)],
    _current_user: Annotated[CurrentUser, Depends(require_permission(VIEW_APPLICATIONS))],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    kando_job_id: int | None = Query(default=None, ge=1),
    status_filter: RuleSetStatus | None = Query(default=None, alias="status"),
    sort: str = Query(default="-created_at"),
) -> dict[str, Any]:
    params = PaginationParams(page=page, page_size=page_size)
    statement = select(ScreeningRuleSet).options(selectinload(ScreeningRuleSet.groups))
    if kando_job_id is not None:
        statement = statement.where(ScreeningRuleSet.kando_job_id == kando_job_id)
    if status_filter is not None:
        statement = statement.where(ScreeningRuleSet.status == status_filter)
    total = _count(db, statement, ScreeningRuleSet.id)
    statement = _apply_sort(
        statement,
        sort,
        allowed={
            "created_at": ScreeningRuleSet.created_at,
            "version": ScreeningRuleSet.version,
            "name": ScreeningRuleSet.name,
            "kando_job_id": ScreeningRuleSet.kando_job_id,
        },
        default=[desc(ScreeningRuleSet.created_at)],
    )
    rows = db.execute(statement.offset(params.offset).limit(params.page_size)).scalars().unique().all()
    return paginated_response(
        [_ruleset_detail(row, include_groups=False) for row in rows],
        PaginationMeta.from_params(params, total=total),
    )


@router.post("/rulesets", status_code=status.HTTP_201_CREATED)
def create_ruleset(
    payload: CreateRulesetRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[CurrentUser, Depends(require_permission(MANAGE_RULESET_DRAFT))],
) -> dict[str, Any]:
    version = payload.version or _next_ruleset_version(db, payload.kando_job_id)
    ruleset = ScreeningRuleSet(
        kando_job_id=payload.kando_job_id,
        name=payload.name,
        version=version,
        status=RuleSetStatus.DRAFT,
        is_active=False,
        default_missing_data_policy=MissingDataPolicy(payload.default_missing_data_policy),
        scoring_enabled=payload.scoring_enabled,
        max_score=payload.max_score,
        ranking_scope=RankingScope(payload.ranking_scope),
    )
    db.add(ruleset)
    db.flush()
    _create_ruleset_groups(db, ruleset, payload.groups)
    _audit_mutation(
        db,
        request,
        current_user,
        action="RULESET_DRAFT_CREATED",
        entity_type="ScreeningRuleSet",
        entity_id=ruleset.id,
        after_json=_ruleset_detail(ruleset, include_groups=True),
    )
    db.commit()
    db.refresh(ruleset)
    return success_response(_ruleset_detail(ruleset, include_groups=True))


@router.post("/rulesets/{ruleset_id}/activate")
def activate_ruleset(
    ruleset_id: UUID,
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[CurrentUser, Depends(require_permission(ACTIVATE_RULESET))],
) -> dict[str, Any]:
    ruleset = _get_ruleset(db, ruleset_id)
    if ruleset.status == RuleSetStatus.ARCHIVED:
        raise AppError(
            code=ErrorCode.VALIDATION_ERROR,
            message_fa="قانون آرشیوشده قابل فعال‌سازی نیست.",
            status_code=409,
        )
    before = _ruleset_detail(ruleset, include_groups=False)
    active_rulesets = db.execute(
        select(ScreeningRuleSet).where(
            ScreeningRuleSet.kando_job_id == ruleset.kando_job_id,
            ScreeningRuleSet.is_active.is_(True),
        ),
    ).scalars().all()
    for active in active_rulesets:
        active.is_active = False
        active.status = RuleSetStatus.ARCHIVED
    ruleset.is_active = True
    ruleset.status = RuleSetStatus.ACTIVE
    db.flush()
    _enqueue_ranking_after_ruleset_change(ruleset.kando_job_id)
    _audit_mutation(
        db,
        request,
        current_user,
        action="RULESET_ACTIVATED",
        entity_type="ScreeningRuleSet",
        entity_id=ruleset.id,
        before_json=before,
        after_json=_ruleset_detail(ruleset, include_groups=False),
    )
    db.commit()
    return success_response(_ruleset_detail(ruleset, include_groups=True))


@router.get("/applications")
def list_applications(
    db: Annotated[Session, Depends(get_db_session)],
    _current_user: Annotated[CurrentUser, Depends(require_permission(VIEW_APPLICATIONS))],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    status_filter: InternalStatus | None = Query(default=None, alias="status"),
    priority_bucket: PriorityBucket | None = Query(default=None),
    job_id: int | None = Query(default=None, ge=1),
    source: str | None = Query(default=None, max_length=120),
    q: str | None = Query(default=None, max_length=200),
    sort: str = Query(default="-priority_score,rank_in_job"),
) -> dict[str, Any]:
    params = PaginationParams(page=page, page_size=page_size)
    statement = select(ScreeningApplication)
    if status_filter is not None:
        statement = statement.where(ScreeningApplication.internal_status == status_filter)
    if priority_bucket is not None:
        statement = statement.where(ScreeningApplication.priority_bucket == priority_bucket)
    if job_id is not None:
        statement = statement.where(ScreeningApplication.kando_job_id == job_id)
    if source:
        statement = statement.where(ScreeningApplication.source_name == source)
    if q:
        pattern = f"%{q.strip()}%"
        statement = statement.where(
            or_(
                ScreeningApplication.candidate_full_name.ilike(pattern),
                ScreeningApplication.source_name.ilike(pattern),
            ),
        )
    total = _count(db, statement, ScreeningApplication.id)
    statement = _apply_sort(
        statement,
        sort,
        allowed={
            "priority_score": ScreeningApplication.priority_score,
            "rank_in_job": ScreeningApplication.rank_in_job,
            "created_at": ScreeningApplication.created_at,
            "last_screened_at": ScreeningApplication.last_screened_at,
            "last_ranked_at": ScreeningApplication.last_ranked_at,
            "kando_application_id": ScreeningApplication.kando_application_id,
        },
        default=[desc(ScreeningApplication.priority_score), asc(ScreeningApplication.rank_in_job)],
    )
    rows = db.execute(statement.offset(params.offset).limit(params.page_size)).scalars().all()
    return paginated_response(
        [_application_summary(row) for row in rows],
        PaginationMeta.from_params(params, total=total),
    )


@router.get("/applications/{application_id}")
def get_application(
    application_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    _current_user: Annotated[CurrentUser, Depends(require_permission(VIEW_APPLICATIONS))],
) -> dict[str, Any]:
    application = _get_screening_application(db, application_id)
    return success_response(_application_detail(db, application))


@router.get("/applications/{application_id}/notes")
def list_application_notes(
    application_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    _current_user: Annotated[CurrentUser, Depends(require_permission(VIEW_APPLICATIONS))],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
) -> dict[str, Any]:
    params = PaginationParams(page=page, page_size=page_size)
    _get_screening_application(db, application_id)
    statement = select(ScreeningNote).where(ScreeningNote.screening_application_id == application_id)
    total = _count(db, statement, ScreeningNote.id)
    rows = db.execute(
        statement.order_by(desc(ScreeningNote.created_at)).offset(params.offset).limit(params.page_size),
    ).scalars().all()
    return paginated_response(
        [_note_dict(row) for row in rows],
        PaginationMeta.from_params(params, total=total),
    )


@router.post("/applications/{application_id}/notes", status_code=status.HTTP_201_CREATED)
def create_application_note(
    application_id: UUID,
    payload: CreateNoteRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[CurrentUser, Depends(require_permission(CREATE_RECRUITER_NOTE))],
) -> dict[str, Any]:
    _get_screening_application(db, application_id)
    note = ScreeningNote(
        screening_application_id=application_id,
        note_type=NoteType(payload.note_type),
        note_fa=payload.note_fa,
        author_user_id=current_user.id,
        note_metadata_json=payload.note_metadata_json,
    )
    db.add(note)
    db.flush()
    _audit_mutation(
        db,
        request,
        current_user,
        action="RECRUITER_NOTE_CREATED",
        entity_type="ScreeningNote",
        entity_id=note.id,
        after_json=_note_dict(note),
    )
    db.commit()
    return success_response(_note_dict(note))


@router.post("/applications/{application_id}/recruiter-decision", status_code=status.HTTP_201_CREATED)
def create_recruiter_decision(
    application_id: UUID,
    payload: RecruiterDecisionRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[CurrentUser, Depends(require_permission(CREATE_RECRUITER_DECISION))],
) -> dict[str, Any]:
    _get_screening_application(db, application_id)
    decision = RecruiterDecisionRecord(
        screening_application_id=application_id,
        recruiter_user_id=current_user.id,
        decision=payload.decision,
        note_fa=payload.note_fa,
        reason_json=payload.reason_json,
    )
    db.add(decision)
    db.flush()
    _audit_mutation(
        db,
        request,
        current_user,
        action="RECRUITER_DECISION_CREATED",
        entity_type="RecruiterDecisionRecord",
        entity_id=decision.id,
        after_json=_recruiter_decision_dict(decision),
    )
    db.commit()
    return success_response(_recruiter_decision_dict(decision))


@router.get("/applications/{application_id}/ai-analysis")
def get_application_ai_analysis(
    application_id: UUID,
    db: Annotated[Session, Depends(get_db_session)],
    _current_user: Annotated[CurrentUser, Depends(require_permission(VIEW_APPLICATIONS))],
) -> dict[str, Any]:
    _get_screening_application(db, application_id)
    row = db.execute(
        select(AIAnalysisRun, AIAnalysisResult)
        .join(AIAnalysisResult, AIAnalysisResult.ai_analysis_run_id == AIAnalysisRun.id)
        .where(AIAnalysisRun.screening_application_id == application_id)
        .order_by(desc(AIAnalysisRun.created_at)),
    ).first()
    return success_response(_ai_analysis_dict(*row) if row else None)


@router.get("/screening/automation/status")
def automation_status(
    db: Annotated[Session, Depends(get_db_session)],
    _current_user: Annotated[CurrentUser, Depends(require_permission(VIEW_APPLICATIONS))],
) -> dict[str, Any]:
    latest_task = db.execute(
        select(WorkerTaskLog).order_by(desc(WorkerTaskLog.created_at)),
    ).scalars().first()
    failed_count = db.execute(
        select(func.count(WorkerTaskLog.id)).where(WorkerTaskLog.status == "FAILED"),
    ).scalar_one()
    latest_sync_error = db.execute(
        select(IntegrationError).order_by(desc(IntegrationError.created_at)),
    ).scalars().first()
    return success_response(
        {
            "automation_enabled": True,
            "latest_task": _worker_task_dict(latest_task) if latest_task else None,
            "failed_task_count": int(failed_count),
            "latest_integration_error": _integration_error_dict(latest_sync_error)
            if latest_sync_error
            else None,
        },
    )


@router.get("/screening/runs")
def list_screening_runs(
    db: Annotated[Session, Depends(get_db_session)],
    _current_user: Annotated[CurrentUser, Depends(require_permission(VIEW_APPLICATIONS))],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    status_filter: str | None = Query(default=None, alias="status", max_length=80),
    sort: str = Query(default="-created_at"),
) -> dict[str, Any]:
    params = PaginationParams(page=page, page_size=page_size)
    statement = select(ScreeningRun)
    if status_filter:
        statement = statement.where(ScreeningRun.status == status_filter)
    total = _count(db, statement, ScreeningRun.id)
    statement = _apply_sort(
        statement,
        sort,
        allowed={
            "created_at": ScreeningRun.created_at,
            "started_at": ScreeningRun.started_at,
            "completed_at": ScreeningRun.completed_at,
        },
        default=[desc(ScreeningRun.created_at)],
    )
    rows = db.execute(statement.offset(params.offset).limit(params.page_size)).scalars().all()
    return paginated_response(
        [_screening_run_dict(row) for row in rows],
        PaginationMeta.from_params(params, total=total),
    )


@router.post("/screening/runs/{run_id}/retry", status_code=status.HTTP_202_ACCEPTED)
def retry_screening_run(
    run_id: UUID,
    payload: RetryRunRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[CurrentUser, Depends(require_permission(ADMIN_REPROCESS))],
) -> dict[str, Any]:
    run = db.get(ScreeningRun, run_id)
    if run is None:
        raise AppError(code=ErrorCode.NOT_FOUND, status_code=404)
    task_id = _enqueue_retry_for_run(run, payload.force)
    _audit_mutation(
        db,
        request,
        current_user,
        action="SCREENING_RUN_RETRY_REQUESTED",
        entity_type="ScreeningRun",
        entity_id=run.id,
        after_json={"task_id": task_id, "force": payload.force},
    )
    db.commit()
    return success_response(
        AcceptedTaskResponse(
            task_id=task_id,
            message_fa="درخواست اجرای مجدد در صف پردازش قرار گرفت.",
        ).model_dump(),
    )


@router.post("/admin/kando/test-connection")
def test_kando_connection(
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[CurrentUser, Depends(require_permission(CHANGE_KANDO_SETTINGS))],
) -> dict[str, Any]:
    configured = bool(settings.kando_company_api_key and settings.kando_ats_base_url)
    result = {
        "configured": configured,
        "reachable": None,
        "message_fa": "تنظیمات اتصال کندو ثبت شده است. تست شبکه واقعی در محیط استیج انجام شود."
        if configured
        else "کلید API یا آدرس سرویس کندو تنظیم نشده است.",
    }
    _audit_mutation(
        db,
        request,
        current_user,
        action="KANDO_CONNECTION_TEST_REQUESTED",
        entity_type="KandoConnection",
        after_json={"configured": configured},
    )
    db.commit()
    return success_response(result)


def _count(db: Session, statement: Select[Any], column: Any) -> int:
    subquery = statement.with_only_columns(column).order_by(None).subquery()
    return int(db.execute(select(func.count()).select_from(subquery)).scalar_one())


def _apply_sort(
    statement: Select[Any],
    sort: str,
    *,
    allowed: dict[str, Any],
    default: list[Any],
) -> Select[Any]:
    sort_items: list[Any] = []
    for raw_item in sort.split(","):
        item = raw_item.strip()
        if not item:
            continue
        descending = item.startswith("-")
        key = item[1:] if descending else item
        column = allowed.get(key)
        if column is None:
            raise AppError(
                code=ErrorCode.VALIDATION_ERROR,
                message_fa="فیلد مرتب‌سازی معتبر نیست.",
                status_code=400,
                field_errors={"sort": ["فیلد مرتب‌سازی معتبر نیست."]},
            )
        sort_items.append(desc(column) if descending else asc(column))
    return statement.order_by(*(sort_items or default))


def _get_screening_application(db: Session, application_id: UUID) -> ScreeningApplication:
    application = db.get(ScreeningApplication, application_id)
    if application is None:
        raise AppError(code=ErrorCode.NOT_FOUND, status_code=404)
    return application


def _get_ruleset(db: Session, ruleset_id: UUID) -> ScreeningRuleSet:
    ruleset = db.execute(
        select(ScreeningRuleSet)
        .options(
            selectinload(ScreeningRuleSet.groups).selectinload(ScreeningRuleGroup.rules),
        )
        .where(ScreeningRuleSet.id == ruleset_id),
    ).scalars().unique().one_or_none()
    if ruleset is None:
        raise AppError(code=ErrorCode.NOT_FOUND, status_code=404)
    return ruleset


def _active_ruleset_for_job(db: Session, kando_job_id: int) -> ScreeningRuleSet | None:
    return db.execute(
        select(ScreeningRuleSet).where(
            ScreeningRuleSet.kando_job_id == kando_job_id,
            ScreeningRuleSet.is_active.is_(True),
            ScreeningRuleSet.status == RuleSetStatus.ACTIVE,
        ),
    ).scalar_one_or_none()


def _next_ruleset_version(db: Session, kando_job_id: int) -> int:
    current = db.execute(
        select(func.max(ScreeningRuleSet.version)).where(
            ScreeningRuleSet.kando_job_id == kando_job_id,
        ),
    ).scalar_one()
    return int(current or 0) + 1


def _create_ruleset_groups(
    db: Session,
    ruleset: ScreeningRuleSet,
    groups: list[dict[str, Any]],
) -> None:
    for group_index, group_payload in enumerate(groups):
        group = ScreeningRuleGroup(
            ruleset_id=ruleset.id,
            group_type=RuleGroupType(group_payload.get("group_type", "SCORING")),
            name=str(group_payload.get("name") or f"Group {group_index + 1}"),
            sort_order=int(group_payload.get("sort_order", group_index)),
            is_enabled=bool(group_payload.get("is_enabled", True)),
        )
        db.add(group)
        db.flush()
        for rule_index, rule_payload in enumerate(group_payload.get("rules", [])):
            rule = ScreeningRule(
                group_id=group.id,
                rule_type=RuleType(rule_payload.get("rule_type", "INFO_ONLY")),
                field_path=str(rule_payload.get("field_path") or "candidate.full_name"),
                operator=RuleOperator(rule_payload.get("operator", "EXISTS")),
                value_json=rule_payload.get("value_json") or {},
                score_delta=rule_payload.get("score_delta"),
                reason_code=rule_payload.get("reason_code"),
                message_fa=rule_payload.get("message_fa"),
                sort_order=int(rule_payload.get("sort_order", rule_index)),
                is_enabled=bool(rule_payload.get("is_enabled", True)),
            )
            db.add(rule)


def _audit_mutation(
    db: Session,
    request: Request,
    current_user: CurrentUser,
    *,
    action: str,
    entity_type: str,
    entity_id: UUID | None = None,
    before_json: dict[str, Any] | None = None,
    after_json: dict[str, Any] | None = None,
) -> None:
    AuditService.record(
        db,
        action=action,
        entity_type=entity_type,
        actor_user_id=current_user.id,
        actor_type=ActorType.USER,
        entity_id=entity_id,
        before_json=before_json or {},
        after_json=after_json or {},
        context=AuditService.context_from_request(request),
    )


def _job_dict(row: KandoJob) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "kando_job_id": row.kando_job_id,
        "title": row.title,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


def _ruleset_summary(row: ScreeningRuleSet) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "kando_job_id": row.kando_job_id,
        "name": row.name,
        "version": row.version,
        "status": row.status.value,
        "is_active": row.is_active,
    }


def _ruleset_detail(row: ScreeningRuleSet, *, include_groups: bool) -> dict[str, Any]:
    data = {
        **_ruleset_summary(row),
        "default_missing_data_policy": row.default_missing_data_policy.value,
        "scoring_enabled": row.scoring_enabled,
        "max_score": row.max_score,
        "ranking_scope": row.ranking_scope.value,
        "config_hash": row.config_hash,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }
    if include_groups:
        data["groups"] = [
            {
                "id": str(group.id),
                "group_type": group.group_type.value,
                "name": group.name,
                "sort_order": group.sort_order,
                "is_enabled": group.is_enabled,
                "rules": [_rule_dict(rule) for rule in sorted(group.rules, key=lambda r: r.sort_order)],
            }
            for group in sorted(row.groups, key=lambda g: g.sort_order)
        ]
    return data


def _rule_dict(row: ScreeningRule) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "rule_type": row.rule_type.value,
        "field_path": row.field_path,
        "operator": row.operator.value,
        "value_json": row.value_json,
        "score_delta": row.score_delta,
        "reason_code": row.reason_code,
        "message_fa": row.message_fa,
        "sort_order": row.sort_order,
        "is_enabled": row.is_enabled,
    }


def _application_summary(row: ScreeningApplication) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "kando_application_id": row.kando_application_id,
        "kando_candidate_id": row.kando_candidate_id,
        "kando_cv_id": row.kando_cv_id,
        "kando_job_id": row.kando_job_id,
        "candidate_full_name": row.candidate_full_name,
        "source_name": row.source_name,
        "internal_status": row.internal_status.value,
        "priority_score": row.priority_score,
        "priority_bucket": row.priority_bucket.value if row.priority_bucket else None,
        "rank_in_job": row.rank_in_job,
        "snapshot_hash": row.snapshot_hash,
        "last_synced_at": _iso(row.last_synced_at),
        "last_screened_at": _iso(row.last_screened_at),
        "last_ranked_at": _iso(row.last_ranked_at),
        "created_at": _iso(row.created_at),
    }


def _application_detail(db: Session, row: ScreeningApplication) -> dict[str, Any]:
    latest_decision = db.execute(
        select(ScreeningDecision)
        .where(ScreeningDecision.screening_application_id == row.id)
        .order_by(desc(ScreeningDecision.created_at)),
    ).scalars().first()
    latest_score = db.execute(
        select(ScreeningScore)
        .where(ScreeningScore.screening_application_id == row.id)
        .order_by(desc(ScreeningScore.created_at)),
    ).scalars().first()
    latest_ranking = db.execute(
        select(RankingResult)
        .where(RankingResult.screening_application_id == row.id)
        .order_by(desc(RankingResult.created_at)),
    ).scalars().first()
    latest_note = db.execute(
        select(ScreeningNote)
        .where(ScreeningNote.screening_application_id == row.id)
        .order_by(desc(ScreeningNote.created_at)),
    ).scalars().first()
    return {
        **_application_summary(row),
        "snapshot": _safe_snapshot_summary(row.raw_snapshot_json),
        "latest_decision": _decision_dict(latest_decision) if latest_decision else None,
        "latest_score": _score_dict(latest_score) if latest_score else None,
        "latest_ranking": _ranking_dict(latest_ranking) if latest_ranking else None,
        "latest_note": _note_dict(latest_note) if latest_note else None,
    }


def _safe_snapshot_summary(snapshot: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        return {}
    return {
        "snapshot_version": snapshot.get("snapshot_version"),
        "snapshot_hash": snapshot.get("snapshot_hash"),
        "kando": snapshot.get("kando"),
        "job": snapshot.get("job"),
        "candidate": _remove_contact_fields(snapshot.get("candidate")),
        "missing_fields": snapshot.get("missing_fields", []),
        "metadata": snapshot.get("metadata", {}),
    }


def _remove_contact_fields(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    blocked = {"email", "mobile", "phone", "address", "national_code"}
    return {key: item for key, item in value.items() if key not in blocked}


def _decision_dict(row: ScreeningDecision) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "internal_status": row.internal_status.value,
        "ruleset_id": str(row.ruleset_id) if row.ruleset_id else None,
        "ruleset_version": row.ruleset_version,
        "reasons_json": row.reasons_json,
        "message_fa": row.message_fa,
        "created_at": _iso(row.created_at),
    }


def _score_dict(row: ScreeningScore) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "score": row.score,
        "score_breakdown_json": row.score_breakdown_json,
        "ruleset_id": str(row.ruleset_id) if row.ruleset_id else None,
        "ruleset_version": row.ruleset_version,
        "created_at": _iso(row.created_at),
    }


def _ranking_dict(row: RankingResult) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "kando_job_id": row.kando_job_id,
        "rank_in_job": row.rank_in_job,
        "priority_bucket": row.priority_bucket.value if row.priority_bucket else None,
        "score": row.score,
        "ranking_scope": row.ranking_scope,
        "score_breakdown_json": row.score_breakdown_json,
        "created_at": _iso(row.created_at),
    }


def _note_dict(row: ScreeningNote) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "screening_application_id": str(row.screening_application_id),
        "note_type": row.note_type.value,
        "note_fa": row.note_fa,
        "author_user_id": str(row.author_user_id) if row.author_user_id else None,
        "note_metadata_json": row.note_metadata_json,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


def _recruiter_decision_dict(row: RecruiterDecisionRecord) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "screening_application_id": str(row.screening_application_id),
        "recruiter_user_id": str(row.recruiter_user_id) if row.recruiter_user_id else None,
        "decision": row.decision.value,
        "note_fa": row.note_fa,
        "reason_json": row.reason_json,
        "created_at": _iso(row.created_at),
    }


def _ai_analysis_dict(run: AIAnalysisRun, result: AIAnalysisResult) -> dict[str, Any]:
    return {
        "run": {
            "id": str(run.id),
            "status": run.status.value,
            "provider": run.provider,
            "model_name": run.model_name,
            "prompt_version": run.prompt_version,
            "input_hash": run.input_hash,
            "error_code": run.error_code,
            "error_message_fa": run.error_message_fa,
            "retry_count": run.retry_count,
            "created_at": _iso(run.created_at),
            "updated_at": _iso(run.updated_at),
        },
        "result": {
            "id": str(result.id),
            "output_json": _safe_ai_output(result.output_json),
            "normalized_signals_json": result.normalized_signals_json,
            "confidence": result.confidence,
            "created_at": _iso(result.created_at),
        },
    }


def _safe_ai_output(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    # Raw model text is not exposed by default; structured AI output is advisory-only.
    return {
        key: item
        for key, item in value.items()
        if key not in {"raw_output", "raw_prompt", "raw_response"}
    }


def _screening_run_dict(row: ScreeningRun) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "ruleset_id": str(row.ruleset_id) if row.ruleset_id else None,
        "ruleset_version": row.ruleset_version,
        "status": row.status,
        "started_at": _iso(row.started_at),
        "completed_at": _iso(row.completed_at),
        "run_context_json": row.run_context_json,
        "created_at": _iso(row.created_at),
    }


def _worker_task_dict(row: WorkerTaskLog) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "task_name": row.task_name,
        "task_id": row.task_id,
        "status": row.status,
        "queue_name": row.queue_name,
        "started_at": _iso(row.started_at),
        "completed_at": _iso(row.completed_at),
        "error_code": row.error_code,
        "message_fa": row.message_fa,
        "created_at": _iso(row.created_at),
    }


def _integration_error_dict(row: IntegrationError) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "source": row.source,
        "error_code": row.error_code,
        "message_fa": row.message_fa,
        "retryable": row.retryable,
        "created_at": _iso(row.created_at),
    }


def _enqueue_retry_for_run(run: ScreeningRun, force: bool) -> str | None:
    from app.workers.pipeline_tasks import run_screening_for_job

    kando_job_id = None
    if isinstance(run.run_context_json, dict):
        value = run.run_context_json.get("kando_job_id")
        if isinstance(value, int):
            kando_job_id = value
    if kando_job_id is None:
        raise AppError(
            code=ErrorCode.VALIDATION_ERROR,
            message_fa="این اجرای غربالگری اطلاعات کافی برای اجرای مجدد ندارد.",
            status_code=400,
        )
    async_result = run_screening_for_job.apply_async(
        args=[kando_job_id],
        kwargs={"force": force},
        queue="screening",
    )
    return str(getattr(async_result, "id", "")) or None


def _enqueue_ranking_after_ruleset_change(kando_job_id: int) -> str | None:
    from app.workers.pipeline_tasks import recalculate_after_ruleset_change

    async_result = recalculate_after_ruleset_change.apply_async(
        args=[kando_job_id],
        queue="ranking",
    )
    return str(getattr(async_result, "id", "")) or None


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()
