"""Tests for AI + rule risk adjudication."""

from app.ai_risk_service import MockAiRiskAssessor
from app.analysis import run_analysis
from app.risk_adjudication import merge_ai_and_rule_risk
from app.risk_rules import evaluate_risk
from app.schemas import RiskResult, StructuredHealthInput


def test_merge_rule_override_when_ai_too_low():
    ai_risk = RiskResult(
        risk_level="low",
        flags=["ai_limited_signals"],
        rule_explanation="AI saw limited signals.",
    )
    rule_risk = evaluate_risk(
        StructuredHealthInput(heart_rate=100, sleep_quality="poor"),
        "My heart rate is 100 and I cannot sleep.",
        "en",
    )

    merged, adjudication = merge_ai_and_rule_risk(ai_risk, rule_risk, "en", "ai")

    assert adjudication.rule_override_applied is True
    assert adjudication.ai_risk_level == "low"
    assert merged.risk_level == rule_risk.risk_level
    assert "rule_safety_override" in merged.flags


def test_ai_mode_heartache_rule_net_and_escalation():
    result = run_analysis("I have a heartache", language="en", mode="ai")

    assert result.analysis_mode == "ai"
    assert result.risk_adjudication is not None
    assert result.risk_adjudication.ai_risk_level == "low"
    assert result.risk_result.risk_level == "emergency"
    assert result.escalation.is_emergency is True


def test_mock_mode_uses_rules_only():
    result = run_analysis("My heart rate is 100 and I cannot sleep.", language="en", mode="mock")

    assert result.analysis_mode == "mock"
    assert result.risk_adjudication is not None
    assert result.risk_adjudication.adjudicated_by == "rules"
    assert result.risk_adjudication.ai_risk_level is None
