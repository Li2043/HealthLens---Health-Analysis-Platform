"""DeepSeek-backed AI risk assessment."""

import json

from app.ai_risk_service import (
    AiRiskAssessor,
    _RISK_ASSESSMENT_PROMPT,
    _RISK_ASSESSMENT_PROMPT_ZH,
    _normalize_risk_level,
)
from app.deepseek_client import DeepSeekClient, strip_json_markdown
from app.schemas import Language, RiskResult, StructuredHealthInput


class DeepSeekRiskAssessor(AiRiskAssessor):
    def __init__(self, client: DeepSeekClient):
        self.client = client

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

        raw = self.client.chat(system=instructions, user=user_prompt, temperature=0)
        payload = json.loads(strip_json_markdown(raw))
        level = _normalize_risk_level(str(payload.get("risk_level", "low")))
        flags = payload.get("flags") or []
        if not isinstance(flags, list):
            flags = []
        reasoning = str(payload.get("reasoning", "")).strip()
        if not reasoning:
            reasoning = "DeepSeek risk assessment completed."

        return RiskResult(
            risk_level=level,
            flags=[str(flag) for flag in flags],
            rule_explanation=reasoning,
        )


def create_deepseek_risk_assessor() -> DeepSeekRiskAssessor:
    return DeepSeekRiskAssessor(client=DeepSeekClient.from_env())
