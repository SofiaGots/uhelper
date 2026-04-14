#!/usr/bin/env python3
"""
UHelper - AI-ассистент для поступления в университет
Главный файл запуска приложения
"""

from dotenv import load_dotenv

from src.bot import UHelperBot
from src.config import get_settings
from src.utils.logging_config import setup_logging


def main() -> None:
    """Основная функция запуска приложения"""

    # Загружаем переменные окружения
    load_dotenv()

    # Валидация конфигурации через Pydantic Settings
    try:
        get_settings()
    except RuntimeError as exc:
        print(f"❌ Ошибка конфигурации: {exc}")
        print("\nПроверьте файл .env (создайте из .env.example) и повторите запуск.")
        return

    setup_logging()

    print("🚀 Запуск UHelper - AI-ассистента для поступления")
    print("📚 Подготовка к запуску бота...")

    try:
        # Создаем и запускаем бота
        bot = UHelperBot()
        import asyncio

        asyncio.run(bot.run())
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        print("\n🔧 Проверьте:")
        print("• Корректность токена Telegram бота")
        print("• Доступность OpenAI-compatible API")
        print("• Интернет-соединение")


if __name__ == "__main__":
    main()
