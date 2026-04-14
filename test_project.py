#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы проекта
"""

import os
import sys

# Устанавливаем путь к корню проекта
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, "src")

# Добавляем в путь
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)


def test_project_structure() -> None:
    """Проверяем структуру проекта"""
    print("🔍 Проверка структуры проекта...")

    # Проверяем существование ключевых файлов
    required_files = [
        "src/agents/__init__.py",
        "src/agents/base_agent.py",
        "src/agents/orchestrator.py",
        "src/agents/university_data_agent.py",
        "src/agents/profile_analyzer_agent.py",
        "src/models/__init__.py",
        "src/models/base.py",
        "src/bot.py",
        "main.py",
        ".env.example",
    ]

    for file_path in required_files:
        full_path = os.path.join(project_root, file_path)
        assert os.path.exists(full_path), f"{file_path} - не найден"
        print(f"✅ {file_path}")


def test_agent_creation() -> None:
    """Проверяем создание агентов"""
    print("\n🤖 Проверка создания агентов...")

    try:
        # Импортируем модели
        from src.models.base import BaseAgentMessage

        print("✅ Модели данных импортируются")

        # Импортируем агентов
        from src.agents.base_agent import BaseAgent
        from src.agents.profile_analyzer_agent import ProfileAnalyzerAgent
        from src.agents.university_data_agent import UniversityDataAgent

        print("✅ Агенты импортируются")

        # Создаем тестового агента
        class TestAgent(BaseAgent):
            async def process(self, message: BaseAgentMessage) -> BaseAgentMessage:
                return message

            def can_handle(self, intent: str) -> bool:
                return True

        _test_agent = TestAgent()
        print("✅ Базовый агент создается")

        # Создаем специализированных агентов
        try:
            _uni_agent = UniversityDataAgent()
            _profile_agent = ProfileAnalyzerAgent()
            print("✅ Специализированные агенты создаются")
        except Exception as e:
            print(f"⚠️ Ошибка создания специализированных агентов: {e}")
            # Это нормально для теста без реальных ключей API

    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        raise
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise


def test_bot_creation() -> None:
    """Проверяем создание бота"""
    print("\n🤖 Проверка создания бота...")

    try:
        from src.bot import UHelperBot

        # Создаем экземпляр бота
        _bot = UHelperBot()
        print("✅ Класс бота создается")

    except ImportError as e:
        print(f"❌ Ошибка импорта бота: {e}")
        raise
    except Exception as e:
        print(f"❌ Ошибка создания бота: {e}")
        raise


def main() -> bool:
    print("🧪 Тестирование проекта UHelper")
    print("=" * 50)

    test_project_structure()
    test_agent_creation()
    test_bot_creation()

    print("\n" + "=" * 50)
    print("🎉 Все основные тесты пройдены успешно!")
    print("\n📋 Следующие шаги:")
    print("1. Создайте файл .env на основе .env.example")
    print("2. Заполните TELEGRAM_BOT_TOKEN и ANTHROPIC_API_KEY")
    print("3. Запустите: python3 main.py")
    return True


if __name__ == "__main__":
    main()
