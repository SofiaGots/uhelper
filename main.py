#!/usr/bin/env python3
"""
UHelper - AI-ассистент для поступления в университет
Главный файл запуска приложения
"""

import asyncio

from dotenv import load_dotenv

from src.bot import UHelperBot
from src.config import get_settings
from src.healthcheck import format_healthcheck, run_healthcheck
from src.utils.logging_config import setup_logging


def main() -> None:
    """Основная функция запуска приложения"""

    load_dotenv()

    try:
        get_settings()
    except RuntimeError as exc:
        print(f"❌ Ошибка конфигурации: {exc}")
        print("\nПроверьте файл .env (создайте из .env.example) и повторите запуск.")
        return

    setup_logging()

    hc = asyncio.run(run_healthcheck())
    print(format_healthcheck(hc))

    print("🚀 Запуск UHelper - AI-ассистента для поступления")
    print("📚 Подготовка к запуску бота...")

    try:
        bot = UHelperBot()
        asyncio.run(bot.run())
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        print("\n🔧 Проверьте:")
        print("• Корректность токена Telegram бота")
        print("• Доступность OpenAI-compatible API")
        print("• Интернет-соединение")


if __name__ == "__main__":
    main()
