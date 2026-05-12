import logging
from collections.abc import Sequence
from typing import Any

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from src.agents.base_agent import BaseAgent
from src.config import settings
from src.models.base import BaseAgentMessage

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """Главный оркестрационный агент - маршрутизирует запросы к специализированным агентам"""

    def __init__(self, agents: Sequence[BaseAgent]) -> None:
        super().__init__()
        self.agents = list(agents)
        self.llm = ChatOpenAI(
            model_name=settings.openai_model,
            openai_api_key=SecretStr(settings.openai_api_key),
            openai_api_base=str(settings.openai_base_url),
            max_tokens=100,
            request_timeout=settings.request_timeout_seconds,
        )

    def can_handle(self, intent: str) -> bool:
        return True  # Оркестратор может обрабатывать любые интенты

    async def process(self, message: BaseAgentMessage) -> BaseAgentMessage:
        intent = await self._detect_intent(message.message, message.context, message.session_id)

        best_agent = self._select_best_agent(intent)

        if best_agent:
            result = await best_agent.process(
                BaseAgentMessage(
                    user_id=message.user_id,
                    session_id=message.session_id,
                    intent=intent,
                    message=message.message,
                    context=message.context,
                )
            )
            return result
        else:
            return self._create_fallback_response(message)

    async def _detect_intent(
        self, message: str, context: dict[str, Any], session_id: str = "-"
    ) -> str:
        prompt = f"""
        Определи намерение пользователя из следующего сообщения.
        Доступные намерения:
        university_search, profile_analysis, timeline_management, exam_prep, general_help.

        Сообщение пользователя: "{message}"

        Верни только одно слово - намерение, без дополнительного текста.
        """

        try:
            response = await self._call_llm_with_retry(
                lambda: self.llm.ainvoke([HumanMessage(content=prompt)])
            )
            intent = str(response.content).strip().lower()

            valid_intents = [
                "university_search",
                "profile_analysis",
                "timeline_management",
                "exam_prep",
                "general_help",
            ]
            return intent if intent in valid_intents else "general_help"

        except Exception as e:
            logger.exception(
                "Intent detection failed [session=%s] %s",
                session_id,
                e,
                extra={"session_id": session_id, "intent": "general_help", "agent": self.name},
            )
            return "general_help"

    def _select_best_agent(self, intent: str) -> BaseAgent | None:
        """Выбирает наиболее подходящего агента для данного намерения"""
        suitable_agents = [agent for agent in self.agents if agent.can_handle(intent)]

        if suitable_agents:
            return suitable_agents[0]  # В MVP берем первого подходящего
        return None

    def _create_fallback_response(self, message: BaseAgentMessage) -> BaseAgentMessage:
        """Создает ответ, когда подходящий агент не найден"""
        fallback_message = """
        Я AI-ассистент для помощи в поступлении в университет.
        Я могу помочь вам с:
        - Поиском университетов и программ
        - Анализом вашего профиля
        - Планированием подготовки к экзаменам
        - Управлением сроками поступления

        Расскажите, что вас интересует?
        """

        message.agent_response = {
            "agent": self.name,
            "response": fallback_message,
            "next_steps": ["general_help"],
            "confidence": 0.8,
        }
        return message
