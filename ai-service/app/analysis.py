"""Health text analysis pipeline."""

from app.ai_risk_service import assess_with_rules_fallback, get_ai_risk_assessor
from app.errors import AnalysisPipelineError, ProviderConfigurationError
from app.escalation import build_escalation, elevate_risk_for_emergency
from app.extractor import get_extractor_for_mode
from app.localization import localize_provider_warning, localize_structured_input
from app.llm_service import get_llm_provider_name_for_mode, get_llm_service_for_mode
from app.risk_adjudication import (
    adjudication_from_rules_only,
    apply_emergency_to_adjudication,
    merge_ai_and_rule_risk,
)
from app.risk_rules import evaluate_risk
from app.safety_validator import validate_llm_output
from app.schemas import AnalysisMode, AnalysisResponse, Language


def run_analysis(
    text: str,
    language: Language = "en",
    mode: AnalysisMode = "mock",
) -> AnalysisResponse:
    """
    Run extraction, risk adjudication, escalation, explanation, and safety validation.

    mock mode: deterministic rules adjudicate risk.
    ai mode: AI adjudicates risk first; rules act as a safety net for missed major risks.

    Raises ProviderConfigurationError or AnalysisPipelineError on provider failures.
    """
    try:
        extractor, extractor_provider, extractor_warning = get_extractor_for_mode(mode)
        structured = localize_structured_input(extractor.extract(text), language)
        rule_risk = assess_with_rules_fallback(structured, text, language)

        provider_warnings: list[str] = []
        if extractor_warning:
            provider_warnings.append(extractor_warning)

        if mode in {"ai", "openai", "deepseek"}:
            ai_assessor, _, ai_warning = get_ai_risk_assessor(
                require_openai=False,
                mode=mode,
            )
            if ai_warning:
                provider_warnings.append(ai_warning)
            ai_risk = ai_assessor.assess_risk(text, structured, language=language)
            risk_result, adjudication = merge_ai_and_rule_risk(
                ai_risk, rule_risk, language, mode
            )
            llm_provider_label = get_llm_provider_name_for_mode(mode)
        else:
            risk_result = evaluate_risk(structured, text, language=language)
            adjudication = adjudication_from_rules_only(risk_result, mode)
            llm_provider_label = get_llm_provider_name_for_mode(mode)

        escalation = build_escalation(text, risk_result.risk_level, language=language)
        risk_result = elevate_risk_for_emergency(risk_result, escalation, language=language)
        adjudication = apply_emergency_to_adjudication(
            adjudication.model_copy(update={"final_risk_level": risk_result.risk_level}),
            risk_result.risk_level,
            language,
        )

        llm = get_llm_service_for_mode(mode)
        explanation = llm.generate_explanation(
            structured,
            risk_result,
            text,
            language=language,
            adjudication=adjudication,
        )
        safety_check = validate_llm_output(explanation, language=language)

        combined_warning = " ".join(provider_warnings).strip() or None

        return AnalysisResponse(
            structured_input=structured,
            risk_result=risk_result,
            escalation=escalation,
            explanation=explanation,
            safety_check=safety_check,
            extractor_provider=extractor_provider,
            llm_provider=llm_provider_label,
            analysis_mode=mode,
            risk_adjudication=adjudication,
            provider_warning=localize_provider_warning(combined_warning, language),
        )
    except ProviderConfigurationError:
        raise
    except Exception as exc:
        raise AnalysisPipelineError from exc
