import anthropic
import os
from typing import List, Dict, Any
from src.agents.base_agent import BaseAgent
from src.models.base import BaseAgentMessage


class OrchestratorAgent(BaseAgent):
    """Главный оркестрационный агент - маршрутизирует запросы к специализированным агентам"""

    def __init__(self, agents: List[BaseAgent]):
        super().__init__()
        self.agents = agents
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def can_handle(self, intent: str) -> bool:
        return True  # Оркестратор может обрабатывать любые интенты

    async def process(self, message: BaseAgentMessage) -> BaseAgentMessage:
        """Определяет намерение и маршрутизирует к соответствующему агенту"""

        # Определяем намерение с помощью AI
        intent = await self._detect_intent(message.message, message.context)

        # Находим подходящего агента
        best_agent = self._select_best_agent(intent)

        if best_agent:
            # Перенаправляем сообщение агенту
            result = await best_agent.process(
                BaseAgentMessage(
                    user_id=message.user_id,
                    session_id=message.session_id,
                    intent=intent,
                    message=message.message,
                    context=message.context
                )
            )
            return result
        else:
            # Если подходящего агента нет, возвращаем общий ответ
            return self._create_fallback_response(message)

    async def _detect_intent(self, message: str, context: Dict[str, Any]) -> str:
        """Определяет намерение пользователя с помощью Claude AI"""

        prompt = f"""
        Определи намерение пользователя из следующего сообщения.
        Доступные намерения: university_search, profile_analysis, timeline_management, exam_prep, general_help.

        Сообщение пользователя: "{message}"

        Верни только одно слово - намерение, без дополнительного текста.
        """

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            intent = response.content[0].text.strip().lower()

            # Проверяем, что намерение корректное
            valid_intents = ["university_search", "profile_analysis", "timeline_management", "exam_prep", "general_help"]
            if intent in valid_intents:
                return intent
            else:
                return "general_help"

        except Exception as e:
            print(f"Ошибка определения намерения: {e}")
            return "general_help"

    def _select_best_agent(self, intent: str) -> BaseAgent:
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
            "confidence": 0.8
        }
        return message