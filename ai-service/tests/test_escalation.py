"""Tests for emergency escalation logic (medical safety policy Layer 4)."""

from fastapi.testclient import TestClient

from app.escalation import build_escalation, detect_emergency_patterns
from app.main import app

client = TestClient(app)


def test_detect_chest_pain_emergency():
    matched = detect_emergency_patterns("I have chest pain and shortness of breath.")
    assert "chest_pain" in matched
    assert "breathing_difficulty" in matched


def test_detect_stroke_emergency():
    matched = detect_emergency_patterns("My face is drooping and my speech is slurred.")
    assert "stroke_signs" in matched


def test_detect_chinese_emergency():
    matched = detect_emergency_patterns("我突然胸痛，而且呼吸困难。")
    assert "chest_pain" in matched
    assert "breathing_difficulty" in matched


def test_detect_chinese_heart_pain_variant():
    matched = detect_emergency_patterns("我心脏痛 无法呼吸")
    assert "chest_pain" in matched
    assert "breathing_difficulty" in matched


def test_no_emergency_for_mild_input():
    matched = detect_emergency_patterns("I slept well and feel fine today.")
    assert matched == []


def test_emergency_overrides_low_risk():
    result = build_escalation("I have chest pain.", risk_level="low")
    assert result.level == "emergency"
    assert result.triage_tier == "emergency"
    assert result.is_emergency is True
    assert "chest_pain" in result.matched_patterns


def test_high_risk_maps_to_urgent_without_emergency_pattern():
    result = build_escalation("My blood pressure is 200.", risk_level="high")
    assert result.level == "urgent"
    assert result.triage_tier == "high"
    assert result.is_emergency is False


def test_moderate_risk_maps_to_routine():
    result = build_escalation("My heart rate is 100.", risk_level="moderate")
    assert result.level == "routine"
    assert result.triage_tier == "moderate"


def test_low_risk_maps_to_self_care():
    result = build_escalation("I feel calm.", risk_level="low")
    assert result.level == "self_care"
    assert result.triage_tier == "low"
    assert result.is_emergency is False


def test_chinese_emergency_message_localized():
    result = build_escalation("我胸痛", risk_level="low", language="zh")
    assert result.level == "emergency"
    assert "急救" in result.recommended_action or "紧急" in result.recommended_action


def test_elevate_risk_for_emergency():
    from app.escalation import elevate_risk_for_emergency
    from app.schemas import RiskResult

    risk = RiskResult(risk_level="low", flags=[], rule_explanation="No vitals detected.")
    escalation = build_escalation("I have chest pain.", risk_level="low")
    elevated = elevate_risk_for_emergency(risk, escalation)

    assert elevated.risk_level == "emergency"
    assert "emergency_symptoms" in elevated.flags


def test_detect_heartache_emergency():
    matched = detect_emergency_patterns("I have a heartache")
    assert "chest_pain" in matched


def test_analyse_endpoint_returns_escalation():
    response = client.post(
        "/analyse",
        json={"text": "I have chest pain and shortness of breath.", "language": "en"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "escalation" in data
    assert data["escalation"]["is_emergency"] is True
    assert data["escalation"]["level"] == "emergency"
    assert data["risk_result"]["risk_level"] == "emergency"


def test_analyse_endpoint_non_emergency_escalation():
    response = client.post(
        "/analyse",
        json={"text": "I slept well and feel calm.", "language": "en"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["escalation"]["is_emergency"] is False
    assert data["escalation"]["level"] in ("self_care", "routine")
