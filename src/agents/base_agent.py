from abc import ABC, abstractmethod
from typing import Dict, Any
from ..models.base import BaseAgentMessage


class BaseAgent(ABC):
    """Базовый класс для всех агентов"""

    def __init__(self):
        self.name = self.__class__.__name__

    @abstractmethod
    async def process(self, message: BaseAgentMessage) -> BaseAgentMessage:
        """Основной метод обработки сообщений"""
        pass

    @abstractmethod
    def can_handle(self, intent: str) -> bool:
        """Проверяет, может ли агент обработать данный интент"""
        pass

    def get_confidence(self, message: BaseAgentMessage) -> float:
        """Возвращает уверенность агента в обработке сообщения (0-1)"""
        return 0.5 if self.can_handle(message.intent) else 0.0