"""Merge AI risk assessment with deterministic rule safety net."""

from app.schemas import AnalysisMode, Language, RiskAdjudication, RiskLevel, RiskResult

_RISK_RANK: dict[RiskLevel, int] = {
    "low": 0,
    "moderate": 1,
    "high": 2,
    "emergency": 3,
}


def risk_rank(level: RiskLevel) -> int:
    return _RISK_RANK[level]


def max_risk_level(a: RiskLevel, b: RiskLevel) -> RiskLevel:
    return a if risk_rank(a) >= risk_rank(b) else b


def _override_reason(
    ai_level: RiskLevel,
    rule_level: RiskLevel,
    language: Language,
) -> str:
    if language == "zh":
        return (
            f"规则安全网将 AI 评估的「{_level_zh(ai_level)}」提升为「{_level_zh(rule_level)}」，"
            "以弥补 AI 可能遗漏的重大风险信号。"
        )
    return (
        f"Rule safety net elevated AI assessment ({ai_level}) to {rule_level} "
        "to catch major risks the AI may have missed."
    )


def _level_zh(level: RiskLevel) -> str:
    return {"low": "低", "moderate": "中", "high": "高", "emergency": "紧急"}[level]


def merge_ai_and_rule_risk(
    ai_risk: RiskResult,
    rule_risk: RiskResult,
    language: Language,
    mode: AnalysisMode,
) -> tuple[RiskResult, RiskAdjudication]:
    """AI adjudicates first; rules may only raise risk, never lower it."""
    final_level = max_risk_level(ai_risk.risk_level, rule_risk.risk_level)
    override = risk_rank(rule_risk.risk_level) > risk_rank(ai_risk.risk_level)

    flags: list[str] = []
    seen: set[str] = set()
    for flag in ai_risk.flags + (rule_risk.flags if override else []):
        if flag not in seen:
            flags.append(flag)
            seen.add(flag)
    if override:
        if "rule_safety_override" not in seen:
            flags.append("rule_safety_override")

    explanation = ai_risk.rule_explanation
    override_reason: str | None = None
    if override:
        override_reason = _override_reason(ai_risk.risk_level, rule_risk.risk_level, language)
        explanation = f"{explanation} {override_reason}"

    merged = RiskResult(
        risk_level=final_level,
        flags=flags,
        rule_explanation=explanation.strip(),
    )
    adjudication = RiskAdjudication(
        mode=mode,
        ai_risk_level=ai_risk.risk_level,
        rule_risk_level=rule_risk.risk_level,
        final_risk_level=final_level,
        adjudicated_by="ai_with_rule_override" if override else "ai",
        rule_override_applied=override,
        override_reason=override_reason,
    )
    return merged, adjudication


def adjudication_from_rules_only(
    rule_risk: RiskResult,
    mode: AnalysisMode = "mock",
) -> RiskAdjudication:
    return RiskAdjudication(
        mode=mode,
        ai_risk_level=None,
        rule_risk_level=rule_risk.risk_level,
        final_risk_level=rule_risk.risk_level,
        adjudicated_by="rules",
        rule_override_applied=False,
        override_reason=None,
    )


def apply_emergency_to_adjudication(
    adjudication: RiskAdjudication,
    final_level: RiskLevel,
    language: Language,
) -> RiskAdjudication:
    if final_level != "emergency":
        return adjudication

    if language == "zh":
        reason = "紧急症状检测将最终风险提升为紧急。"
    else:
        reason = "Emergency symptom detection elevated the final risk to emergency."

    return adjudication.model_copy(
        update={
            "final_risk_level": "emergency",
            "adjudicated_by": "ai_with_emergency_override"
            if adjudication.mode == "ai"
            else "rules",
            "override_reason": reason,
        }
    )
