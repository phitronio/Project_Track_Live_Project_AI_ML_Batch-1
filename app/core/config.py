from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    APP_NAME: str = "Sales Agent"
    DEBUG: bool = False

    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: SecretStr = SecretStr("postgres")
    DB_NAME: str = "sales_agent"
    DB_SCHEMA: str = "sales_agent"

    GEMINI_API_KEY: SecretStr = SecretStr("")
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    
    EMBEDDINGS_URL: str = "http://127.0.0.1:8090"

    @property
    def DATABASE_URL(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.DB_USER,
            password=self.DB_PASSWORD.get_secret_value(),
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings():
    return Settings()
