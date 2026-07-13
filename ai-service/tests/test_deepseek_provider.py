"""Automated tests for DeepSeek providers (all API calls mocked)."""

import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from openai import APIStatusError, APITimeoutError, AuthenticationError, RateLimitError

from app.ai_risk_service import get_ai_risk_assessor
from app.analysis import run_analysis
from app.deepseek_client import DeepSeekClient, require_deepseek_api_key
from app.deepseek_extractor import DeepSeekLLMExtractor, create_deepseek_extractor
from app.deepseek_llm_service import DeepSeekLLMService, create_deepseek_llm_service
from app.deepseek_risk_service import DeepSeekRiskAssessor, create_deepseek_risk_assessor
from app.errors import AnalysisPipelineError, ProviderConfigurationError
from app.extractor import get_extractor_for_mode
from app.llm_service import get_llm_provider_name, get_llm_service, get_llm_service_for_mode
from app.schemas import RiskResult, StructuredHealthInput


def _sample_risk() -> RiskResult:
    return RiskResult(
        risk_level="moderate",
        flags=["elevated_heart_rate"],
        rule_explanation="test",
    )


def _sample_structured() -> StructuredHealthInput:
    return StructuredHealthInput(heart_rate=110)


def _chat_response(content: str | None, reasoning: str | None = None):
    message = SimpleNamespace(content=content, reasoning_content=reasoning)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def _deepseek_client() -> DeepSeekClient:
    return DeepSeekClient(api_key="test-deepseek-key")


def test_get_llm_service_selects_deepseek(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-deepseek-key")

    service = get_llm_service()
    assert isinstance(service, DeepSeekLLMService)


def test_get_llm_service_for_mode_deepseek(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-deepseek-key")

    service = get_llm_service_for_mode("deepseek")
    assert isinstance(service, DeepSeekLLMService)


def test_get_extractor_for_mode_deepseek(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-deepseek-key")

    extractor, provider, warning = get_extractor_for_mode("deepseek")
    assert isinstance(extractor, DeepSeekLLMExtractor)
    assert provider == "deepseek"
    assert warning is None


def test_get_ai_risk_assessor_for_deepseek_mode(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-deepseek-key")

    assessor, provider, warning = get_ai_risk_assessor(mode="deepseek")
    assert isinstance(assessor, DeepSeekRiskAssessor)
    assert provider == "deepseek"
    assert warning is None


def test_missing_deepseek_api_key_raises(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")

    with pytest.raises(ProviderConfigurationError) as exc:
        require_deepseek_api_key()

    message = str(exc.value)
    assert "DEEPSEEK_API_KEY" in message
    assert "sk-" not in message


def test_create_deepseek_uses_env_defaults(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-deepseek-key")
    monkeypatch.delenv("DEEPSEEK_BASE_URL", raising=False)
    monkeypatch.delenv("DEEPSEEK_MODEL", raising=False)
    monkeypatch.delenv("DEEPSEEK_TIMEOUT_SECONDS", raising=False)

    client = DeepSeekClient.from_env()
    assert client.base_url == "https://api.deepseek.com"
    assert client.model == "deepseek-v4-flash"
    assert client.timeout == 60.0


@patch.object(DeepSeekClient, "chat")
def test_deepseek_returns_message_content(mock_chat, monkeypatch):
    mock_chat.return_value = "Your heart rate is slightly elevated."

    service = DeepSeekLLMService(client=_deepseek_client())
    explanation = service.generate_explanation(
        _sample_structured(),
        _sample_risk(),
        source_text="heart rate 110",
        language="en",
    )

    assert "Your heart rate is slightly elevated." in explanation
    assert "not a medical diagnosis" in explanation.lower()


@patch.object(DeepSeekClient, "chat")
def test_deepseek_ignores_reasoning_content(mock_chat, monkeypatch):
    mock_chat.return_value = "Visible health summary."

    service = DeepSeekLLMService(client=_deepseek_client())
    explanation = service.generate_explanation(
        _sample_structured(),
        _sample_risk(),
        source_text="heart rate 110",
        language="en",
    )

    assert "Visible health summary." in explanation
    assert "chain-of-thought" not in explanation


@patch.object(DeepSeekClient, "chat")
def test_deepseek_extractor_parses_json(mock_chat):
    payload = {
        "heart_rate": 110,
        "systolic_bp": None,
        "diastolic_bp": None,
        "mood": None,
        "sleep_quality": None,
        "symptoms": [],
        "extraction_confidence": "high",
        "missing_or_ambiguous_fields": [],
        "extraction_notes": None,
        "field_evidence": [],
    }
    mock_chat.return_value = json.dumps(payload)

    extractor = DeepSeekLLMExtractor(client=_deepseek_client())
    result = extractor.extract("heart rate 110")

    assert result.heart_rate == 110
    assert result.extraction_confidence == "high"


@patch.object(DeepSeekClient, "chat")
def test_deepseek_risk_assessor_parses_json(mock_chat):
    mock_chat.return_value = json.dumps(
        {
            "risk_level": "moderate",
            "flags": ["elevated_heart_rate"],
            "reasoning": "Heart rate is above normal.",
        }
    )

    assessor = DeepSeekRiskAssessor(client=_deepseek_client())
    result = assessor.assess_risk(
        "heart rate 110",
        _sample_structured(),
        language="en",
    )

    assert result.risk_level == "moderate"
    assert "elevated_heart_rate" in result.flags


@patch("app.deepseek_llm_service.create_deepseek_llm_service")
@patch("app.deepseek_risk_service.create_deepseek_risk_assessor")
@patch("app.deepseek_extractor.create_deepseek_extractor")
def test_run_analysis_deepseek_mode_uses_deepseek_providers(
    mock_create_extractor,
    mock_create_assessor,
    mock_create_llm,
    monkeypatch,
):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-deepseek-key")

    mock_extractor = MagicMock()
    mock_extractor.extract.return_value = StructuredHealthInput(heart_rate=110)
    mock_create_extractor.return_value = mock_extractor

    mock_assessor = MagicMock()
    mock_assessor.assess_risk.return_value = RiskResult(
        risk_level="moderate",
        flags=["elevated_heart_rate"],
        rule_explanation="DeepSeek risk assessment completed.",
    )
    mock_create_assessor.return_value = mock_assessor

    mock_llm = MagicMock()
    mock_llm.generate_explanation.return_value = (
        "Your heart rate is slightly elevated. This is not a medical diagnosis."
    )
    mock_create_llm.return_value = mock_llm

    result = run_analysis("heart rate 110", language="en", mode="deepseek")

    mock_create_extractor.assert_called_once()
    mock_create_assessor.assert_called_once()
    mock_create_llm.assert_called_once()
    assert result.analysis_mode == "deepseek"
    assert result.extractor_provider == "deepseek"
    assert result.llm_provider == "deepseek"


@patch.object(DeepSeekClient, "_get_client")
def test_deepseek_empty_choices_raises(mock_get_client):
    client = MagicMock()
    mock_get_client.return_value = client
    client.chat.completions.create.return_value = SimpleNamespace(choices=[])

    service = DeepSeekLLMService(client=_deepseek_client())
    with pytest.raises(AnalysisPipelineError, match="empty choices"):
        service.generate_explanation(
            _sample_structured(),
            _sample_risk(),
            source_text="heart rate 110",
        )


@patch.object(DeepSeekClient, "chat")
def test_deepseek_empty_content_raises(mock_chat):
    mock_chat.side_effect = AnalysisPipelineError("DeepSeek returned empty content.")

    service = DeepSeekLLMService(client=_deepseek_client())
    with pytest.raises(AnalysisPipelineError, match="empty content"):
        service.generate_explanation(
            _sample_structured(),
            _sample_risk(),
            source_text="heart rate 110",
        )


@patch.object(DeepSeekClient, "_get_client")
def test_deepseek_timeout(mock_get_client):
    client = MagicMock()
    mock_get_client.return_value = client
    client.chat.completions.create.side_effect = APITimeoutError(request=MagicMock())

    service = DeepSeekLLMService(client=_deepseek_client())
    with pytest.raises(AnalysisPipelineError, match="timed out"):
        service.generate_explanation(
            _sample_structured(),
            _sample_risk(),
            source_text="heart rate 110",
        )


@patch.object(DeepSeekClient, "_get_client")
def test_deepseek_authentication_error(mock_get_client):
    client = MagicMock()
    mock_get_client.return_value = client
    client.chat.completions.create.side_effect = AuthenticationError(
        "invalid key",
        response=MagicMock(status_code=401),
        body=None,
    )

    service = DeepSeekLLMService(client=_deepseek_client())
    with pytest.raises(AnalysisPipelineError, match="authentication failed"):
        service.generate_explanation(
            _sample_structured(),
            _sample_risk(),
            source_text="heart rate 110",
        )


@patch.object(DeepSeekClient, "_get_client")
def test_deepseek_insufficient_balance(mock_get_client):
    client = MagicMock()
    mock_get_client.return_value = client
    client.chat.completions.create.side_effect = APIStatusError(
        "payment required",
        response=MagicMock(status_code=402),
        body=None,
    )

    service = DeepSeekLLMService(client=_deepseek_client())
    with pytest.raises(AnalysisPipelineError, match="balance"):
        service.generate_explanation(
            _sample_structured(),
            _sample_risk(),
            source_text="heart rate 110",
        )


@patch.object(DeepSeekClient, "_get_client")
def test_deepseek_rate_limit(mock_get_client):
    client = MagicMock()
    mock_get_client.return_value = client
    client.chat.completions.create.side_effect = RateLimitError(
        "rate limit",
        response=MagicMock(status_code=429),
        body=None,
    )

    service = DeepSeekLLMService(client=_deepseek_client())
    with pytest.raises(AnalysisPipelineError, match="rate limit"):
        service.generate_explanation(
            _sample_structured(),
            _sample_risk(),
            source_text="heart rate 110",
        )


@patch.object(DeepSeekClient, "_get_client")
def test_deepseek_upstream_5xx(mock_get_client):
    client = MagicMock()
    mock_get_client.return_value = client
    client.chat.completions.create.side_effect = APIStatusError(
        "server error",
        response=MagicMock(status_code=503),
        body=None,
    )

    service = DeepSeekLLMService(client=_deepseek_client())
    with pytest.raises(AnalysisPipelineError, match="temporarily unavailable"):
        service.generate_explanation(
            _sample_structured(),
            _sample_risk(),
            source_text="heart rate 110",
        )


def test_unknown_llm_provider_raises(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")

    with pytest.raises(ProviderConfigurationError, match="Unknown LLM_PROVIDER"):
        get_llm_service()


def test_unknown_analysis_mode_raises(monkeypatch):
    with pytest.raises(ProviderConfigurationError, match="Unknown analysis mode"):
        get_llm_service_for_mode("unknown-provider")


def test_get_llm_provider_name_deepseek(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    assert get_llm_provider_name() == "deepseek"
