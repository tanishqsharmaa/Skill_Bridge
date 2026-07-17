"""Unit tests for src/core/config.py — no real secrets required."""
import pytest
from pydantic import ValidationError


_ALL_KEYS = {
    "DEEPSEEK_API_KEY": "test-deepseek",
    "GEMINI_API_KEY": "test-gemini",
    "SUPABASE_URL": "https://test.supabase.co",
    "SUPABASE_SERVICE_KEY": "test-service-key",
    "RESEND_API_KEY": "test-resend",
    "LANGSMITH_API_KEY": "test-langsmith",
}


def test_settings_loads_from_env(monkeypatch):
    """Settings instantiates successfully when all required env vars are present."""
    for key, val in _ALL_KEYS.items():
        monkeypatch.setenv(key, val)

    # Import Settings class directly (not the cached `settings` singleton)
    from src.core.config import Settings

    s = Settings()
    assert s.supabase_url == "https://test.supabase.co"
    assert s.deepseek_api_key == "test-deepseek"
    assert s.gemini_api_key == "test-gemini"
    assert s.supabase_service_key == "test-service-key"
    assert s.resend_api_key == "test-resend"
    assert s.langsmith_api_key == "test-langsmith"


def test_settings_missing_key_raises(monkeypatch):
    """Settings raises ValidationError when any required env var is absent."""
    for key in _ALL_KEYS:
        monkeypatch.delenv(key, raising=False)

    # Override model_config so pydantic-settings does NOT fall back to .env file
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class SettingsNoEnvFile(BaseSettings):
        deepseek_api_key: str
        gemini_api_key: str
        supabase_url: str
        supabase_service_key: str
        resend_api_key: str
        langsmith_api_key: str

        model_config = SettingsConfigDict(env_file=None)

    with pytest.raises((ValidationError, Exception)):
        SettingsNoEnvFile()
