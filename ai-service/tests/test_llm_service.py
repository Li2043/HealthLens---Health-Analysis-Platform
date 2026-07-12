from app.llm_service import MockLLMService
from app.schemas import RiskResult, StructuredHealthInput


def test_mock_llm_returns_deterministic_text():
    service = MockLLMService()
    structured = StructuredHealthInput(heart_rate=110)
    risk = RiskResult(
        risk_level="moderate",
        flags=["elevated_heart_rate"],
        rule_explanation="Rule engine detected 1 flag(s): heart rate above 100 bpm. Overall risk level is moderate.",
    )

    result1 = service.explain(structured, risk)
    result2 = service.explain(structured, risk)

    assert result1 == result2
    assert len(result1) > 0


def test_mock_llm_includes_disclaimer():
    service = MockLLMService()
    structured = StructuredHealthInput()
    risk = RiskResult(
        risk_level="low",
        flags=[],
        rule_explanation="No rule-based flags were triggered. Overall risk level is low.",
    )

    result = service.explain(structured, risk)
    assert "not a medical diagnosis" in result.lower()


def test_mock_llm_returns_health_focused_english_text():
    service = MockLLMService()
    structured = StructuredHealthInput(heart_rate=110)
    risk = RiskResult(
        risk_level="moderate",
        flags=["elevated_heart_rate"],
        rule_explanation="Rule engine detected 1 flag(s): heart rate above 100 bpm.",
    )

    result = service.generate_explanation(
        structured,
        risk,
        source_text="My heart rate is 110 and I feel stressed.",
        language="en",
    )

    assert "From your description" in result
    assert "heart rate" in result.lower()
    assert "workflow" not in result.lower()
    assert "rule engine" not in result.lower()
    assert "not a medical diagnosis" in result.lower()


def test_mock_llm_returns_chinese_explanation():
    service = MockLLMService()
    structured = StructuredHealthInput(heart_rate=110)
    risk = RiskResult(
        risk_level="moderate",
        flags=["elevated_heart_rate"],
        rule_explanation="规则引擎检测到 1 个标志：心率超过 100 次/分。总体风险等级为中。",
    )

    result = service.generate_explanation(structured, risk, language="zh")

    assert "根据您的描述" in result
    assert "这不是医疗诊断" in result
    assert "工作流" not in result
    assert "规则引擎" not in result


def test_low_risk_explanation_reassures_and_suggests_self_care():
    service = MockLLMService()
    structured = StructuredHealthInput(sleep_quality="poor")
    risk = RiskResult(
        risk_level="low",
        flags=["poor_sleep"],
        rule_explanation="Low risk.",
    )

    result = service.generate_explanation(
        structured,
        risk,
        source_text="I slept badly last night.",
        language="en",
    )

    assert "no strong reason to worry" in result.lower()
    assert "daily self-care" in result.lower()
    assert "not a medical diagnosis" in result.lower()


def test_moderate_risk_explanation_includes_causes_and_countermeasures():
    service = MockLLMService()
    structured = StructuredHealthInput(heart_rate=110, mood="anxious")
    risk = RiskResult(
        risk_level="moderate",
        flags=["elevated_heart_rate", "anxiety_or_stress_flag"],
        rule_explanation="Moderate risk.",
    )

    result = service.generate_explanation(
        structured,
        risk,
        source_text="My heart rate is 110 and I feel stressed.",
        language="en",
    )

    assert "possible contributing factors" in result.lower()
    assert "suggested next steps" in result.lower()
    assert "24–48 hours" in result


def test_high_risk_explanation_includes_emergency_number_and_first_aid():
    service = MockLLMService()
    structured = StructuredHealthInput()
    risk = RiskResult(
        risk_level="high",
        flags=["emergency_symptoms"],
        rule_explanation="High risk.",
    )

    result = service.generate_explanation(
        structured,
        risk,
        source_text="I have severe chest pain and shortness of breath.",
        language="en",
    )

    assert "999" in result
    assert "a&e" in result.lower()
    assert "first steps" in result.lower()
    assert "call 999" in result.lower()


def test_high_risk_chinese_explanation_includes_120():
    service = MockLLMService()
    structured = StructuredHealthInput()
    risk = RiskResult(
        risk_level="high",
        flags=["emergency_symptoms"],
        rule_explanation="高风险。",
    )

    result = service.generate_explanation(
        structured,
        risk,
        source_text="我胸痛，喘不过气。",
        language="zh",
    )

    assert "120" in result
    assert "急诊" in result
    assert "第一步" in result
