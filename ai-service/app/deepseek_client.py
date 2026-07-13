"""Shared DeepSeek client helpers (OpenAI-compatible Chat Completions)."""

import os
import re

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from app.errors import AnalysisPipelineError, ProviderConfigurationError

DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"
DEFAULT_DEEPSEEK_TIMEOUT_SECONDS = 60.0


def deepseek_settings() -> tuple[str, str, str, float]:
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    base_url = os.getenv("DEEPSEEK_BASE_URL", DEFAULT_DEEPSEEK_BASE_URL).strip()
    model = os.getenv("DEEPSEEK_MODEL", DEFAULT_DEEPSEEK_MODEL).strip()
    timeout_raw = os.getenv(
        "DEEPSEEK_TIMEOUT_SECONDS", str(DEFAULT_DEEPSEEK_TIMEOUT_SECONDS)
    )
    timeout = float(timeout_raw)
    return api_key, base_url, model, timeout


def require_deepseek_api_key() -> str:
    api_key, _, _, _ = deepseek_settings()
    if not api_key:
        raise ProviderConfigurationError(
            "DEEPSEEK_API_KEY is required when using DeepSeek provider."
        )
    return api_key


def strip_json_markdown(text: str) -> str:
    cleaned = re.sub(r"```(?:json)?\s*", "", text)
    cleaned = re.sub(r"```", "", cleaned)
    return cleaned.strip()


def map_deepseek_error(exc: Exception) -> AnalysisPipelineError:
    if isinstance(exc, APITimeoutError):
        return AnalysisPipelineError("DeepSeek request timed out.")
    if isinstance(exc, AuthenticationError):
        return AnalysisPipelineError("DeepSeek authentication failed.")
    if isinstance(exc, RateLimitError):
        return AnalysisPipelineError("DeepSeek rate limit exceeded.")
    if isinstance(exc, APIStatusError):
        status = exc.status_code
        if status == 402:
            return AnalysisPipelineError("DeepSeek account balance is insufficient.")
        if status == 429:
            return AnalysisPipelineError("DeepSeek rate limit exceeded.")
        if status >= 500:
            return AnalysisPipelineError("DeepSeek service is temporarily unavailable.")
        return AnalysisPipelineError("DeepSeek request failed.")
    if isinstance(exc, APIConnectionError):
        return AnalysisPipelineError("Could not connect to DeepSeek.")
    return AnalysisPipelineError("DeepSeek request failed.")


class DeepSeekClient:
    """Lazy OpenAI SDK client configured for DeepSeek."""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_DEEPSEEK_BASE_URL,
        model: str = DEFAULT_DEEPSEEK_MODEL,
        timeout: float = DEFAULT_DEEPSEEK_TIMEOUT_SECONDS,
    ):
        if not api_key.strip():
            raise ProviderConfigurationError(
                "DEEPSEEK_API_KEY is required when using DeepSeek provider."
            )
        self.api_key = api_key.strip()
        self.base_url = base_url.strip() or DEFAULT_DEEPSEEK_BASE_URL
        self.model = model.strip() or DEFAULT_DEEPSEEK_MODEL
        self.timeout = timeout
        self._client: OpenAI | None = None

    @classmethod
    def from_env(cls) -> "DeepSeekClient":
        api_key = require_deepseek_api_key()
        _, base_url, model, timeout = deepseek_settings()
        return cls(api_key=api_key, base_url=base_url, model=model, timeout=timeout)

    def _get_client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
            )
        return self._client

    @staticmethod
    def extract_message_content(response) -> str:
        choices = getattr(response, "choices", None) or []
        if not choices:
            raise AnalysisPipelineError("DeepSeek returned empty choices.")

        message = choices[0].message
        content = getattr(message, "content", None)
        if content is None or not str(content).strip():
            raise AnalysisPipelineError("DeepSeek returned empty content.")

        # reasoning_content must never be surfaced to callers.
        return str(content)

    def chat(self, system: str, user: str, *, temperature: float = 0) -> str:
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return self.extract_message_content(response)
        except AnalysisPipelineError:
            raise
        except Exception as exc:
            raise map_deepseek_error(exc) from exc
