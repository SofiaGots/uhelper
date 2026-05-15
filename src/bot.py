import asyncio
import logging
import socket
from typing import Any, TypedDict

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import Command
from aiogram.types import Message
from pydantic import ValidationError

from src.agents.base_agent import BaseAgent
from src.agents.exceptions import SAFE_USER_MESSAGE, log_agent_error
from src.agents.orchestrator import OrchestratorAgent
from src.agents.profile_analyzer_agent import ProfileAnalyzerAgent
from src.agents.university_data_agent import UniversityDataAgent
from src.config import settings
from src.models.base import BaseAgentMessage
from src.utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class SessionState(TypedDict):
    """Состояние сессии пользователя."""

    session_id: str
    conversation_history: list[dict[str, str]]
    user_profile: dict[str, Any]


class UHelperBot:
    """Основной класс Telegram-бота на базе aiogram"""

    def __init__(self) -> None:
        self.token = settings.telegram_bot_token
        self.bot: Bot | None = None
        self.dp: Dispatcher | None = None
        self.orchestrator: OrchestratorAgent | None = None
        self.rate_limiter = RateLimiter(
            limit=settings.rate_limit_messages,
            window_seconds=settings.rate_limit_window_seconds,
        )

        # Инициализируем сессии пользователей
        self.user_sessions: dict[int, SessionState] = {}

    def initialize_agents(self) -> None:
        """Инициализирует всех агентов"""
        university_agent = UniversityDataAgent()
        profile_agent = ProfileAnalyzerAgent()

        agents: list[BaseAgent] = [university_agent, profile_agent]
        self.orchestrator = OrchestratorAgent(agents)

    async def start_command(self, message: Message) -> None:
        """Обрабатывает команду /start"""
        welcome_message = """
        👋 Привет! Я AI-ассистент для помощи в поступлении в университет.

        🤔 Что я умею:
        • Помогать с поиском университетов и программ
        • Анализировать ваш профиль и давать рекомендации
        • Помогать с планированием подготовки

        💬 Просто напишите мне, что вас интересует!

        Например:
        • "Какие университеты в Москве с IT-направлением?"
        • "Проанализируй мой профиль"
        • "Что нужно для поступления на экономику?"
        """

        await message.answer(welcome_message)

    async def handle_message(self, message: Message) -> None:
        """Обрабатывает текстовые сообщения пользователя"""
        user = message.from_user
        if user is None:
            return

        message_text = message.text or ""
        rate_limit = await self.rate_limiter.check(str(user.id))
        if not rate_limit.allowed:
            await message.answer(
                "Слишком много сообщений подряд. "
                f"Попробуйте снова через {rate_limit.retry_after_seconds} сек."
            )
            return

        # Получаем или создаем сессию пользователя
        if user.id not in self.user_sessions:
            self.user_sessions[user.id] = {
                "session_id": str(user.id),
                "conversation_history": [],
                "user_profile": {},
            }

        session = self.user_sessions[user.id]

        # Обрабатываем сообщение через оркестратор
        try:
            # Создаем сообщение для агента
            agent_message = BaseAgentMessage(
                user_id=str(user.id),
                session_id=session["session_id"],
                intent="",  # Будет определено оркестратором
                message=message_text,
                context={
                    "user_profile": session["user_profile"],
                    "conversation_history": session["conversation_history"],
                },
            )

            if self.orchestrator is None:
                raise RuntimeError("Orchestrator is not initialized")

            result = await self.orchestrator.process(agent_message)

            # Обновляем контекст
            if result.agent_response:
                agent_response = result.agent_response
                session["conversation_history"].append(
                    {
                        "user": message_text,
                        "intent": result.intent,
                        "agent": str(agent_response.get("agent", "-")),
                        "response": str(agent_response.get("response", "-")),
                    }
                )

                # Отправляем ответ пользователю
                await message.answer(str(agent_response.get("response", "")))

        except ValidationError:
            await message.answer(
                "Сообщение должно быть непустым, до 2000 символов, на русском или английском."
            )
        except Exception as e:
            session_id = session.get("session_id", "-")
            log_agent_error(e, {"session_id": session_id, "intent": message_text, "agent": "bot"})
            await message.answer(SAFE_USER_MESSAGE)

    async def help_command(self, message: Message) -> None:
        """Обрабатывает команду /help"""
        help_text = """
        📚 **Команды бота:**

        /start - Начать работу с ботом
        /help - Показать эту справку
        /profile - Начать анализ вашего профиля
        /universities - Поиск университетов

        💡 **Что можно спросить:**
        • "Какие университеты в [город] с [специальность]?"
        • "Проанализируй мой профиль: у меня 5 по математике, 4 по физике"
        • "Требования для поступления на [специальность]"
        • "Какие экзамены нужны для [университет]?"
        """
        await message.answer(help_text)

    async def profile_command(self, message: Message) -> None:
        """Обрабатывает команду /profile"""
        profile_instructions = """
        📊 **Анализ профиля**

        Чтобы я мог проанализировать ваш профиль, расскажите о себе:

        📚 **Академическая информация:**
        - Ваши оценки по школьным предметам
        - Результаты пробных ЕГЭ
        - Участие в олимпиадах

        🎯 **Интересы и предпочтения:**
        - Какие предметы вам нравятся
        - Карьерные цели
        - Предпочтительные города/университеты

        💬 **Пример:**
        "У меня 5 по математике, 4 по физике, интересуюсь программированием,
        хочу поступить в Москве"
        """
        await message.answer(profile_instructions)

    async def universities_command(self, message: Message) -> None:
        """Обрабатывает команду /universities"""
        universities_help = """
        🏛️ **Поиск университетов**

        Вы можете искать университеты по:
        • Городу (например, "университеты в Москве")
        • Специальности (например, "IT университеты")
        • Университету (например, "МГУ программы")

        💡 **Примеры запросов:**
        • "Какие есть технические университеты в Санкт-Петербурге?"
        • "Программы экономики в Москве"
        • "МГУ требования поступления"
        """
        await message.answer(universities_help)

    async def health_command(self, message: Message) -> None:
        from src.healthcheck import format_healthcheck, run_healthcheck

        result = await run_healthcheck()
        await message.answer(f"<code>{format_healthcheck(result)}</code>", parse_mode="HTML")

    async def setup_handlers(self) -> None:
        """Настраивает обработчики команд"""
        if self.dp is None:
            raise RuntimeError("Dispatcher is not initialized")

        self.dp.message.register(self.start_command, Command("start"))
        self.dp.message.register(self.help_command, Command("help"))
        self.dp.message.register(self.profile_command, Command("profile"))
        self.dp.message.register(self.universities_command, Command("universities"))
        self.dp.message.register(self.health_command, Command("health"))
        self.dp.message.register(self.handle_message)

    async def run(self) -> None:
        """Запускает бота"""
        if not self.token:
            print("❌ Ошибка: TELEGRAM_BOT_TOKEN не установлен")
            return

        # Инициализируем бота с кастомным DNS resolver и HTTP proxy
        resolver = aiohttp.AsyncResolver(nameservers=["1.1.1.1", "8.8.8.8"])
        proxy_url = "http://sofa:1234567890@vpn.gots.ru:8888"
        session = HttpProxyAiohttpSession(http_proxy=proxy_url)
        session._connector_init["resolver"] = resolver
        session._connector_init["family"] = socket.AF_INET
        self.bot = Bot(token=self.token, session=session)
        self.dp = Dispatcher()

        # Инициализируем агентов
        self.initialize_agents()

        # Настраиваем обработчики
        await self.setup_handlers()

        # Запускаем бота
        print("🚀 Бот запущен...")
        await self.dp.start_polling(self.bot)


class HttpProxyAiohttpSession(AiohttpSession):
    def __init__(self, http_proxy: str, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._http_proxy = http_proxy

    async def create_session(self) -> aiohttp.ClientSession:
        if self._should_reset_connector:
            await self.close()

        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                connector=self._connector_type(**self._connector_init),
                headers={
                    "User-Agent": f"Python aiohttp/{aiohttp.__version__} "
                    f"aiogram/{__import__('aiogram').__version__}",
                },
                proxy=self._http_proxy,
            )
            self._should_reset_connector = False

        return self._session


if __name__ == "__main__":
    bot = UHelperBot()
    asyncio.run(bot.run())
