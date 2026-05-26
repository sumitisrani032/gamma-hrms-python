from functools import lru_cache
from typing import Annotated

from pydantic import AnyUrl, BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _assemble_cors_origins(value: str | list[str]) -> list[str]:
    if isinstance(value, str):
        if value == "*":
            return ["*"]
        return [origin.strip() for origin in value.split(",") if origin.strip()]
    return value


CorsOrigins = Annotated[list[str], BeforeValidator(_assemble_cors_origins)]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=True,
    )

    PROJECT_NAME: str
    API_V1_STR: str
    ENVIRONMENT: str
    DEBUG: bool
    PORT: int
    HOST: str

    DATABASE_URL: AnyUrl
    BACKEND_CORS_ORIGINS: CorsOrigins
    SECRET_KEY_BASE: str


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
