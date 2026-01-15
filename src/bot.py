import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from src.agents.orchestrator import OrchestratorAgent
from src.agents.university_data_agent import UniversityDataAgent
from src.agents.profile_analyzer_agent import ProfileAnalyzerAgent
from src.models.base import BaseAgentMessage


class UHelperBot:
    """Основной класс Telegram-бота на базе aiogram"""

    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.bot = None
        self.dp = None
        self.orchestrator = None

        # Инициализируем сессии пользователей
        self.user_sessions = {}

    def initialize_agents(self):
        """Инициализирует всех агентов"""
        university_agent = UniversityDataAgent()
        profile_agent = ProfileAnalyzerAgent()

        agents = [university_agent, profile_agent]
        self.orchestrator = OrchestratorAgent(agents)

    async def start_command(self, message: Message):
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

    async def handle_message(self, message: Message):
        """Обрабатывает текстовые сообщения пользователя"""
        user = message.from_user
        message_text = message.text

        # Получаем или создаем сессию пользователя
        if user.id not in self.user_sessions:
            self.user_sessions[user.id] = {
                "session_id": str(user.id),
                "conversation_history": [],
                "user_profile": {}
            }

        session = self.user_sessions[user.id]

        # Создаем сообщение для агента
        agent_message = BaseAgentMessage(
            user_id=str(user.id),
            session_id=session["session_id"],
            intent="",  # Будет определено оркестратором
            message=message_text,
            context={
                "user_profile": session["user_profile"],
                "conversation_history": session["conversation_history"]
            }
        )

        # Обрабатываем сообщение через оркестратор
        try:
            result = await self.orchestrator.process(agent_message)

            # Обновляем контекст
            session["conversation_history"].append({
                "user": message_text,
                "agent": result.agent_response["agent"],
                "response": result.agent_response["response"]
            })

            # Отправляем ответ пользователю
            await message.answer(result.agent_response["response"])

        except Exception as e:
            error_message = "Извините, произошла ошибка. Попробуйте позже."
            await message.answer(error_message)
            print(f"Ошибка обработки сообщения: {e}")

    async def help_command(self, message: Message):
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

    async def profile_command(self, message: Message):
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
        "У меня 5 по математике, 4 по физике, интересуюсь программированием, хочу поступить в Москве"
        """
        await message.answer(profile_instructions)

    async def universities_command(self, message: Message):
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

    async def setup_handlers(self):
        """Настраивает обработчики команд"""
        self.dp.message.register(self.start_command, Command("start"))
        self.dp.message.register(self.help_command, Command("help"))
        self.dp.message.register(self.profile_command, Command("profile"))
        self.dp.message.register(self.universities_command, Command("universities"))
        self.dp.message.register(self.handle_message)

    async def run(self):
        """Запускает бота"""
        if not self.token:
            print("❌ Ошибка: TELEGRAM_BOT_TOKEN не установлен")
            return

        # Инициализируем бота и диспетчер
        self.bot = Bot(token=self.token)
        self.dp = Dispatcher()

        # Инициализируем агентов
        self.initialize_agents()

        # Настраиваем обработчики
        await self.setup_handlers()

        # Запускаем бота
        print("🚀 Бот запущен...")
        await self.dp.start_polling(self.bot)


if __name__ == "__main__":
    bot = UHelperBot()
    asyncio.run(bot.run())