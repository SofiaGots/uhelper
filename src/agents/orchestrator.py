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

_INTENT_KEYWORDS: dict[str, list[str]] = {
    "university_search": [
        "университет",
        "универ",
        "вуз",
        "вузы",
        "поступление",
        "факультет",
        "кафедр",
        "магистратура",
        "бакалавриат",
        "москв",
        "спб",
        "питер",
        "петербург",
        "санкт",
        "екатеринбург",
        "новосибирск",
        "томск",
        "казань",
        "обучение",
        "бюджет",
        "платн",
        "стоимость",
        "диплом",
        "поступить",
        "проходной",
        "балл",
    ],
    "program_search": [
        "направление",
        "специальность",
        "программ",
        "предмет",
        "экономи",
        "юриспруденц",
        "международн",
        "менеджмент",
        "маркетинг",
        "журналистик",
        "психологи",
        "биологи",
        "хими",
        "информат",
        "программирован",
        "it",
        "робототехник",
        "авиастроен",
        "машиностроен",
        "финанс",
        "бухуч",
        "истори",
        "литератур",
        "иностранн",
        "математ",
        "физик",
        "егэ",
    ],
    "profile_analysis": [
        "профиль",
        "мои шансы",
        "gpa",
        "оценк",
        "резюме",
        "сильн",
        "слаб",
        "рекомендац",
        "успеваемость",
    ],
    "timeline_management": [
        "срок",
        "дедлайн",
        "deadline",
        "календарь",
        "когда",
        "график",
        "расписание",
        "напомни",
        "план",
        "этап",
    ],
    "exam_prep": [
        "экзамен",
        "подготовк",
        "тест",
        "sat",
        "ielts",
        "toefl",
        "тренировк",
        "задание",
        "пробн",
    ],
}

_AGENT_TO_INTENT: dict[str, str] = {
    "UniversityDataAgent": "university_search",
    "ProfileAnalyzerAgent": "profile_analysis",
}


def _detect_intent_keyword(message: str, context: dict[str, Any] | None = None) -> str:
    msg_lower = message.lower()
    scores: dict[str, int] = {}
    for intent, keywords in _INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in msg_lower)
        if score > 0:
            scores[intent] = score
    if scores:
        return max(scores, key=scores.get)  # type: ignore[type-var]
    if context:
        history = context.get("conversation_history", [])
        if history:
            last = history[-1]
            last_intent = last.get("intent") or _AGENT_TO_INTENT.get(last.get("agent", ""))
            if last_intent:
                return last_intent
    return "general_help"


class OrchestratorAgent(BaseAgent):
    def __init__(self, agents: Sequence[BaseAgent]) -> None:
        super().__init__()
        self.agents = list(agents)
        self._enable_llm = False
        try:
            self.llm = ChatOpenAI(
                model_name=settings.openai_model,
                openai_api_key=SecretStr(settings.openai_api_key),
                openai_api_base=str(settings.openai_base_url),
                max_tokens=50,
                request_timeout=settings.request_timeout_seconds,
            )
            self._enable_llm = True
        except Exception:
            logger.warning(
                "LLM not available, using keyword-only intent detection",
                extra={"agent": self.name},
            )

    def can_handle(self, intent: str) -> bool:
        return True

    async def process(self, message: BaseAgentMessage) -> BaseAgentMessage:
        intent = await self._detect_intent(message.message, message.context, message.session_id)
        best_agent = self._select_best_agent(intent)

        if best_agent:
            return await best_agent.process(
                BaseAgentMessage(
                    user_id=message.user_id,
                    session_id=message.session_id,
                    intent=intent,
                    message=message.message,
                    context=message.context,
                )
            )
        return self._create_fallback_response(message)

    async def _detect_intent(
        self, message: str, context: dict[str, Any], session_id: str = "-"
    ) -> str:
        keyword_intent = _detect_intent_keyword(message, context)
        if not self._enable_llm:
            return keyword_intent

        prompt = (
            f"Определи намерение пользователя. Варианты: university_search, "
            f"program_search, profile_analysis, timeline_management, exam_prep, "
            f"general_help.\n"
            f'Сообщение: "{message}"\n'
            f"Ответь одним словом."
        )
        try:
            response = await self._call_llm_with_retry(
                lambda: self.llm.ainvoke([HumanMessage(content=prompt)]),
                call_timeout=10.0,
            )
            intent = str(response.content).strip().lower()
            valid = (
                "university_search",
                "program_search",
                "profile_analysis",
                "timeline_management",
                "exam_prep",
                "general_help",
            )  # noqa: E501
            if intent in valid:
                return intent
        except Exception:
            logger.info(
                "LLM intent detection failed, using keyword fallback [session=%s]",
                session_id,
                extra={"session_id": session_id, "intent": keyword_intent, "agent": self.name},
            )
        return keyword_intent

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
