from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('ENV', 'development')}"
    )

settings = Settings()