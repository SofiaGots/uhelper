import logging
from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from typing import Any

from ..config import settings
from ..models.base import BaseAgentMessage
from ..utils.retry import CircuitBreaker, call_with_retry
from .exceptions import log_agent_error

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    _circuit_breaker = CircuitBreaker(
        failure_threshold=settings.circuit_breaker_failure_threshold,
        reset_timeout=settings.circuit_breaker_reset_timeout,
    )

    def __init__(self) -> None:
        self.name = self.__class__.__name__

    @abstractmethod
    async def process(self, message: BaseAgentMessage) -> BaseAgentMessage:
        raise NotImplementedError

    @abstractmethod
    def can_handle(self, intent: str) -> bool:
        raise NotImplementedError

    def get_confidence(self, message: BaseAgentMessage) -> float:
        return 0.5 if self.can_handle(message.intent) else 0.0

    async def _call_llm_with_retry(
        self,
        llm_call: Callable[[], Coroutine[Any, Any, Any]],
        call_timeout: float | None = None,
    ) -> Any:
        return await call_with_retry(
            llm_call,
            retries=settings.retry_max_attempts,
            base_delay=settings.retry_base_delay,
            max_delay=settings.retry_max_delay,
            call_timeout=call_timeout or settings.request_timeout_seconds,
            circuit_breaker=self._circuit_breaker,
        )

    def _safe_handle_error(
        self,
        exc: Exception,
        session_id: str = "-",
        intent: str = "-",
    ) -> str:
        ctx = {"session_id": session_id, "intent": intent, "agent": self.name}
        return log_agent_error(exc, ctx)
