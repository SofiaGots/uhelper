"""Конфигурация приложения с валидацией через Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import AnyUrl, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Глобальные настройки приложения, подтягиваются из окружения/.env."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", case_sensitive=False)

    environment: Literal["development", "production", "testing"] = Field(
        default="development", description="Текущий режим работы приложения"
    )

    telegram_bot_token: str = Field(min_length=10, alias="TELEGRAM_BOT_TOKEN")

    openai_api_key: str = Field(min_length=10, alias="OPENAI_API_KEY")
    openai_project_id: str | None = Field(default=None, alias="OPENAI_PROJECT_ID")
    openai_base_url: AnyUrl = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")
    openai_model: str = Field(default="gpt-3.5-turbo", alias="OPENAI_MODEL")

    database_url: str = Field(default="sqlite:///uhelper.db", alias="DATABASE_URL")
    redis_url: str | None = Field(default=None, alias="REDIS_URL")

    request_timeout_seconds: int = Field(default=15, ge=1, le=60)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Возвращает кэшированный объект настроек, валидирует на старте."""
    try:
        return Settings()  # type: ignore
    except ValidationError as exc:
        # Оставляем читаемую ошибку, чтобы рантайм упал раньше с понятным сообщением
        missing: set[str] = {
            str(err["loc"][0]) for err in exc.errors() if err["type"] == "missing"
        }
        details = "; ".join(str(e) for e in exc.errors())
        raise RuntimeError(
            f"Конфигурация невалидна. Отсутствуют/некорректны: {', '.join(missing)}. "
            f"Детали: {details}"
        ) from exc


settings = get_settings()
