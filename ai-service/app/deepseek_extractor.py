"""DeepSeek-backed health signal extraction."""

import json

from app.deepseek_client import DeepSeekClient, strip_json_markdown
from app.extractor import (
    EXTRACTOR_SYSTEM_PROMPT,
    EXTRACTION_JSON_SCHEMA,
    BaseHealthExtractor,
    RegexFallbackExtractor,
    _finalize_extraction,
    _parse_field_evidence,
)
from app.schemas import StructuredHealthInput


class DeepSeekLLMExtractor(BaseHealthExtractor):
    """DeepSeek Chat Completions extractor with regex fallback on failure."""

    def __init__(self, client: DeepSeekClient):
        self.client = client
        self._fallback = RegexFallbackExtractor()

    def extract(self, text: str) -> StructuredHealthInput:
        system = (
            EXTRACTOR_SYSTEM_PROMPT
            + "\n\nReturn valid JSON only matching this schema:\n"
            + json.dumps(EXTRACTION_JSON_SCHEMA)
        )
        try:
            raw = self.client.chat(system=system, user=text, temperature=0)
            data = json.loads(strip_json_markdown(raw))
            field_evidence = _parse_field_evidence(data.pop("field_evidence", []))
            result = StructuredHealthInput(**data, extraction_evidence=field_evidence)
            return _finalize_extraction(text, result)
        except Exception:
            fallback = self._fallback.extract(text)
            return fallback.model_copy(
                update={
                    "extraction_confidence": "low",
                    "extraction_notes": (
                        "DeepSeek extraction failed; regex fallback was used. "
                        + (fallback.extraction_notes or "")
                    ).strip(),
                }
            )


def create_deepseek_extractor() -> DeepSeekLLMExtractor:
    return DeepSeekLLMExtractor(client=DeepSeekClient.from_env())
