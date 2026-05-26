from __future__ import annotations
from functools import lru_cache
try:
    # Python 3.9+
    from typing import Annotated, List, Union  # type: ignore
except ImportError:  # pragma: no cover
    # Python <3.9
    from typing_extensions import Annotated
    from typing import List, Union

from pydantic import AnyUrl, BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _assemble_cors_origins(value: Union[str, List[str]]) -> List[str]:
    if isinstance(value, str):
        if value == "*":
            return ["*"]
        return [origin.strip() for origin in value.split(",") if origin.strip()]
    return value


CorsOrigins = Annotated[List[str], BeforeValidator(_assemble_cors_origins)]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=True,
    )

    PROJECT_NAME: str = "Gamma HRMS Python Backend Module"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    DATABASE_URL: AnyUrl = "postgresql+asyncpg://postgres:postgres@localhost:5432/gamma_hrms"
    BACKEND_CORS_ORIGINS: CorsOrigins = ["*"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
