from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Any

from app.models.enums import InternalStatus, MissingDataPolicy, RuleType
from app.services.normalization_service import NormalizationService

UNSUPPORTED_SOURCE_REASON_FA = "رزومه ساختاریافته یا cvId قابل دریافت نیست"
PASS_GATE_NOT_MET_MESSAGES_FA = {
    "english_level": "سطح زبان انگلیسی کافی نیست",
}
AI_HARD_REJECT_BLOCKED_CODE = "AI_HARD_REJECT_BLOCKED"


@dataclass(frozen=True)
class MatchedRule:
    name: str | None
    rule_type: str
    reason: str
    score_delta: int | None = None
    source: str = "RULE"


@dataclass(frozen=True)
class RuleEngineResult:
    decision: InternalStatus
    matched_rules: list[MatchedRule]
    missing_fields: list[str]
    reasons: list[str]
    confidence: float = 1.0
    passed_gates_count: int = 0
    positive_reasons_count: int = 0
    blocked_ai_hard_rejects: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "matched_rules": [rule.__dict__ for rule in self.matched_rules],
            "missing_fields": self.missing_fields,
            "reasons": self.reasons,
            "confidence": self.confidence,
            "passed_gates_count": self.passed_gates_count,
            "positive_reasons_count": self.positive_reasons_count,
            "blocked_ai_hard_rejects": self.blocked_ai_hard_rejects,
        }


@dataclass(frozen=True)
class RuleEvaluation:
    matched: bool
    missing: bool = False
    values: list[Any] = field(default_factory=list)


class RuleEngine:
    """Deterministic application rule engine.

    Rules are data supplied by RuleSet JSON/database records. This service intentionally does not
    hardcode customer-specific business rules. It evaluates the configured rules against a canonical
    application snapshot and optional validated AI signals.
    """

    def __init__(self, normalizer: NormalizationService | None = None) -> None:
        self.normalizer = normalizer or NormalizationService()

    def evaluate(
        self,
        *,
        snapshot: dict[str, Any],
        ruleset: dict[str, Any],
        ai_signals: dict[str, Any] | None = None,
        allow_ai_hard_reject: bool = False,
    ) -> RuleEngineResult:
        missing_fields = set(_as_string_list(snapshot.get("missing_fields")))
        if snapshot.get("kando", {}).get("cv_id") is None:
            return RuleEngineResult(
                decision=InternalStatus.UNSUPPORTED_SOURCE,
                matched_rules=[],
                missing_fields=["kando.cv_id"],
                reasons=[UNSUPPORTED_SOURCE_REASON_FA],
                confidence=1.0,
                passed_gates_count=0,
                positive_reasons_count=0,
            )

        matched_rules: list[MatchedRule] = []
        reasons: list[str] = []
        review_reasons: list[str] = []
        reject_reasons: list[str] = []
        blocked_ai_hard_rejects: list[str] = []
        passed_gates_count = 0
        positive_reasons_count = 0

        for group in _sorted_groups(ruleset):
            for rule in _sorted_rules(group):
                if rule.get("is_enabled") is False:
                    continue
                rule_type = _rule_type(rule)
                evaluation = self.evaluate_rule(snapshot=snapshot, rule=rule, ai_signals=ai_signals)
                reason = _reason(rule)

                if evaluation.missing:
                    self._apply_missing_policy(rule, ruleset, missing_fields, review_reasons, reject_reasons)
                    continue

                if _is_ai_target(rule) and rule_type == RuleType.REJECT_GATE and not allow_ai_hard_reject:
                    if evaluation.matched:
                        blocked_ai_hard_rejects.append(rule.get("name") or reason)
                    continue

                if rule_type == RuleType.NEEDS_REVIEW_GATE and evaluation.matched:
                    review_reasons.append(reason)
                    matched_rules.append(_matched_rule(rule, reason))
                elif rule_type == RuleType.REJECT_GATE:
                    if evaluation.matched:
                        reject_reasons.append(reason)
                        matched_rules.append(_matched_rule(rule, reason))
                    else:
                        failed_reason = _pass_gate_failure_message(rule)
                        if failed_reason:
                            reject_reasons.append(failed_reason)
                elif rule_type in {RuleType.PASS_GATE, RuleType.OVERRIDE_PASS}:
                    if evaluation.matched:
                        passed_gates_count += 1
                        positive_reasons_count += 1
                        reasons.append(reason)
                        matched_rules.append(_matched_rule(rule, reason))
                    elif rule_type == RuleType.PASS_GATE:
                        failed_reason = _pass_gate_failure_message(rule)
                        if failed_reason:
                            reject_reasons.append(failed_reason)
                elif rule_type in {RuleType.SCORE_BONUS, RuleType.SCORE_PENALTY, RuleType.INFO_ONLY}:
                    if evaluation.matched and rule_type == RuleType.INFO_ONLY:
                        matched_rules.append(_matched_rule(rule, reason))

        final_reasons: list[str]
        if reject_reasons:
            decision = InternalStatus.SMART_REJECTED
            final_reasons = _dedupe_preserve_order([*reject_reasons])
        elif review_reasons or missing_fields:
            decision = InternalStatus.NEEDS_HUMAN_REVIEW
            final_reasons = _dedupe_preserve_order([*review_reasons, *reasons])
        else:
            decision = InternalStatus.SMART_NOT_REJECTED
            final_reasons = _dedupe_preserve_order(reasons)

        return RuleEngineResult(
            decision=decision,
            matched_rules=matched_rules,
            missing_fields=sorted(missing_fields),
            reasons=final_reasons,
            confidence=1.0 if not missing_fields else 0.8,
            passed_gates_count=passed_gates_count,
            positive_reasons_count=positive_reasons_count,
            blocked_ai_hard_rejects=blocked_ai_hard_rejects,
        )

    def evaluate_rule(
        self,
        *,
        snapshot: dict[str, Any],
        rule: dict[str, Any],
        ai_signals: dict[str, Any] | None = None,
    ) -> RuleEvaluation:
        values = self._resolve_rule_values(snapshot=snapshot, rule=rule, ai_signals=ai_signals)
        if not values:
            return RuleEvaluation(matched=False, missing=True)
        return RuleEvaluation(
            matched=any(_compare(operator=_operator(rule), actual=value, expected=rule.get("values")) for value in values),
            missing=False,
            values=values,
        )

    def _resolve_rule_values(
        self,
        *,
        snapshot: dict[str, Any],
        rule: dict[str, Any],
        ai_signals: dict[str, Any] | None,
    ) -> list[Any]:
        entity = str(rule.get("target_entity") or "").lower()
        fields = _as_string_list(rule.get("target_fields"))
        values: list[Any] = []

        if entity == "candidate":
            values.extend(_values_for_fields(snapshot.get("candidate"), fields))
        elif entity == "job":
            values.extend(_values_for_fields(snapshot.get("job"), fields))
        elif entity == "cv":
            values.extend(_values_for_fields(snapshot.get("cv"), fields))
        elif entity == "language":
            values.extend(_language_values(snapshot, fields))
        elif entity == "work":
            values.extend(_collection_values(snapshot.get("work_experiences"), fields))
        elif entity == "education":
            values.extend(_collection_values(snapshot.get("education"), fields))
        elif entity == "application_source":
            values.extend(_collection_values(snapshot.get("application_sources"), fields))
        elif entity == "ai":
            values.extend(_ai_values(ai_signals or {}, fields))
        else:
            values.extend(_snapshot_path_values(snapshot, fields))

        return [value for value in _flatten(values) if value is not None and value != ""]

    def _apply_missing_policy(
        self,
        rule: dict[str, Any],
        ruleset: dict[str, Any],
        missing_fields: set[str],
        review_reasons: list[str],
        reject_reasons: list[str],
    ) -> None:
        fields = _as_string_list(rule.get("target_fields")) or [rule.get("field_path")]
        for field in fields:
            if field:
                missing_fields.add(_missing_field_name(rule, field))
        policy = _missing_policy(rule.get("on_missing_policy") or ruleset.get("default_missing_data_policy"))
        reason = _reason(rule)
        if policy == MissingDataPolicy.REJECT:
            reject_reasons.append(reason)
        elif policy == MissingDataPolicy.NEEDS_REVIEW:
            review_reasons.append(reason)


class UnsupportedRuleOperator(ValueError):
    pass


def _sorted_groups(ruleset: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        _as_dict_list(ruleset.get("groups")),
        key=lambda group: (group.get("priority", group.get("sort_order", 0)), group.get("name", "")),
    )


def _sorted_rules(group: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        _as_dict_list(group.get("rules")),
        key=lambda rule: (rule.get("priority", rule.get("sort_order", 0)), rule.get("name", "")),
    )


def _rule_type(rule: dict[str, Any]) -> RuleType:
    return RuleType(str(rule.get("rule_type")))


def _operator(rule: dict[str, Any]) -> str:
    return str(rule.get("operator") or "").upper()


def _reason(rule: dict[str, Any]) -> str:
    return str(rule.get("reason_template") or rule.get("message_fa") or rule.get("name") or "قانون اعمال شد")


def _matched_rule(rule: dict[str, Any], reason: str) -> MatchedRule:
    return MatchedRule(
        name=rule.get("name"),
        rule_type=str(rule.get("rule_type")),
        reason=reason,
        score_delta=rule.get("score_delta"),
        source="AI" if _is_ai_target(rule) else "RULE",
    )


def _missing_policy(value: Any) -> MissingDataPolicy:
    if value is None:
        return MissingDataPolicy.NEEDS_REVIEW
    return MissingDataPolicy(str(value))


def _missing_field_name(rule: dict[str, Any], field: Any) -> str:
    entity = str(rule.get("target_entity") or "").lower()
    if entity == "language" and str(field) == "english_level":
        return "language.english_level"
    if entity:
        return f"{entity}.{field}"
    return str(field)


def _is_ai_target(rule: dict[str, Any]) -> bool:
    return str(rule.get("target_entity") or "").lower() == "ai"


def _pass_gate_failure_message(rule: dict[str, Any]) -> str | None:
    if _rule_type(rule) not in {RuleType.PASS_GATE, RuleType.REJECT_GATE}:
        return None
    fields = _as_string_list(rule.get("target_fields"))
    for field in fields:
        if field in PASS_GATE_NOT_MET_MESSAGES_FA:
            return PASS_GATE_NOT_MET_MESSAGES_FA[field]
    return None


def _compare(*, operator: str, actual: Any, expected: Any) -> bool:
    expected_values = _as_list(expected)
    if operator == "EXISTS":
        return actual is not None and actual != ""
    if operator == "NOT_EXISTS":
        return actual is None or actual == ""
    if operator == "EQUALS":
        return any(_normalize_scalar(actual) == _normalize_scalar(item) for item in expected_values)
    if operator == "NOT_EQUALS":
        return all(_normalize_scalar(actual) != _normalize_scalar(item) for item in expected_values)
    if operator == "IN":
        return any(_normalize_scalar(actual) == _normalize_scalar(item) for item in expected_values)
    if operator == "NOT_IN":
        return all(_normalize_scalar(actual) != _normalize_scalar(item) for item in expected_values)
    if operator == "CONTAINS":
        return any(_normalize_scalar(item) in _normalize_scalar(actual) for item in expected_values)
    if operator == "NOT_CONTAINS":
        return all(_normalize_scalar(item) not in _normalize_scalar(actual) for item in expected_values)
    if operator == "CONTAINS_ANY":
        return any(_normalize_scalar(item) in _normalize_scalar(actual) for item in expected_values)
    if operator in {"FUZZY_MATCH", "FUZZY_IN"}:
        actual_text = _normalize_scalar(actual)
        return any(
            _normalize_scalar(item) in actual_text
            or actual_text in _normalize_scalar(item)
            or SequenceMatcher(None, actual_text, _normalize_scalar(item)).ratio() >= 0.82
            for item in expected_values
        )
    if operator == "REGEX_MATCH":
        actual_text = str(actual or "")
        return any(re.search(str(item), actual_text, flags=re.IGNORECASE) is not None for item in expected_values)
    if operator == "GREATER_THAN":
        return _number(actual) is not None and any(_number(actual) > _number(item) for item in expected_values if _number(item) is not None)
    if operator == "GREATER_THAN_OR_EQUAL":
        return _number(actual) is not None and any(_number(actual) >= _number(item) for item in expected_values if _number(item) is not None)
    if operator == "LESS_THAN":
        return _number(actual) is not None and any(_number(actual) < _number(item) for item in expected_values if _number(item) is not None)
    if operator == "LESS_THAN_OR_EQUAL":
        return _number(actual) is not None and any(_number(actual) <= _number(item) for item in expected_values if _number(item) is not None)
    if operator == "BETWEEN":
        return _between(actual, expected_values)
    if operator == "NOT_BETWEEN":
        return not _between(actual, expected_values)
    if operator == "DURATION_AT_LEAST":
        actual_number = _number(actual)
        required = _number(expected_values[0]) if expected_values else None
        return actual_number is not None and required is not None and actual_number >= required
    raise UnsupportedRuleOperator(f"Unsupported rule operator: {operator}")


def _between(actual: Any, expected_values: list[Any]) -> bool:
    actual_number = _number(actual)
    if actual_number is None or len(expected_values) < 2:
        return False
    low = _number(expected_values[0])
    high = _number(expected_values[1])
    return low is not None and high is not None and low <= actual_number <= high


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def _normalize_scalar(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("ي", "ی").replace("ك", "ک").strip().lower()


def _language_values(snapshot: dict[str, Any], fields: list[str]) -> list[Any]:
    rows = _as_dict_list(snapshot.get("language_skills"))
    values: list[Any] = []
    for field in fields:
        if field == "english_level":
            for row in rows:
                language = _normalize_scalar(row.get("language") or row.get("language_normalized"))
                if language in {"english", "انگلیسی"}:
                    values.append(row.get("level") or row.get("level_normalized"))
        else:
            values.extend(_collection_values(rows, [field]))
    return values


def _collection_values(rows: Any, fields: list[str]) -> list[Any]:
    values: list[Any] = []
    for row in _as_dict_list(rows):
        values.extend(_values_for_fields(row, fields))
    return values


def _values_for_fields(source: Any, fields: list[str]) -> list[Any]:
    if not isinstance(source, dict):
        return []
    values: list[Any] = []
    for field in fields:
        values.extend(_snapshot_path_values(source, [field]))
    return values


def _snapshot_path_values(snapshot: dict[str, Any], fields: list[str]) -> list[Any]:
    values: list[Any] = []
    for field in fields:
        current: Any = snapshot
        for part in str(field).split("."):
            if isinstance(current, dict):
                current = current.get(part)
            else:
                current = None
                break
        values.append(current)
    return values


def _ai_values(ai_signals: dict[str, Any], fields: list[str]) -> list[Any]:
    values: list[Any] = []
    for field in fields:
        if field == "positive_signals.code":
            values.extend(_signal_codes(ai_signals.get("positive_signals")))
        elif field == "negative_signals.code":
            values.extend(_signal_codes(ai_signals.get("negative_signals")))
        else:
            values.extend(_snapshot_path_values(ai_signals, [field]))
    return values


def _signal_codes(value: Any) -> list[str]:
    return [str(item.get("code")) for item in _as_dict_list(value) if item.get("code")]


def _flatten(values: list[Any]) -> list[Any]:
    flattened: list[Any] = []
    for value in values:
        if isinstance(value, list):
            flattened.extend(_flatten(value))
        else:
            flattened.append(value)
    return flattened


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _as_string_list(value: Any) -> list[str]:
    return [str(item) for item in _as_list(value) if item is not None]


def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
