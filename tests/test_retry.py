import asyncio

import pytest

from src.utils.retry import CircuitBreaker, call_with_retry


@pytest.mark.asyncio
async def test_circuit_breaker_starts_closed() -> None:
    cb = CircuitBreaker(failure_threshold=3, reset_timeout=60.0)
    assert cb.state == "closed"
    assert cb.is_available()


@pytest.mark.asyncio
async def test_circuit_breaker_opens_after_threshold() -> None:
    cb = CircuitBreaker(failure_threshold=3, reset_timeout=60.0)
    for _ in range(3):
        cb.record_failure()
    assert cb.state == "open"
    assert not cb.is_available()


@pytest.mark.asyncio
async def test_circuit_breaker_resets_on_success() -> None:
    cb = CircuitBreaker(failure_threshold=3, reset_timeout=60.0)
    for _ in range(2):
        cb.record_failure()
    cb.record_success()
    assert cb.state == "closed"
    assert cb._failure_count == 0
    assert cb.is_available()


@pytest.mark.asyncio
async def test_circuit_breaker_half_open_transition() -> None:
    cb = CircuitBreaker(failure_threshold=3, reset_timeout=0.05)

    for _ in range(3):
        cb.record_failure()
    assert cb.state == "open"

    await asyncio.sleep(0.06)
    assert cb.state == "half-open"
    assert cb.is_available()


@pytest.mark.asyncio
async def test_retry_succeeds_on_third_attempt() -> None:
    call_count = 0

    async def flaky() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("fail")
        return "success"

    result = await call_with_retry(flaky, retries=3, base_delay=0.01, max_delay=0.05)
    assert result == "success"
    assert call_count == 3


@pytest.mark.asyncio
async def test_retry_fails_after_exhaustion() -> None:
    call_count = 0

    async def always_fails() -> str:
        nonlocal call_count
        call_count += 1
        raise ValueError("always fail")

    with pytest.raises(ValueError, match="always fail"):
        await call_with_retry(always_fails, retries=3, base_delay=0.01, max_delay=0.05)
    assert call_count == 3


@pytest.mark.asyncio
async def test_retry_respects_timeout() -> None:
    async def slow() -> str:
        await asyncio.sleep(1.0)
        return "done"

    with pytest.raises(TimeoutError):
        await call_with_retry(slow, retries=1, call_timeout=0.05, base_delay=0.01)


@pytest.mark.asyncio
async def test_circuit_breaker_blocks_when_open() -> None:
    cb = CircuitBreaker(failure_threshold=1, reset_timeout=60.0)
    cb.record_failure()

    async def ok() -> str:
        return "ok"

    with pytest.raises(RuntimeError, match="Circuit breaker is open"):
        await call_with_retry(ok, retries=1, circuit_breaker=cb, base_delay=0.01)


@pytest.mark.asyncio
async def test_circuit_breaker_recovers_after_half_open() -> None:
    cb = CircuitBreaker(failure_threshold=1, reset_timeout=0.05)
    cb.record_failure()
    assert cb.state == "open"

    await asyncio.sleep(0.06)
    assert cb.state == "half-open"

    async def works_now() -> str:
        return "recovered"

    result = await call_with_retry(works_now, retries=1, circuit_breaker=cb, base_delay=0.01)
    assert result == "recovered"
    assert cb.state == "closed"
