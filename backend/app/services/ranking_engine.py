from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any

from app.models.enums import InternalStatus, PriorityBucket, RuleType
from app.services.rule_engine import RuleEngine, RuleEngineResult

DEFAULT_BASE_SCORE = 30
DEFAULT_MAX_SCORE = 100


@dataclass(frozen=True)
class RankingOutcome:
    kando_application_id: int
    kando_job_id: int | None
    priority_score: int | None
    priority_bucket: PriorityBucket
    rank_in_job: int | None
    score_breakdown: dict[str, Any]
    enters_priority_queue: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "kando_application_id": self.kando_application_id,
            "kando_job_id": self.kando_job_id,
            "priority_score": self.priority_score,
            "priority_bucket": self.priority_bucket.value,
            "rank_in_job": self.rank_in_job,
            "score_breakdown": self.score_breakdown,
            "enters_priority_queue": self.enters_priority_queue,
        }


class RankingEngine:
    """Deterministic score and queue ranking engine.

    Ranking is intentionally separate from AI analysis. Optional AI signals may affect configured
    score bonus/penalty rules, but AI output alone never creates a rejection or a final rank.
    """

    def __init__(self, rule_engine: RuleEngine | None = None) -> None:
        self.rule_engine = rule_engine or RuleEngine()

    def score_application(
        self,
        *,
        snapshot: dict[str, Any],
        ruleset: dict[str, Any],
        rule_result: RuleEngineResult,
        ai_signals: dict[str, Any] | None = None,
    ) -> RankingOutcome:
        application_id = int(snapshot.get("kando", {}).get("application_id") or 0)
        job_id_value = snapshot.get("kando", {}).get("job_id")
        kando_job_id = int(job_id_value) if job_id_value is not None else None

        if rule_result.decision == InternalStatus.UNSUPPORTED_SOURCE:
            return self._unknown(application_id, kando_job_id, rule_result, "unsupported_source")
        if rule_result.decision == InternalStatus.NEEDS_HUMAN_REVIEW and rule_result.missing_fields:
            return self._unknown(application_id, kando_job_id, rule_result, "missing_required_data")

        max_score = _int_or_default(ruleset.get("max_score"), DEFAULT_MAX_SCORE)
        base_score = _int_or_default(ruleset.get("base_score"), DEFAULT_BASE_SCORE)
        bonuses: list[dict[str, Any]] = []
        penalties: list[dict[str, Any]] = []

        for rule in _scoring_rules(ruleset):
            if rule.get("is_enabled") is False:
                continue
            evaluation = self.rule_engine.evaluate_rule(snapshot=snapshot, rule=rule, ai_signals=ai_signals)
            if evaluation.missing or not evaluation.matched:
                continue
            rule_type = RuleType(str(rule.get("rule_type")))
            delta = _int_or_default(rule.get("score_delta"), 0)
            item = {
                "rule_name": rule.get("name"),
                "reason": rule.get("reason_template") or rule.get("message_fa") or rule.get("name"),
                "score_delta": abs(delta),
                "source": "AI" if str(rule.get("target_entity") or "").lower() == "ai" else "RULE",
            }
            if rule_type == RuleType.SCORE_BONUS:
                bonuses.append(item)
            elif rule_type == RuleType.SCORE_PENALTY:
                penalties.append(item)

        bonus_total = sum(int(item["score_delta"]) for item in bonuses)
        penalty_total = sum(int(item["score_delta"]) for item in penalties)
        score = _clamp(base_score + bonus_total - penalty_total, 0, max_score)
        bucket = _bucket_for_score(score)
        enters_priority_queue = rule_result.decision in {
            InternalStatus.SMART_NOT_REJECTED,
            InternalStatus.NEEDS_HUMAN_REVIEW,
        }

        return RankingOutcome(
            kando_application_id=application_id,
            kando_job_id=kando_job_id,
            priority_score=score,
            priority_bucket=bucket,
            rank_in_job=None,
            enters_priority_queue=enters_priority_queue,
            score_breakdown={
                "base_score": base_score,
                "bonus_total": bonus_total,
                "penalty_total": penalty_total,
                "max_score": max_score,
                "bonuses": bonuses,
                "penalties": penalties,
                "rule_decision": rule_result.decision.value,
                "advisory_ai_used": any(item["source"] == "AI" for item in [*bonuses, *penalties]),
            },
        )

    def rank_for_job(self, outcomes: list[tuple[RankingOutcome, RuleEngineResult, dict[str, Any]]]) -> list[RankingOutcome]:
        rankable = [item for item in outcomes if item[0].enters_priority_queue and item[0].priority_score is not None]
        rankable.sort(
            key=lambda item: (
                -(item[0].priority_score or 0),
                -item[1].passed_gates_count,
                -item[1].positive_reasons_count,
                len(item[1].missing_fields),
                _received_at_sort_value(item[2]),
                item[0].kando_application_id,
            ),
        )
        ranked_by_application_id: dict[int, RankingOutcome] = {}
        for index, (outcome, _rule_result, _snapshot) in enumerate(rankable, start=1):
            ranked_by_application_id[outcome.kando_application_id] = replace(outcome, rank_in_job=index)

        result: list[RankingOutcome] = []
        for outcome, _rule_result, _snapshot in outcomes:
            result.append(ranked_by_application_id.get(outcome.kando_application_id, outcome))
        return result

    def _unknown(
        self,
        application_id: int,
        kando_job_id: int | None,
        rule_result: RuleEngineResult,
        reason: str,
    ) -> RankingOutcome:
        return RankingOutcome(
            kando_application_id=application_id,
            kando_job_id=kando_job_id,
            priority_score=None,
            priority_bucket=PriorityBucket.REVIEW_UNKNOWN,
            rank_in_job=None,
            enters_priority_queue=False,
            score_breakdown={
                "rule_decision": rule_result.decision.value,
                "reason": reason,
                "missing_fields": rule_result.missing_fields,
            },
        )


def _scoring_rules(ruleset: dict[str, Any]) -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = []
    for group in sorted(
        _as_dict_list(ruleset.get("groups")),
        key=lambda item: (item.get("priority", item.get("sort_order", 0)), item.get("name", "")),
    ):
        for rule in sorted(
            _as_dict_list(group.get("rules")),
            key=lambda item: (item.get("priority", item.get("sort_order", 0)), item.get("name", "")),
        ):
            if str(rule.get("rule_type")) in {RuleType.SCORE_BONUS.value, RuleType.SCORE_PENALTY.value}:
                rules.append(rule)
    return rules


def _bucket_for_score(score: int) -> PriorityBucket:
    if score >= 75:
        return PriorityBucket.HIGH
    if score >= 50:
        return PriorityBucket.MEDIUM
    return PriorityBucket.LOW


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


def _int_or_default(value: Any, default: int) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _received_at_sort_value(snapshot: dict[str, Any]) -> str:
    metadata = snapshot.get("metadata") if isinstance(snapshot.get("metadata"), dict) else {}
    value = metadata.get("received_at") or metadata.get("built_at") or ""
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]
