from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI PR Review Service"
    environment: str = "development"

    database_url: str          # required: app refuses to start without it
    github_token: str = ""
    gemini_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()