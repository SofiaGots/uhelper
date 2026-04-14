#!/usr/bin/env python3
"""
Тестовый скрипт для проверки структуры проекта
"""

import os
import sys

# Добавляем src в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_imports() -> None:
    """Проверяем, что все модули импортируются корректно"""
    try:
        from src.models.base import BaseAgentMessage, UserProfile

        assert BaseAgentMessage and UserProfile
        print("✅ Модели данных импортируются корректно")

        from src.agents.base_agent import BaseAgent
        from src.agents.orchestrator import OrchestratorAgent
        from src.agents.profile_analyzer_agent import ProfileAnalyzerAgent
        from src.agents.university_data_agent import UniversityDataAgent

        assert BaseAgent and OrchestratorAgent and ProfileAnalyzerAgent and UniversityDataAgent
        print("✅ Агенты импортируются корректно")

        print("✅ Все импорты работают правильно!")
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        raise


def test_agents_initialization() -> None:
    """Проверяем инициализацию агентов"""
    try:
        # Тестируем базовый агент
        from src.agents.base_agent import BaseAgent
        from src.models.base import BaseAgentMessage

        class TestAgent(BaseAgent):
            async def process(self, message: BaseAgentMessage) -> BaseAgentMessage:
                return message

            def can_handle(self, intent: str) -> bool:
                return True

        _agent = TestAgent()
        print("✅ Базовый агент инициализируется корректно")

    except Exception as e:
        print(f"❌ Ошибка инициализации агентов: {e}")
        raise


if __name__ == "__main__":
    print("🧪 Тестирование структуры проекта UHelper")
    print("-" * 40)

    test_imports()
    test_agents_initialization()

    print("-" * 40)
    print("🎉 Все тесты пройдены успешно!")
