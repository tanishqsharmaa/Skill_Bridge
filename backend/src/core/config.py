from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    deepseek_api_key: str
    gemini_api_key: str
    supabase_url: str
    supabase_service_key: str
    resend_api_key: str
    langsmith_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
