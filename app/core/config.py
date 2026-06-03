from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    ENV: str = "development"
    APP_VERSION: str = "2.0.0"
    RELEASE_CHANNEL: str = "stable"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()