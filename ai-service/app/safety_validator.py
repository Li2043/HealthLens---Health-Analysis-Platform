"""Validate LLM output for safety compliance."""

from app.schemas import Language, SafetyCheck

DISCLAIMER_PHRASE_EN = "not a medical diagnosis"
DISCLAIMER_PHRASE_ZH = "这不是医疗诊断"

DIAGNOSTIC_PHRASES_EN = [
    "you have hypertension",
    "you have heart disease",
    "you are diagnosed with",
]

DIAGNOSTIC_PHRASES_ZH = [
    "你患有",
    "你已确诊",
    "你被确诊",
    "确诊患有",
]

MEDICATION_PHRASES_EN = [
    "take medication",
    "you should take medicine",
    "you should take medication",
]

MEDICATION_PHRASES_ZH = [
    "服用药物",
    "应该吃药",
    "应当用药",
    "用药建议",
]


def _contains_disclaimer(text: str, language: Language | None = None) -> bool:
    if language == "zh":
        return DISCLAIMER_PHRASE_ZH in text
    if language == "en":
        return DISCLAIMER_PHRASE_EN in text.lower()
    return DISCLAIMER_PHRASE_ZH in text or DISCLAIMER_PHRASE_EN in text.lower()


def _contains_diagnostic_language(text: str, language: Language | None = None) -> bool:
    lower = text.lower()
    if language == "zh":
        return any(phrase in text for phrase in DIAGNOSTIC_PHRASES_ZH)
    if language == "en":
        return any(phrase in lower for phrase in DIAGNOSTIC_PHRASES_EN)
    return any(phrase in text for phrase in DIAGNOSTIC_PHRASES_ZH) or any(
        phrase in lower for phrase in DIAGNOSTIC_PHRASES_EN
    )


def _contains_medication_advice(text: str, language: Language | None = None) -> bool:
    lower = text.lower()
    if language == "zh":
        return any(phrase in text for phrase in MEDICATION_PHRASES_ZH)
    if language == "en":
        return any(phrase in lower for phrase in MEDICATION_PHRASES_EN)
    return any(phrase in text for phrase in MEDICATION_PHRASES_ZH) or any(
        phrase in lower for phrase in MEDICATION_PHRASES_EN
    )


def validate_llm_output(text: str, language: Language | None = None) -> SafetyCheck:
    """Check that LLM explanation is safe and includes the required disclaimer."""
    contains_disclaimer = _contains_disclaimer(text, language)
    contains_diagnostic_language = _contains_diagnostic_language(text, language)
    contains_medication_advice = _contains_medication_advice(text, language)
    passed = (
        contains_disclaimer
        and not contains_diagnostic_language
        and not contains_medication_advice
    )

    return SafetyCheck(
        contains_disclaimer=contains_disclaimer,
        contains_diagnostic_language=contains_diagnostic_language,
        contains_medication_advice=contains_medication_advice,
        passed=passed,
    )
