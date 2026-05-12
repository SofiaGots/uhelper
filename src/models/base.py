from typing import Any

from pydantic import BaseModel, field_validator

from src.utils.text_sanitizer import sanitize_user_text


class BaseAgentMessage(BaseModel):
    """Базовое сообщение для коммуникации между агентами"""

    user_id: str
    session_id: str
    intent: str
    message: str
    context: dict[str, Any]
    agent_response: dict[str, Any] | None = None

    @field_validator("message", mode="before")
    @classmethod
    def validate_message(cls, value: str) -> str:
        """Валидирует и очищает пользовательский текст.

        Args:
            value: Сырой текст сообщения.

        Returns:
            Очищенный текст.

        Raises:
            ValueError: Если текст пустой или язык не поддерживается.
        """

        return sanitize_user_text(str(value))


class UserProfile(BaseModel):
    """Профиль пользователя"""

    user_id: str
    grades: dict[str, float]  # предмет: оценка
    interests: list[str]
    target_universities: list[str]
    preferred_cities: list[str]
    test_scores: dict[str, float]  # тип теста: балл


class UniversityInfo(BaseModel):
    """Информация о университете"""

    name: str
    city: str
    programs: list[str]
    entry_requirements: dict[str, float]  # предмет: минимальный балл
    application_deadlines: dict[str, str]  # тип заявки: дата
