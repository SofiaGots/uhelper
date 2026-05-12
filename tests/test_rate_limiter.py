import pytest

from src.utils.rate_limiter import InMemoryRateLimitStore, RateLimiter


class FakeClock:
    """Контролируемое время для тестов rate limiter."""

    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.mark.asyncio
async def test_rate_limiter_allows_requests_under_limit() -> None:
    clock = FakeClock()
    limiter = RateLimiter(limit=2, window_seconds=60, clock=clock)

    first = await limiter.check("user:1")
    second = await limiter.check("user:1")

    assert first.allowed is True
    assert second.allowed is True


@pytest.mark.asyncio
async def test_rate_limiter_blocks_requests_over_limit() -> None:
    clock = FakeClock()
    limiter = RateLimiter(limit=2, window_seconds=60, clock=clock)

    await limiter.check("user:1")
    await limiter.check("user:1")
    blocked = await limiter.check("user:1")

    assert blocked.allowed is False
    assert blocked.retry_after_seconds == 60


@pytest.mark.asyncio
async def test_rate_limiter_allows_after_window_expires() -> None:
    clock = FakeClock()
    limiter = RateLimiter(limit=1, window_seconds=60, clock=clock)

    await limiter.check("user:1")
    blocked = await limiter.check("user:1")
    clock.advance(61)
    allowed = await limiter.check("user:1")

    assert blocked.allowed is False
    assert allowed.allowed is True


@pytest.mark.asyncio
async def test_in_memory_store_keeps_keys_independent() -> None:
    clock = FakeClock()
    store = InMemoryRateLimitStore()
    limiter = RateLimiter(limit=1, window_seconds=60, store=store, clock=clock)

    first_user = await limiter.check("user:1")
    second_user = await limiter.check("user:2")

    assert first_user.allowed is True
    assert second_user.allowed is True
