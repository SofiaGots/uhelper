import asyncio
import random
import time
from collections.abc import Callable, Coroutine
from typing import Any


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: float = 30.0,
        half_open_max_retries: int = 1,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._reset_timeout = reset_timeout
        self._half_open_max_retries = half_open_max_retries

        self._state: str = "closed"
        self._failure_count = 0
        self._last_failure_time: float | None = None
        self._half_open_attempts = 0

    @property
    def state(self) -> str:
        if self._state == "open" and self._last_failure_time is not None:
            if time.monotonic() - self._last_failure_time >= self._reset_timeout:
                self._state = "half-open"
                self._half_open_attempts = 0
        return self._state

    def is_available(self) -> bool:
        return self.state != "open"

    def record_success(self) -> None:
        self._state = "closed"
        self._failure_count = 0
        self._last_failure_time = None
        self._half_open_attempts = 0

    def record_failure(self) -> bool:
        self._failure_count += 1
        self._last_failure_time = time.monotonic()

        if self.state == "half-open":
            self._half_open_attempts += 1
            if self._half_open_attempts >= self._half_open_max_retries:
                self._state = "open"
            return self._half_open_attempts < self._half_open_max_retries

        if self._failure_count >= self._failure_threshold:
            self._state = "open"
            return False

        return True

    def reset(self) -> None:
        self._state = "closed"
        self._failure_count = 0
        self._last_failure_time = None
        self._half_open_attempts = 0


async def call_with_retry(
    coro_factory: Callable[[], Coroutine[Any, Any, Any]],
    retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    call_timeout: float | None = None,
    circuit_breaker: CircuitBreaker | None = None,
) -> Any:  # noqa: ANN401
    if circuit_breaker and not circuit_breaker.is_available():
        raise RuntimeError("Circuit breaker is open")

    last_exc: Exception | None = None

    for attempt in range(retries):
        try:
            if call_timeout is not None:
                result = await asyncio.wait_for(coro_factory(), timeout=call_timeout)
            else:
                result = await coro_factory()

            if circuit_breaker:
                circuit_breaker.record_success()

            return result

        except Exception as e:
            last_exc = e

            if circuit_breaker:
                cb_allowed = circuit_breaker.record_failure()
                if not cb_allowed:
                    raise RuntimeError("Circuit breaker is open") from e

            if attempt < retries - 1:
                delay = min(base_delay * (2**attempt) + random.uniform(0, 0.5), max_delay)
                await asyncio.sleep(delay)

    raise last_exc  # type: ignore[misc]
