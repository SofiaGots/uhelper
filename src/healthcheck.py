import asyncio
import time
from typing import Any

from src.config import settings
from src.version import VERSION


async def check_database() -> dict[str, Any]:
    start = time.monotonic()
    url = settings.database_url
    try:
        import sqlalchemy as sa
        from sqlalchemy import text

        engine = sa.create_engine(url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        latency = (time.monotonic() - start) * 1000
        return {"status": "ok", "latency_ms": round(latency, 1)}
    except ImportError:
        return {"status": "skipped", "reason": "sqlalchemy not installed"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def check_telegram_api() -> dict[str, Any]:
    if not settings.telegram_bot_token or len(settings.telegram_bot_token) < 10:
        return {"status": "skipped", "reason": "no token configured"}

    start = time.monotonic()
    try:
        import aiohttp

        url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/getMe"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as resp:
                data = await resp.json()
        latency = (time.monotonic() - start) * 1000
        if data.get("ok"):
            return {"status": "ok", "latency_ms": round(latency, 1)}
        return {"status": "error", "error": data.get("description", "unknown")}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def check_openai_api() -> dict[str, Any]:
    if not settings.openai_api_key or len(settings.openai_api_key) < 10:
        return {"status": "skipped", "reason": "no api key configured"}

    start = time.monotonic()
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=str(settings.openai_base_url),
        )
        await client.models.list()
        latency = (time.monotonic() - start) * 1000
        return {"status": "ok", "latency_ms": round(latency, 1)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def run_healthcheck() -> dict[str, Any]:
    db_result = await check_database()
    tg_result = await check_telegram_api()
    ai_result = await check_openai_api()

    all_ok = all(
        r["status"] == "ok" or r["status"] == "skipped" for r in (db_result, tg_result, ai_result)
    )

    return {
        "status": "ok" if all_ok else "degraded",
        "version": VERSION,
        "dependencies": {
            "database": db_result,
            "telegram_api": tg_result,
            "openai_api": ai_result,
        },
    }


def format_healthcheck(result: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"Healthcheck: {result['status']}")
    lines.append(f"Version: {result['version']}")
    lines.append("")
    for name, dep in result["dependencies"].items():
        status = dep["status"]
        icon = {"ok": "OK", "error": "ERR", "skipped": "--"}.get(status, "??")
        latency = dep.get("latency_ms")
        latency_str = f" ({latency}ms)" if latency else ""
        error_str = f" - {dep.get('error', '')}" if status == "error" else ""
        lines.append(f"  [{icon}] {name}{latency_str}{error_str}")
    return "\n".join(lines)


async def main() -> None:
    result = await run_healthcheck()
    print(format_healthcheck(result))
    if result["status"] != "ok":
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
