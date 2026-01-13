from pydantic import BaseModel
from typing import Dict, Any, Optional


class BaseAgentMessage(BaseModel):
    """Базовое сообщение для коммуникации между агентами"""
    user_id: str
    session_id: str
    intent: str
    message: str
    context: Dict[str, Any]
    agent_response: Optional[Dict[str, Any]] = None


class UserProfile(BaseModel):
    """Профиль пользователя"""
    user_id: str
    grades: Dict[str, float]  # предмет: оценка
    interests: list[str]
    target_universities: list[str]
    preferred_cities: list[str]
    test_scores: Dict[str, float]  # тип теста: балл


class UniversityInfo(BaseModel):
    """Информация о университете"""
    name: str
    city: str
    programs: list[str]
    entry_requirements: Dict[str, float]  # предмет: минимальный балл
    application_deadlines: Dict[str, str]  # тип заявки: дата