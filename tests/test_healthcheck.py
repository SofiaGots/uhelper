import pytest

from src.healthcheck import check_database, format_healthcheck, run_healthcheck
from src.version import VERSION


@pytest.mark.asyncio
async def test_healthcheck_returns_version() -> None:
    result = await run_healthcheck()
    assert result["version"] == VERSION


@pytest.mark.asyncio
async def test_healthcheck_has_status_field() -> None:
    result = await run_healthcheck()
    assert result["status"] in ("ok", "degraded")


@pytest.mark.asyncio
async def test_healthcheck_has_all_dependencies() -> None:
    result = await run_healthcheck()
    deps = result["dependencies"]
    for name in ("database", "telegram_api", "openai_api"):
        assert name in deps
        assert deps[name]["status"] in ("ok", "error", "skipped")


@pytest.mark.asyncio
async def test_healthcheck_database_returns_reasonably() -> None:
    result = await check_database()
    assert result["status"] in ("ok", "skipped", "error")


def test_format_healthcheck_contains_status_and_version() -> None:
    result = {
        "status": "ok",
        "version": "0.1.0",
        "dependencies": {
            "database": {"status": "ok", "latency_ms": 5.2},
            "telegram_api": {"status": "skipped", "reason": "no token"},
            "openai_api": {"status": "error", "error": "connection failed"},
        },
    }
    output = format_healthcheck(result)
    assert "Healthcheck: ok" in output
    assert "Version: 0.1.0" in output
    assert "[OK] database (5.2ms)" in output
    assert "[--] telegram_api" in output
    assert "[ERR] openai_api - connection failed" in output
