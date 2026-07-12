"""AI-first risk assessment with mock fallback for offline demos."""

import json
import os
import re
from abc import ABC, abstractmethod

from app.errors import ProviderConfigurationError
from app.risk_rules import evaluate_risk
from app.schemas import Language, RiskLevel, RiskResult, StructuredHealthInput

_RISK_LEVELS: set[str] = {"low", "moderate", "high", "emergency"}

_RISK_ASSESSMENT_PROMPT = """You assess health consultation risk from user text and structured signals.

Return JSON only with:
- risk_level: one of low, moderate, high, emergency
- flags: array of short snake_case concern flags (may be empty)
- reasoning: brief plain-text rationale (NOT a diagnosis, no medication advice)

Guidelines:
- Be cautious with chest pain, breathing difficulty, stroke signs, severe bleeding, loss of consciousness.
- Use emergency only for clearly urgent red-flag presentations.
- Do NOT invent vitals not present in the structured input.
- This is a demo triage assistant, not clinical care.
"""

_RISK_ASSESSMENT_PROMPT_ZH = """你根据用户描述和结构化信号评估健康咨询风险。

仅返回 JSON：
- risk_level：low、moderate、high、emergency 之一
- flags：简短 snake_case 关注点列表（可为空）
- reasoning：简短说明（不是诊断，不给用药建议）

注意胸痛、呼吸困难、中风征象、大出血、意识丧失等应谨慎处理。
不得编造结构化输入中不存在的生命体征数值。
"""


def _normalize_risk_level(value: str) -> RiskLevel:
    normalized = value.strip().lower()
    if normalized not in _RISK_LEVELS:
        return "low"
    return normalized  # type: ignore[return-value]


def _strip_markdown(text: str) -> str:
    cleaned = re.sub(r"```(?:json)?\s*", "", text)
    cleaned = re.sub(r"```", "", cleaned)
    return cleaned.strip()


class AiRiskAssessor(ABC):
    @abstractmethod
    def assess_risk(
        self,
        text: str,
        structured: StructuredHealthInput,
        language: Language = "en",
    ) -> RiskResult:
        pass


class MockAiRiskAssessor(AiRiskAssessor):
    """
    Simulated AI risk judgment for AI mode without OpenAI.

    Intentionally vitals-focused and optimistic on symptom-only text so the
    rule safety net can demonstrate catching missed major risks.
    """

    def assess_risk(
        self,
        text: str,
        structured: StructuredHealthInput,
        language: Language = "en",
    ) -> RiskResult:
        flags: list[str] = []
        level: RiskLevel = "low"

        if structured.systolic_bp is not None and structured.systolic_bp >= 180:
            level = "high"
            flags.append("very_high_systolic_bp")
        elif structured.systolic_bp is not None and structured.systolic_bp >= 140:
            level = "moderate"
            flags.append("elevated_blood_pressure")
        elif structured.heart_rate is not None and structured.heart_rate > 120:
            level = "high"
            flags.append("very_elevated_heart_rate")
        elif structured.heart_rate is not None and structured.heart_rate > 100:
            level = "moderate"
            flags.append("elevated_heart_rate")
        elif structured.mood in {"anxious", "stressed", "low"} or structured.sleep_quality == "poor":
            level = "moderate"
            if structured.mood in {"anxious", "stressed"}:
                flags.append("anxiety_or_stress_flag")
            if structured.mood == "low":
                flags.append("low_mood_flag")
            if structured.sleep_quality == "poor":
                flags.append("poor_sleep")

        if language == "zh":
            reasoning = (
                "模拟 AI 主要依据可量化的生命体征与情绪/睡眠信号评估风险；"
                "对仅描述症状而无数字的输入倾向于保守低估。"
            )
        else:
            reasoning = (
                "Simulated AI assessment focuses on quantified vitals and mood/sleep signals; "
                "symptom-only descriptions without numbers are often rated conservatively low."
            )

        if not flags:
            flags.append("ai_limited_signals")

        return RiskResult(risk_level=level, flags=flags, rule_explanation=reasoning)


class OpenAiRiskAssessor(AiRiskAssessor):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def assess_risk(
        self,
        text: str,
        structured: StructuredHealthInput,
        language: Language = "en",
    ) -> RiskResult:
        if language == "zh":
            user_prompt = (
                f"用户输入：{text}\n"
                f"结构化信号：{structured.model_dump_json()}\n"
                "请评估风险等级并返回 JSON。"
            )
            instructions = _RISK_ASSESSMENT_PROMPT_ZH
        else:
            user_prompt = (
                f"User input: {text}\n"
                f"Structured signals: {structured.model_dump_json()}\n"
                "Assess risk and return JSON."
            )
            instructions = _RISK_ASSESSMENT_PROMPT

        client = self._get_client()
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions=instructions,
            input=user_prompt,
        )
        payload = json.loads(_strip_markdown(response.output_text))
        level = _normalize_risk_level(str(payload.get("risk_level", "low")))
        flags = payload.get("flags") or []
        if not isinstance(flags, list):
            flags = []
        reasoning = str(payload.get("reasoning", "")).strip()
        if not reasoning:
            reasoning = "AI risk assessment completed."

        return RiskResult(
            risk_level=level,
            flags=[str(flag) for flag in flags],
            rule_explanation=reasoning,
        )


def get_ai_risk_assessor(require_openai: bool = False) -> tuple[AiRiskAssessor, str, str | None]:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            return OpenAiRiskAssessor(api_key=api_key), "openai", None
        except Exception as exc:
            if require_openai:
                raise ProviderConfigurationError from exc

    if require_openai:
        raise ProviderConfigurationError(
            "OPENAI_API_KEY is required for AI mode but is not configured."
        )

    return (
        MockAiRiskAssessor(),
        "mock-ai",
        "OPENAI_API_KEY missing; using simulated AI risk assessment.",
    )


def assess_with_rules_fallback(
    structured: StructuredHealthInput,
    text: str,
    language: Language,
) -> RiskResult:
    """Expose rule-only assessment for the safety net layer."""
    return evaluate_risk(structured, text, language=language)
