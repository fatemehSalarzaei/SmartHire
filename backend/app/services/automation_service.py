from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai import AIAnalysisResult, AIAnalysisRun
from app.models.enums import AIAnalysisStatus, InternalStatus, RuleSetStatus
from app.models.kando import KandoApplication
from app.models.ranking import RankingResult, ScreeningScore
from app.models.screening import (
    ScreeningApplication,
    ScreeningDecision,
    ScreeningRuleSet,
)
from app.services.ai_analysis_service import AIAnalysisService
from app.services.prompt_builder import PromptBuilder
from app.services.ranking_engine import RankingEngine, RankingOutcome
from app.services.rule_engine import RuleEngine, RuleEngineResult
from app.services.snapshot_builder import SnapshotBuilder

RULESET_NOT_ACTIVE_CODE = "RULESET_NOT_ACTIVE"
RULESET_NOT_ACTIVE_MESSAGE_FA = "برای این عنوان شغلی قانون فعال تعریف نشده است."
SNAPSHOT_UNCHANGED_CODE = "SNAPSHOT_UNCHANGED"
AI_ALREADY_CURRENT_CODE = "AI_ALREADY_CURRENT"
SCREENING_ALREADY_CURRENT_CODE = "SCREENING_ALREADY_CURRENT"
RANKING_ALREADY_CURRENT_CODE = "RANKING_ALREADY_CURRENT"


@dataclass(frozen=True)
class PipelineStepResult:
    status: str
    code: str | None = None
    message_fa: str | None = None
    screening_application_id: UUID | None = None
    kando_application_id: int | None = None
    kando_job_id: int | None = None
    snapshot_hash: str | None = None
    idempotency_key: str | None = None
    details: dict[str, Any] | None = None

    @property
    def skipped(self) -> bool:
        return self.status == "skipped"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "code": self.code,
            "message_fa": self.message_fa,
            "screening_application_id": str(self.screening_application_id)
            if self.screening_application_id
            else None,
            "kando_application_id": self.kando_application_id,
            "kando_job_id": self.kando_job_id,
            "snapshot_hash": self.snapshot_hash,
            "idempotency_key": self.idempotency_key,
            "details": self.details or {},
        }


class ScreeningAutomationService:
    """Automatic screening pipeline orchestration.

    This service coordinates existing Task 04-07 building blocks. It remains deterministic and
    idempotent; it does not expose manual daily screening and it never mutates Kando.
    """

    def __init__(
        self,
        db: Session,
        *,
        snapshot_builder: SnapshotBuilder | None = None,
        ai_service: AIAnalysisService | None = None,
        rule_engine: RuleEngine | None = None,
        ranking_engine: RankingEngine | None = None,
        prompt_builder: PromptBuilder | None = None,
    ) -> None:
        self.db = db
        self.snapshot_builder = snapshot_builder or SnapshotBuilder(db)
        self.ai_service = ai_service or AIAnalysisService(db)
        self.rule_engine = rule_engine or RuleEngine()
        self.ranking_engine = ranking_engine or RankingEngine(self.rule_engine)
        self.prompt_builder = prompt_builder or PromptBuilder()

    def build_application_snapshot(
        self,
        kando_application_id: int,
        *,
        force: bool = False,
    ) -> PipelineStepResult:
        result = self.snapshot_builder.build_for_kando_application_id(kando_application_id)
        snapshot = result.snapshot
        kando = snapshot["kando"]
        application = self._get_or_create_screening_application(int(kando["application_id"]))
        existing_hash = application.snapshot_hash
        if existing_hash == result.snapshot_hash and not force:
            return PipelineStepResult(
                status="skipped",
                code=SNAPSHOT_UNCHANGED_CODE,
                message_fa="اسنپ‌شات رزومه نسبت به اجرای قبلی تغییری نداشته است.",
                screening_application_id=application.id,
                kando_application_id=application.kando_application_id,
                kando_job_id=application.kando_job_id,
                snapshot_hash=application.snapshot_hash,
                idempotency_key=make_idempotency_key(
                    "snapshot",
                    application.kando_application_id,
                    application.snapshot_hash,
                ),
            )

        application.kando_candidate_id = int(kando["candidate_id"])
        application.kando_cv_id = kando.get("cv_id")
        application.kando_job_id = int(kando["job_id"])
        application.candidate_full_name = snapshot.get("candidate", {}).get("full_name")
        application.source_name = _first_source_name(snapshot)
        application.kando_hire_step_id = kando.get("hire_step_id")
        application.kando_status_id = kando.get("status_id")
        application.raw_snapshot_json = snapshot
        application.snapshot_hash = result.snapshot_hash
        application.last_synced_at = datetime.now(timezone.utc)
        if application.internal_status is None:
            application.internal_status = InternalStatus.NOT_REVIEWED
        self.db.add(application)
        self.db.flush()
        return PipelineStepResult(
            status="completed",
            screening_application_id=application.id,
            kando_application_id=application.kando_application_id,
            kando_job_id=application.kando_job_id,
            snapshot_hash=application.snapshot_hash,
            idempotency_key=make_idempotency_key(
                "snapshot",
                application.kando_application_id,
                application.snapshot_hash,
            ),
            details={"missing_fields": result.missing_fields},
        )

    def build_snapshots_for_job(
        self,
        kando_job_id: int,
        *,
        force: bool = False,
    ) -> list[PipelineStepResult]:
        applications = self.db.execute(
            select(KandoApplication).where(KandoApplication.kando_job_id == kando_job_id),
        ).scalars().all()
        return [
            self.build_application_snapshot(application.kando_application_id, force=force)
            for application in applications
        ]

    def run_ai_for_application(
        self,
        screening_application_id: UUID,
        *,
        force: bool = False,
    ) -> PipelineStepResult:
        application = self._screening_application(screening_application_id)
        input_hash = self.prompt_builder.build_resume_analysis_prompt(
            snapshot=application.raw_snapshot_json,
        ).input_hash
        latest = self._latest_ai_run(application.id)
        if (
            latest is not None
            and latest.input_hash == input_hash
            and latest.status == AIAnalysisStatus.SUCCEEDED
            and not force
        ):
            return PipelineStepResult(
                status="skipped",
                code=AI_ALREADY_CURRENT_CODE,
                message_fa="تحلیل هوش مصنوعی برای نسخه فعلی رزومه قبلاً انجام شده است.",
                screening_application_id=application.id,
                kando_application_id=application.kando_application_id,
                kando_job_id=application.kando_job_id,
                snapshot_hash=application.snapshot_hash,
                idempotency_key=make_idempotency_key("ai", application.id, input_hash),
            )
        outcome = self.ai_service.analyze_screening_application(application.id)
        return PipelineStepResult(
            status="completed" if outcome.used_output else "failed",
            code=outcome.error_code,
            message_fa=outcome.message_fa,
            screening_application_id=application.id,
            kando_application_id=application.kando_application_id,
            kando_job_id=application.kando_job_id,
            snapshot_hash=application.snapshot_hash,
            idempotency_key=make_idempotency_key("ai", application.id, input_hash),
            details={"ai_status": outcome.run.status.value, "used_output": outcome.used_output},
        )

    def run_screening_for_application(
        self,
        screening_application_id: UUID,
        *,
        force: bool = False,
    ) -> PipelineStepResult:
        application = self._screening_application(screening_application_id)
        ruleset = self._active_ruleset(application.kando_job_id)
        if ruleset is None:
            return PipelineStepResult(
                status="failed",
                code=RULESET_NOT_ACTIVE_CODE,
                message_fa=RULESET_NOT_ACTIVE_MESSAGE_FA,
                screening_application_id=application.id,
                kando_application_id=application.kando_application_id,
                kando_job_id=application.kando_job_id,
                snapshot_hash=application.snapshot_hash,
            )
        ruleset_dict = ruleset_to_dict(ruleset)
        ai_signals = self._latest_ai_signals(application.id)
        idempotency_key = make_idempotency_key(
            "screening",
            application.id,
            application.snapshot_hash,
            ruleset.id,
            ruleset.version,
            _ai_signal_hash(ai_signals),
        )
        if self._existing_decision(application.id, idempotency_key) is not None and not force:
            return PipelineStepResult(
                status="skipped",
                code=SCREENING_ALREADY_CURRENT_CODE,
                message_fa="غربالگری این نسخه رزومه و قوانین قبلاً انجام شده است.",
                screening_application_id=application.id,
                kando_application_id=application.kando_application_id,
                kando_job_id=application.kando_job_id,
                snapshot_hash=application.snapshot_hash,
                idempotency_key=idempotency_key,
            )
        rule_result = self.rule_engine.evaluate(
            snapshot=application.raw_snapshot_json,
            ruleset=ruleset_dict,
            ai_signals=ai_signals,
        )
        decision = ScreeningDecision(
            screening_application_id=application.id,
            internal_status=rule_result.decision,
            ruleset_id=ruleset.id,
            ruleset_version=ruleset.version,
            reasons_json={
                "idempotency_key": idempotency_key,
                "snapshot_hash": application.snapshot_hash,
                "rule_result": rule_result.to_dict(),
                "ai_advisory_used": ai_signals is not None,
            },
            message_fa="؛ ".join(rule_result.reasons[:3]) if rule_result.reasons else None,
        )
        _ensure_uuid(decision)
        self.db.add(decision)
        application.internal_status = rule_result.decision
        application.last_screened_at = datetime.now(timezone.utc)
        self.db.flush()
        return PipelineStepResult(
            status="completed",
            screening_application_id=application.id,
            kando_application_id=application.kando_application_id,
            kando_job_id=application.kando_job_id,
            snapshot_hash=application.snapshot_hash,
            idempotency_key=idempotency_key,
            details={"decision": rule_result.decision.value, "reasons": rule_result.reasons},
        )

    def calculate_ranking_for_application(
        self,
        screening_application_id: UUID,
        *,
        force: bool = False,
    ) -> PipelineStepResult:
        application = self._screening_application(screening_application_id)
        ruleset = self._active_ruleset(application.kando_job_id)
        if ruleset is None:
            return PipelineStepResult(
                status="failed",
                code=RULESET_NOT_ACTIVE_CODE,
                message_fa=RULESET_NOT_ACTIVE_MESSAGE_FA,
                screening_application_id=application.id,
                kando_application_id=application.kando_application_id,
                kando_job_id=application.kando_job_id,
                snapshot_hash=application.snapshot_hash,
            )
        rule_result = self._latest_rule_result(application.id)
        if rule_result is None:
            ai_signals = self._latest_ai_signals(application.id)
            rule_result = self.rule_engine.evaluate(
                snapshot=application.raw_snapshot_json,
                ruleset=ruleset_to_dict(ruleset),
                ai_signals=ai_signals,
            )
        idempotency_key = make_idempotency_key(
            "ranking",
            application.id,
            application.snapshot_hash,
            ruleset.id,
            ruleset.version,
            rule_result.to_dict(),
        )
        if self._existing_ranking(application.id, idempotency_key) is not None and not force:
            return PipelineStepResult(
                status="skipped",
                code=RANKING_ALREADY_CURRENT_CODE,
                message_fa="رتبه‌بندی این نسخه رزومه قبلاً محاسبه شده است.",
                screening_application_id=application.id,
                kando_application_id=application.kando_application_id,
                kando_job_id=application.kando_job_id,
                snapshot_hash=application.snapshot_hash,
                idempotency_key=idempotency_key,
            )
        ai_signals = self._latest_ai_signals(application.id)
        outcome = self.ranking_engine.score_application(
            snapshot=application.raw_snapshot_json,
            ruleset=ruleset_to_dict(ruleset),
            rule_result=rule_result,
            ai_signals=ai_signals,
        )
        self._persist_ranking(application, outcome, idempotency_key)
        return PipelineStepResult(
            status="completed",
            screening_application_id=application.id,
            kando_application_id=application.kando_application_id,
            kando_job_id=application.kando_job_id,
            snapshot_hash=application.snapshot_hash,
            idempotency_key=idempotency_key,
            details={
                "priority_score": outcome.priority_score,
                "priority_bucket": outcome.priority_bucket.value,
                "rank_in_job": outcome.rank_in_job,
            },
        )

    def calculate_ranking_for_job(
        self,
        kando_job_id: int,
        *,
        force: bool = False,
    ) -> list[PipelineStepResult]:
        applications = self.db.execute(
            select(ScreeningApplication).where(ScreeningApplication.kando_job_id == kando_job_id),
        ).scalars().all()
        results = [
            self.calculate_ranking_for_application(application.id, force=force)
            for application in applications
        ]
        self._recalculate_rank_positions(kando_job_id)
        return results

    def run_full_pipeline_for_application(
        self,
        kando_application_id: int,
        *,
        force: bool = False,
        run_ai: bool = True,
    ) -> list[PipelineStepResult]:
        snapshot_result = self.build_application_snapshot(kando_application_id, force=force)
        if snapshot_result.screening_application_id is None:
            return [snapshot_result]
        results = [snapshot_result]
        if run_ai:
            results.append(
                self.run_ai_for_application(snapshot_result.screening_application_id, force=force),
            )
        results.append(
            self.run_screening_for_application(
                snapshot_result.screening_application_id,
                force=force,
            ),
        )
        results.append(
            self.calculate_ranking_for_application(
                snapshot_result.screening_application_id,
                force=force,
            ),
        )
        return results

    def retry_failed_ai(self, *, limit: int = 50) -> list[PipelineStepResult]:
        rows = self.db.execute(
            select(AIAnalysisRun)
            .where(AIAnalysisRun.status == AIAnalysisStatus.FAILED)
            .order_by(AIAnalysisRun.created_at.asc())
            .limit(limit),
        ).scalars().all()
        seen: set[UUID] = set()
        results: list[PipelineStepResult] = []
        for row in rows:
            if row.screening_application_id in seen:
                continue
            seen.add(row.screening_application_id)
            results.append(self.run_ai_for_application(row.screening_application_id, force=True))
        return results

    def _get_or_create_screening_application(
        self,
        kando_application_id: int,
    ) -> ScreeningApplication:
        application = self.db.execute(
            select(ScreeningApplication).where(
                ScreeningApplication.kando_application_id == kando_application_id,
            ),
        ).scalar_one_or_none()
        if application is None:
            application = ScreeningApplication(
                kando_application_id=kando_application_id,
                kando_candidate_id=0,
                kando_job_id=0,
                internal_status=InternalStatus.NOT_REVIEWED,
                raw_snapshot_json={},
            )
            _ensure_uuid(application)
            self.db.add(application)
            self.db.flush()
        elif application.id is None:
            _ensure_uuid(application)
        return application

    def _screening_application(self, screening_application_id: UUID) -> ScreeningApplication:
        application = self.db.execute(
            select(ScreeningApplication).where(ScreeningApplication.id == screening_application_id),
        ).scalar_one_or_none()
        if application is None:
            raise ValueError(f"Screening application not found: {screening_application_id}")
        return application

    def _active_ruleset(self, kando_job_id: int) -> ScreeningRuleSet | None:
        return self.db.execute(
            select(ScreeningRuleSet).where(
                ScreeningRuleSet.kando_job_id == kando_job_id,
                ScreeningRuleSet.status == RuleSetStatus.ACTIVE,
                ScreeningRuleSet.is_active.is_(True),
            ),
        ).scalar_one_or_none()

    def _latest_ai_run(self, screening_application_id: UUID) -> AIAnalysisRun | None:
        return self.db.execute(
            select(AIAnalysisRun)
            .where(AIAnalysisRun.screening_application_id == screening_application_id)
            .order_by(AIAnalysisRun.created_at.desc()),
        ).scalars().first()

    def _latest_ai_signals(self, screening_application_id: UUID) -> dict[str, Any] | None:
        row = self.db.execute(
            select(AIAnalysisResult)
            .join(AIAnalysisRun, AIAnalysisResult.ai_analysis_run_id == AIAnalysisRun.id)
            .where(
                AIAnalysisRun.screening_application_id == screening_application_id,
                AIAnalysisRun.status == AIAnalysisStatus.SUCCEEDED,
            )
            .order_by(AIAnalysisRun.created_at.desc()),
        ).scalars().first()
        return row.output_json if row is not None else None

    def _existing_decision(
        self,
        screening_application_id: UUID,
        idempotency_key: str,
    ) -> ScreeningDecision | None:
        rows = self.db.execute(
            select(ScreeningDecision).where(
                ScreeningDecision.screening_application_id == screening_application_id,
            ),
        ).scalars().all()
        return _find_by_idempotency_key(rows, idempotency_key, "reasons_json")

    def _existing_ranking(
        self,
        screening_application_id: UUID,
        idempotency_key: str,
    ) -> RankingResult | None:
        rows = self.db.execute(
            select(RankingResult).where(
                RankingResult.screening_application_id == screening_application_id,
            ),
        ).scalars().all()
        return _find_by_idempotency_key(rows, idempotency_key, "score_breakdown_json")

    def _latest_rule_result(self, screening_application_id: UUID) -> RuleEngineResult | None:
        row = self.db.execute(
            select(ScreeningDecision)
            .where(ScreeningDecision.screening_application_id == screening_application_id)
            .order_by(ScreeningDecision.created_at.desc()),
        ).scalars().first()
        if row is None or not isinstance(row.reasons_json, dict):
            return None
        raw = row.reasons_json.get("rule_result")
        if not isinstance(raw, dict):
            return None
        return _rule_result_from_dict(raw)

    def _persist_ranking(
        self,
        application: ScreeningApplication,
        outcome: RankingOutcome,
        idempotency_key: str,
    ) -> None:
        if outcome.priority_score is not None:
            score = ScreeningScore(
                screening_application_id=application.id,
                score=outcome.priority_score,
                score_breakdown_json={
                    **outcome.score_breakdown,
                    "idempotency_key": idempotency_key,
                },
            )
            _ensure_uuid(score)
            self.db.add(score)
        ranking = RankingResult(
            screening_application_id=application.id,
            kando_job_id=application.kando_job_id,
            rank_in_job=outcome.rank_in_job,
            priority_bucket=outcome.priority_bucket,
            score=outcome.priority_score,
            ranking_scope="JOB",
            score_breakdown_json={**outcome.score_breakdown, "idempotency_key": idempotency_key},
        )
        _ensure_uuid(ranking)
        self.db.add(ranking)
        application.priority_score = outcome.priority_score
        application.priority_bucket = outcome.priority_bucket
        application.rank_in_job = outcome.rank_in_job
        application.last_ranked_at = datetime.now(timezone.utc)
        self.db.flush()

    def _recalculate_rank_positions(self, kando_job_id: int) -> None:
        applications = self.db.execute(
            select(ScreeningApplication).where(ScreeningApplication.kando_job_id == kando_job_id),
        ).scalars().all()
        rankable = [
            item
            for item in applications
            if item.priority_score is not None and item.priority_bucket is not None
        ]
        rankable.sort(
            key=lambda item: (
                -(item.priority_score or 0),
                item.created_at,
                item.kando_application_id,
            ),
        )
        for index, application in enumerate(rankable, start=1):
            application.rank_in_job = index
        self.db.flush()


def ruleset_to_dict(ruleset: ScreeningRuleSet) -> dict[str, Any]:
    return {
        "name": ruleset.name,
        "version": ruleset.version,
        "kando_job_id": ruleset.kando_job_id,
        "default_missing_data_policy": ruleset.default_missing_data_policy.value,
        "scoring_enabled": ruleset.scoring_enabled,
        "max_score": ruleset.max_score,
        "groups": [
            {
                "name": group.name,
                "group_type": group.group_type.value,
                "sort_order": group.sort_order,
                "priority": group.sort_order,
                "is_enabled": group.is_enabled,
                "rules": [
                    {
                        "name": rule.message_fa or rule.reason_code or str(rule.id),
                        "rule_type": rule.rule_type.value,
                        "target_entity": _target_entity_from_field(rule.field_path),
                        "target_fields": [_relative_field_for_target(rule.field_path)],
                        "operator": rule.operator.value,
                        "values": rule.value_json.get("values", rule.value_json.get("value", []))
                        if isinstance(rule.value_json, dict)
                        else [],
                        "score_delta": rule.score_delta,
                        "reason_template": rule.message_fa,
                        "is_enabled": rule.is_enabled,
                        "sort_order": rule.sort_order,
                        "terms": [
                            {
                                "field_path": term.field_path,
                                "operator": term.operator.value,
                                "value_json": term.value_json,
                            }
                            for term in sorted(
                                rule.terms,
                                key=lambda term: term.field_path,
                            )
                        ],
                    }
                    for rule in sorted(
                        group.rules,
                        key=lambda item: (item.sort_order, str(item.id)),
                    )
                ],
            }
            for group in sorted(ruleset.groups, key=lambda item: (item.sort_order, item.name))
        ],
    }


def make_idempotency_key(*parts: Any) -> str:
    serialized = json.dumps([_jsonable(part) for part in parts], sort_keys=True, ensure_ascii=False)
    return "sha256:" + hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _first_source_name(snapshot: dict[str, Any]) -> str | None:
    sources = snapshot.get("application_sources")
    if isinstance(sources, list) and sources:
        first = sources[0]
        if isinstance(first, dict) and first.get("source_name"):
            return str(first["source_name"])
    return None


def _ensure_uuid(value: Any) -> None:
    if getattr(value, "id", None) is None:
        value.id = uuid4()


def _find_by_idempotency_key(rows: list[Any], idempotency_key: str, field_name: str) -> Any | None:
    for row in rows:
        payload = getattr(row, field_name, None)
        if isinstance(payload, dict) and payload.get("idempotency_key") == idempotency_key:
            return row
    return None


def _ai_signal_hash(ai_signals: dict[str, Any] | None) -> str | None:
    return make_idempotency_key("ai_signals", ai_signals) if ai_signals is not None else None


def _rule_result_from_dict(value: dict[str, Any]) -> RuleEngineResult:
    from app.services.rule_engine import MatchedRule

    return RuleEngineResult(
        decision=InternalStatus(value["decision"]),
        matched_rules=[MatchedRule(**item) for item in value.get("matched_rules", [])],
        missing_fields=list(value.get("missing_fields", [])),
        reasons=list(value.get("reasons", [])),
        confidence=float(value.get("confidence", 1.0)),
        passed_gates_count=int(value.get("passed_gates_count", 0)),
        positive_reasons_count=int(value.get("positive_reasons_count", 0)),
        blocked_ai_hard_rejects=list(value.get("blocked_ai_hard_rejects", [])),
    )


def _relative_field_for_target(field_path: str | None) -> str:
    if not field_path:
        return ""
    value = str(field_path)
    parts = value.split(".", 1)
    if parts[0] in {
        "candidate",
        "job",
        "cv",
        "language",
        "work",
        "work_experiences",
        "education",
        "application_source",
        "application_sources",
        "ai",
    } and len(parts) == 2:
        return parts[1]
    return value


def _target_entity_from_field(field_path: str | None) -> str:
    if not field_path:
        return "snapshot"
    root = str(field_path).split(".", 1)[0]
    return {
        "candidate": "candidate",
        "language": "language",
        "work_experiences": "work",
        "work": "work",
        "ai": "ai",
    }.get(root, "snapshot")


def _jsonable(value: Any) -> Any:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _jsonable(value[key]) for key in sorted(value)}
    if isinstance(value, list | tuple):
        return [_jsonable(item) for item in value]
    return value
