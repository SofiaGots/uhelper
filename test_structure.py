#!/usr/bin/env python3
"""
Тестовый скрипт для проверки структуры проекта
"""

import os
import sys

# Добавляем src в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Проверяем, что все модули импортируются корректно"""
    try:
        from models.base import BaseAgentMessage, UserProfile
        print("✅ Модели данных импортируются корректно")

        from agents.base_agent import BaseAgent
        from agents.orchestrator import OrchestratorAgent
        from agents.university_data_agent import UniversityDataAgent
        from agents.profile_analyzer_agent import ProfileAnalyzerAgent
        print("✅ Агенты импортируются корректно")

        print("✅ Все импорты работают правильно!")
        return True

    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_agents_initialization():
    """Проверяем инициализацию агентов"""
    try:
        # Тестируем базовый агент
        from agents.base_agent import BaseAgent

        class TestAgent(BaseAgent):
            def process(self, message):
                return message
            def can_handle(self, intent):
                return True

        agent = TestAgent()
        print("✅ Базовый агент инициализируется корректно")

        return True

    except Exception as e:
        print(f"❌ Ошибка инициализации агентов: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Тестирование структуры проекта UHelper")
    print("-" * 40)

    success = True
    success &= test_imports()
    success &= test_agents_initialization()

    print("-" * 40)
    if success:
        print("🎉 Все тесты пройдены успешно!")
    else:
        print("❌ Есть проблемы с структурой проекта")