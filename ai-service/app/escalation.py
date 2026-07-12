"""Emergency escalation logic (Layer 4 of the medical AI safety policy).

This module detects red-flag emergency symptom patterns from the raw user text
and derives an escalation recommendation. It is intentionally independent of the
vitals-centric rule engine: a symptom-only emergency (e.g. chest pain) must be
able to trigger escalation even when no numeric vitals are present.

This is a prototype safety net, not a clinical triage system. Patterns are
conservative and may produce false positives; false positives are an acceptable
trade-off given the asymmetric cost of missing an emergency.
"""

from app.schemas import (
    EscalationLevel,
    EscalationResult,
    Language,
    RiskLevel,
    RiskResult,
    TriageTier,
)

# Triage tier is the canonical, doc-aligned risk band (see docs/TRIAGE_POLICY.md).
# Escalation level is the action label; the two are 1:1 by design.
_LEVEL_TO_TIER: dict[EscalationLevel, TriageTier] = {
    "self_care": "low",
    "routine": "moderate",
    "urgent": "high",
    "emergency": "emergency",
}

# Each red-flag pattern maps to a list of lowercase substrings (English + 简体中文).
# A pattern fires if ANY of its keywords appears in the lowercased source text.
_EMERGENCY_PATTERNS: dict[str, list[str]] = {
    "chest_pain": [
        "chest pain",
        "chest tightness",
        "tight chest",
        "pain in my chest",
        "heart pain",
        "heart ache",
        "heartache",
        "heart hurts",
        "my heart hurts",
        "aching heart",
        "胸痛",
        "胸口痛",
        "胸闷",
        "胸口疼",
        "心脏痛",
        "心脏疼",
        "心痛",
    ],
    "breathing_difficulty": [
        "shortness of breath",
        "short of breath",
        "difficulty breathing",
        "can't breathe",
        "cannot breathe",
        "trouble breathing",
        "呼吸困难",
        "喘不过气",
        "无法呼吸",
        "气促",
    ],
    "stroke_signs": [
        "drooping",
        "slurred",
        "slur my words",
        "weakness on one side",
        "one side of my body",
        "面部下垂",
        "嘴歪",
        "口齿不清",
        "说话含糊",
        "半身无力",
        "偏瘫",
    ],
    "loss_of_consciousness": [
        "loss of consciousness",
        "lost consciousness",
        "passed out",
        "fainted",
        "unconscious",
        "昏迷",
        "失去意识",
        "晕倒",
        "昏厥",
    ],
    "severe_bleeding": [
        "severe bleeding",
        "heavy bleeding",
        "bleeding heavily",
        "won't stop bleeding",
        "uncontrolled bleeding",
        "大出血",
        "出血不止",
        "血流不止",
    ],
    "anaphylaxis": [
        "anaphylaxis",
        "severe allergic reaction",
        "throat closing",
        "throat is closing",
        "过敏性休克",
        "喉咙肿",
        "严重过敏",
    ],
    "seizure": [
        "seizure",
        "convulsion",
        "convulsing",
        "抽搐",
        "癫痫发作",
    ],
    "suicidal_ideation": [
        "suicidal",
        "kill myself",
        "want to die",
        "end my life",
        "自杀",
        "想死",
        "轻生",
        "结束自己的生命",
    ],
}

_EMERGENCY_MESSAGE = {
    "en": (
        "These symptoms can indicate a medical emergency. Please seek urgent "
        "in-person medical care or call your local emergency number now. "
        "This is not a diagnosis."
    ),
    "zh": (
        "这些症状可能提示医疗紧急情况。请立即就近就医，或拨打当地急救电话。"
        "这不是诊断。"
    ),
}

_URGENT_MESSAGE = {
    "en": (
        "Based on the detected signals, please contact a healthcare professional "
        "promptly. This is not a diagnosis."
    ),
    "zh": "根据检测到的信号，请尽快联系医疗专业人员。这不是诊断。",
}

_ROUTINE_MESSAGE = {
    "en": (
        "Consider contacting a healthcare professional if these signs persist or "
        "worsen. This is not a diagnosis."
    ),
    "zh": "如果这些迹象持续或加重，请考虑联系医疗专业人员。这不是诊断。",
}

_SELF_CARE_MESSAGE = {
    "en": (
        "No urgent concerns were detected. Continue to monitor how you feel and "
        "seek advice if symptoms persist or worsen. This is not a diagnosis."
    ),
    "zh": "未检测到紧急情况。请继续关注自身感受，若症状持续或加重请寻求建议。这不是诊断。",
}


def detect_emergency_patterns(text: str) -> list[str]:
    """Return the ids of any red-flag emergency patterns found in the text."""
    if not text:
        return []
    lowered = text.lower()
    matched: list[str] = []
    for pattern_id, keywords in _EMERGENCY_PATTERNS.items():
        if any(keyword in lowered for keyword in keywords):
            matched.append(pattern_id)
    return matched


def _message(level: EscalationLevel, language: Language) -> str:
    lang = "zh" if language == "zh" else "en"
    return {
        "emergency": _EMERGENCY_MESSAGE,
        "urgent": _URGENT_MESSAGE,
        "routine": _ROUTINE_MESSAGE,
        "self_care": _SELF_CARE_MESSAGE,
    }[level][lang]


def build_escalation(
    text: str,
    risk_level: RiskLevel,
    language: Language = "en",
) -> EscalationResult:
    """Derive an escalation recommendation from red-flag detection and risk level.

    Emergency-pattern detection overrides the numeric risk level so that
    symptom-only emergencies still escalate.
    """
    matched = detect_emergency_patterns(text)

    if matched:
        level: EscalationLevel = "emergency"
    elif risk_level == "high":
        level = "urgent"
    elif risk_level == "moderate":
        level = "routine"
    else:
        level = "self_care"

    return EscalationResult(
        level=level,
        triage_tier=_LEVEL_TO_TIER[level],
        is_emergency=bool(matched),
        matched_patterns=matched,
        recommended_action=_message(level, language),
    )


def elevate_risk_for_emergency(
    risk_result: RiskResult,
    escalation: EscalationResult,
    language: Language = "en",
) -> RiskResult:
    """Align risk_level with emergency escalation so the UI does not show low risk."""
    if not escalation.is_emergency:
        return risk_result

    flags = list(risk_result.flags)
    if "emergency_symptoms" not in flags:
        flags.append("emergency_symptoms")

    if language == "zh":
        explanation = (
            "在您描述中检测到紧急症状（如胸痛、呼吸困难等）。"
            "整体风险等级已提升为紧急，请尽快寻求专业医疗帮助。"
        )
    else:
        explanation = (
            "Emergency symptoms were detected in your description "
            "(for example chest pain or breathing difficulty). "
            "Overall risk is elevated to emergency — please seek urgent medical care."
        )

    return RiskResult(
        risk_level="emergency",
        flags=flags,
        rule_explanation=explanation,
    )
