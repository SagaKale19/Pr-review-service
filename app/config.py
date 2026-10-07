from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI PR Review Service"
    environment: str = "development"

    database_url: str          # required: app refuses to start without it
    github_token: str = ""
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"
    gemini_fallback_models: str = ""   # comma-separated
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()