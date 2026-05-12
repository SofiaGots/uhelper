"""Rate limiting для пользовательских запросов."""

from collections.abc import Callable
from dataclasses import dataclass
from math import ceil
from time import monotonic
from typing import Protocol


@dataclass(frozen=True)
class RateLimitResult:
    """Результат проверки лимита."""

    allowed: bool
    retry_after_seconds: int = 0


class RateLimitStore(Protocol):
    """Интерфейс хранилища лимитов, совместимый с будущей Redis-реализацией."""

    async def get_events(self, key: str) -> list[float]:
        """Возвращает временные метки запросов.

        Args:
            key: Ключ пользователя или сессии.

        Returns:
            Список временных меток.
        """

    async def set_events(self, key: str, events: list[float]) -> None:
        """Сохраняет временные метки запросов.

        Args:
            key: Ключ пользователя или сессии.
            events: Список временных меток.
        """


class InMemoryRateLimitStore:
    """In-memory хранилище лимитов для MVP."""

    def __init__(self) -> None:
        self._events: dict[str, list[float]] = {}

    async def get_events(self, key: str) -> list[float]:
        """Возвращает копию временных меток для ключа.

        Args:
            key: Ключ пользователя или сессии.

        Returns:
            Список временных меток.
        """

        return list(self._events.get(key, []))

    async def set_events(self, key: str, events: list[float]) -> None:
        """Сохраняет временные метки для ключа.

        Args:
            key: Ключ пользователя или сессии.
            events: Список временных меток.
        """

        self._events[key] = events


class RateLimiter:
    """Ограничивает количество запросов в скользящем временном окне."""

    def __init__(
        self,
        limit: int,
        window_seconds: int,
        store: RateLimitStore | None = None,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self.store = store or InMemoryRateLimitStore()
        self.clock = clock

    async def check(self, key: str) -> RateLimitResult:
        """Проверяет, может ли ключ выполнить новый запрос.

        Args:
            key: Ключ пользователя или сессии.

        Returns:
            Результат проверки лимита.
        """

        now = self.clock()
        cutoff = now - self.window_seconds
        events = [
            event_time for event_time in await self.store.get_events(key) if event_time > cutoff
        ]

        if len(events) >= self.limit:
            retry_after = ceil(self.window_seconds - (now - events[0]))
            await self.store.set_events(key, events)
            return RateLimitResult(allowed=False, retry_after_seconds=max(retry_after, 1))

        events.append(now)
        await self.store.set_events(key, events)
        return RateLimitResult(allowed=True)
