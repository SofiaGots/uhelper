#!/usr/bin/env python3
"""
UHelper - AI-ассистент для поступления в университет
Главный файл запуска приложения
"""

import os
from dotenv import load_dotenv
from src.bot import UHelperBot


def main():
    """Основная функция запуска приложения"""

    # Загружаем переменные окружения
    load_dotenv()

    # Проверяем необходимые переменные
    required_env_vars = ["TELEGRAM_BOT_TOKEN", "ANTHROPIC_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Ошибка: Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        print("\nПожалуйста, создайте файл .env на основе .env.example и заполните значения:")
        print("TELEGRAM_BOT_TOKEN=ваш_токен_бота")
        print("ANTHROPIC_API_KEY=ваш_ключ_anthropic")
        return

    print("🚀 Запуск UHelper - AI-ассистента для поступления")
    print("📚 Подготовка к запуску бота...")

    try:
        # Создаем и запускаем бота
        bot = UHelperBot()
        bot.run()
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        print("\n🔧 Проверьте:")
        print("• Корректность токена Telegram бота")
        print("• Доступность Anthropic API")
        print("• Интернет-соединение")


if __name__ == "__main__":
    main()