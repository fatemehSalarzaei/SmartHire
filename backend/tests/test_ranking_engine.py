import json
from pathlib import Path

from app.models.enums import PriorityBucket
from app.services.ranking_engine import RankingEngine
from app.services.rule_engine import RuleEngine

FIXTURES = Path(__file__).resolve().parents[2] / "tests/fixtures"


def _load_json(relative_path: str):
    return json.loads((FIXTURES / relative_path).read_text())


def test_ranking_engine_matches_expected_ranking_fixture() -> None:
    ruleset = _load_json("rulesets/customer_support_ruleset_v1.json")
    expected = {item["kando_application_id"]: item for item in _load_json("expected/ranking_results.json")}
    rule_engine = RuleEngine()
    ranking_engine = RankingEngine(rule_engine)

    valid_snapshot = _load_json("snapshots/application_snapshot_valid.json")
    valid_result = rule_engine.evaluate(snapshot=valid_snapshot, ruleset=ruleset)
    valid_ranking = ranking_engine.score_application(
        snapshot=valid_snapshot,
        ruleset=ruleset,
        rule_result=valid_result,
    )

    assert valid_ranking.priority_score == expected[1001]["priority_score"]
    assert valid_ranking.priority_bucket.value == expected[1001]["priority_bucket"]

    missing_language_snapshot = _load_json("snapshots/application_snapshot_missing_language.json")
    missing_language_result = rule_engine.evaluate(snapshot=missing_language_snapshot, ruleset=ruleset)
    missing_language_ranking = ranking_engine.score_application(
        snapshot=missing_language_snapshot,
        ruleset=ruleset,
        rule_result=missing_language_result,
    )

    assert missing_language_ranking.priority_score == expected[1004]["priority_score"]
    assert missing_language_ranking.priority_bucket.value == expected[1004]["priority_bucket"]
    assert missing_language_ranking.rank_in_job == expected[1004]["rank_in_job"]


def test_ai_bonus_can_affect_score_but_not_decision() -> None:
    ruleset = _load_json("rulesets/customer_support_ruleset_with_ai_signals.json")
    ai_signals = _load_json("ai/ai_valid_output.json")
    snapshot = _load_json("snapshots/application_snapshot_valid.json")
    rule_engine = RuleEngine()
    ranking_engine = RankingEngine(rule_engine)

    rule_result = rule_engine.evaluate(snapshot=snapshot, ruleset=ruleset, ai_signals=ai_signals)
    ranking = ranking_engine.score_application(
        snapshot=snapshot,
        ruleset=ruleset,
        rule_result=rule_result,
        ai_signals=ai_signals,
    )

    assert rule_result.decision.value == "SMART_NOT_REJECTED"
    assert ranking.priority_score == 95
    assert ranking.score_breakdown["advisory_ai_used"] is True


def test_rank_for_job_orders_by_score_and_does_not_rank_review_unknown() -> None:
    ruleset = _load_json("rulesets/customer_support_ruleset_v1.json")
    rule_engine = RuleEngine()
    ranking_engine = RankingEngine(rule_engine)
    valid_snapshot = _load_json("snapshots/application_snapshot_valid.json")
    lower_snapshot = _load_json("snapshots/application_snapshot_valid.json")
    lower_snapshot["kando"]["application_id"] = 1007
    lower_snapshot["education"] = []
    lower_snapshot["metadata"]["built_at"] = "2026-06-11T00:00:00Z"
    unknown_snapshot = _load_json("snapshots/application_snapshot_missing_language.json")

    rows = []
    for snapshot in [lower_snapshot, valid_snapshot, unknown_snapshot]:
        rule_result = rule_engine.evaluate(snapshot=snapshot, ruleset=ruleset)
        outcome = ranking_engine.score_application(snapshot=snapshot, ruleset=ruleset, rule_result=rule_result)
        rows.append((outcome, rule_result, snapshot))

    ranked = {item.kando_application_id: item for item in ranking_engine.rank_for_job(rows)}

    assert ranked[1001].rank_in_job == 1
    assert ranked[1007].rank_in_job == 2
    assert ranked[1004].priority_bucket == PriorityBucket.REVIEW_UNKNOWN
    assert ranked[1004].rank_in_job is None
