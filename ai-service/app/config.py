"""Application configuration from environment variables."""

import os

SERVICE_NAME = "healthlens-ai-service"

APP_VERSION = os.getenv("APP_VERSION", "dev")
APP_ENV = os.getenv("APP_ENV", "development")

EXTRACTOR_PROVIDER = os.getenv("EXTRACTOR_PROVIDER", "mock").lower()
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock").lower()

DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
DEEPSEEK_TIMEOUT_SECONDS = float(os.getenv("DEEPSEEK_TIMEOUT_SECONDS", "60"))

ANALYSE_TIMEOUT_SECONDS = float(os.getenv("ANALYSE_TIMEOUT_SECONDS", "30"))
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "5000"))


def is_openai_provider_misconfigured() -> bool:
    """True when OpenAI is requested but no API key is available."""
    if not os.getenv("OPENAI_API_KEY"):
        return EXTRACTOR_PROVIDER == "openai" or LLM_PROVIDER == "openai"
    return False


def is_deepseek_provider_misconfigured() -> bool:
    """True when DeepSeek is requested but no API key is available."""
    if not os.getenv("DEEPSEEK_API_KEY", "").strip():
        return (
            EXTRACTOR_PROVIDER == "deepseek"
            or LLM_PROVIDER == "deepseek"
        )
    return False


def is_provider_misconfigured() -> bool:
    """True when a configured paid provider is missing required credentials."""
    return is_openai_provider_misconfigured() or is_deepseek_provider_misconfigured()
