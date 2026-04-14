from typing import Any

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from src.agents.base_agent import BaseAgent
from src.config import settings
from src.models.base import BaseAgentMessage


class ProfileAnalyzerAgent(BaseAgent):
    """Агент для анализа профиля студента и рекомендаций"""

    def __init__(self) -> None:
        super().__init__()
        self.llm = ChatOpenAI(
            model_name=settings.openai_model,
            openai_api_key=SecretStr(settings.openai_api_key),
            openai_api_base=str(settings.openai_base_url),
            max_tokens=600,
            request_timeout=settings.request_timeout_seconds,
        )

    def can_handle(self, intent: str) -> bool:
        return intent in ["profile_analysis", "recommendations", "fit_assessment"]

    async def process(self, message: BaseAgentMessage) -> BaseAgentMessage:
        """Анализирует профиль пользователя и дает рекомендации"""

        # Извлекаем данные профиля из контекста
        user_profile = message.context.get("user_profile", {})

        if message.intent == "profile_analysis":
            response = await self._analyze_profile(user_profile)
        elif message.intent == "recommendations":
            response = await self._get_recommendations(user_profile)
        elif message.intent == "fit_assessment":
            response = await self._assess_fit(user_profile, message.message)
        else:
            response = "Извините, я не понял ваш запрос о профиле"

        message.agent_response = {
            "agent": self.name,
            "response": response,
            "next_steps": ["profile_analysis", "university_search"],
            "confidence": 0.85,
        }
        return message

    async def _analyze_profile(self, profile: dict[str, Any]) -> str:
        """Анализирует профиль пользователя"""

        if not profile:
            return """
            Чтобы проанализировать ваш профиль, мне нужна информация о вас.

            Пожалуйста, предоставьте:
            📊 **Академические данные:**
            - Ваши оценки по предметам
            - Результаты ЕГЭ (если уже сдавали)

            🎯 **Интересы:**
            - Какие предметы вам нравятся
            - Карьерные интересы

            🏙️ **Предпочтения:**
            - Желаемые города для обучения
            - Предпочтения по типу университета

            Например: "У меня 5 по математике, 4 по физике, хочу стать программистом"
            """

        prompt = f"""
        Проанализируй профиль студента и дай оценку его шансов на поступление.

        Профиль пользователя: {profile}

        Предоставь структурированный анализ:
        - Расчет среднего балла
        - Оценка сильных и слабых сторон
        - Предварительная оценка шансов на поступление
        - Рекомендации по улучшению
        """

        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return str(response.content)
        except Exception as e:
            return f"Ошибка анализа профиля: {e}"

    async def _get_recommendations(self, profile: dict[str, Any]) -> str:
        """Дает рекомендации на основе профиля"""

        if not profile:
            return (
                "Пожалуйста, сначала предоставьте информацию о вашем профиле "
                "для получения рекомендаций."
            )

        prompt = f"""
        На основе профиля студента дай рекомендации по:
        - Подходящим университетам
        - Программам обучения
        - Плану подготовки

        Профиль: {profile}

        Будь конкретным и дай практические советы.
        """

        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return str(response.content)
        except Exception as e:
            return f"Ошибка получения рекомендаций: {e}"

    async def _assess_fit(self, profile: dict[str, Any], university_query: str) -> str:
        """Оценивает соответствие профиля конкретному университету"""

        if not profile:
            return "Пожалуйста, сначала предоставьте информацию о вашем профиле."

        prompt = f"""
        Оцени, насколько профиль студента подходит для поступления в университет по запросу.

        Профиль студента: {profile}
        Запрос университета: {university_query}

        Дай оценку по шкале 1-10 и конкретные рекомендации.
        """

        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return str(response.content)
        except Exception as e:
            return f"Ошибка оценки соответствия: {e}"

    def calculate_gpa(self, grades: dict[str, float]) -> float:
        """Рассчитывает средний балл"""
        if not grades:
            return 0.0
        return sum(grades.values()) / len(grades)

    def identify_strengths(self, grades: dict[str, float]) -> list[str]:
        """Определяет сильные стороны"""
        if not grades:
            return []

        strong_subjects = []
        for subject, grade in grades.items():
            if grade >= 4.5:  # Оценка 4.5 и выше считается сильной стороной
                strong_subjects.append(subject)

        return strong_subjects

    def identify_weaknesses(self, grades: dict[str, float]) -> list[str]:
        """Определяет слабые стороны"""
        if not grades:
            return []

        weak_subjects = []
        for subject, grade in grades.items():
            if grade < 3.5:  # Оценка ниже 3.5 считается слабой стороной
                weak_subjects.append(subject)

        return weak_subjects
