from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI PR Review Service"
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()