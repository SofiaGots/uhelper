from typing import Any

from pydantic import BaseModel


class BaseAgentMessage(BaseModel):
    """Базовое сообщение для коммуникации между агентами"""

    user_id: str
    session_id: str
    intent: str
    message: str
    context: dict[str, Any]
    agent_response: dict[str, Any] | None = None


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
