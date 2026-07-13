"""DeepSeek Chat Completions LLM explanation provider."""

from app.deepseek_client import DeepSeekClient
from app.llm_service import (
    LLMService,
    _compose_disclaimer,
    _compose_risk_level_guidance,
    _strip_markdown,
    build_explanation_prompts,
)
from app.schemas import Language, RiskAdjudication, RiskResult, StructuredHealthInput


class DeepSeekLLMService(LLMService):
    """DeepSeek Chat Completions provider using the OpenAI Python SDK."""

    def __init__(self, client: DeepSeekClient):
        self.client = client

    def generate_explanation(
        self,
        structured: StructuredHealthInput,
        risk: RiskResult,
        source_text: str = "",
        language: Language = "en",
        adjudication: RiskAdjudication | None = None,
    ) -> str:
        instructions, user_prompt = build_explanation_prompts(
            structured, risk, source_text, language
        )
        llm_summary = _strip_markdown(
            self.client.chat(system=instructions, user=user_prompt)
        )

        parts = [llm_summary]
        parts.extend(
            _compose_risk_level_guidance(
                risk.risk_level,
                risk.flags,
                source_text,
                language,
            )
        )
        parts.append(_compose_disclaimer(risk.risk_level, language))
        return _strip_markdown(" ".join(parts))


def create_deepseek_llm_service() -> DeepSeekLLMService:
    return DeepSeekLLMService(client=DeepSeekClient.from_env())
