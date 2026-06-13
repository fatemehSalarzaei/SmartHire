import copy
import json
from pathlib import Path

from app.models.enums import InternalStatus
from app.services.rule_engine import AI_HARD_REJECT_BLOCKED_CODE, RuleEngine

FIXTURES = Path(__file__).resolve().parents[2] / "tests/fixtures"


def _load_json(relative_path: str):
    return json.loads((FIXTURES / relative_path).read_text())


def test_rule_engine_matches_expected_screening_decisions_fixture() -> None:
    ruleset = _load_json("rulesets/customer_support_ruleset_v1.json")
    expected = {item["kando_application_id"]: item for item in _load_json("expected/screening_decisions.json")}
    snapshots = [
        _load_json("snapshots/application_snapshot_valid.json"),
        _load_json("snapshots/application_snapshot_rejected.json"),
        _load_json("snapshots/application_snapshot_unsupported_source.json"),
    ]
    engine = RuleEngine()

    for snapshot in snapshots:
        result = engine.evaluate(snapshot=snapshot, ruleset=ruleset)
        expected_item = expected[snapshot["kando"]["application_id"]]

        assert result.decision.value == expected_item["decision"]
        assert result.missing_fields == expected_item["missing_fields"]
        for reason in expected_item["main_reasons"]:
            assert reason in result.reasons


def test_missing_critical_language_defaults_to_human_review_not_reject() -> None:
    ruleset = _load_json("rulesets/customer_support_ruleset_v1.json")
    snapshot = _load_json("snapshots/application_snapshot_missing_language.json")

    result = RuleEngine().evaluate(snapshot=snapshot, ruleset=ruleset)

    assert result.decision == InternalStatus.NEEDS_HUMAN_REVIEW
    assert "language.english_level" in result.missing_fields
    assert result.confidence < 1.0


def test_ai_scoring_signal_can_match_but_ai_only_hard_reject_is_blocked() -> None:
    snapshot = _load_json("snapshots/application_snapshot_valid.json")
    ruleset = _load_json("rulesets/customer_support_ruleset_with_ai_signals.json")
    ai_signals = _load_json("ai/ai_valid_output.json")
    hard_reject_rule = {
        "name": "AI hard reject must not apply",
        "rule_type": "REJECT_GATE",
        "target_entity": "ai",
        "target_fields": ["negative_signals.code"],
        "operator": "IN",
        "values": ["AI_REJECT"],
        "reason_template": "رد فقط بر اساس هوش مصنوعی ممنوع است",
    }
    mutated_ruleset = copy.deepcopy(ruleset)
    mutated_ruleset["groups"].append(
        {
            "name": "Forbidden AI reject",
            "group_type": "GATE",
            "priority": 0,
            "rules": [hard_reject_rule],
        },
    )
    ai_signals["negative_signals"] = [{"code": "AI_REJECT", "label_fa": "ریسک", "confidence": 0.9}]

    result = RuleEngine().evaluate(snapshot=snapshot, ruleset=mutated_ruleset, ai_signals=ai_signals)

    assert result.decision != InternalStatus.SMART_REJECTED
    assert result.blocked_ai_hard_rejects == ["AI hard reject must not apply"]
    assert AI_HARD_REJECT_BLOCKED_CODE == "AI_HARD_REJECT_BLOCKED"
