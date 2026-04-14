import asyncio
from collections.abc import Callable, Generator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest


@dataclass
class FakeLLMResponse:
    content: str


class FakeLLM:
    """Простой фейковый LLM для тестов."""

    def __init__(self, responder: Callable[[str], str]) -> None:
        self._responder = responder

    async def ainvoke(self, messages: list[Any]) -> FakeLLMResponse:
        # Берём текст последнего сообщения
        last = messages[-1].content if messages else ""
        return FakeLLMResponse(self._responder(str(last)))


@pytest.fixture
def fake_intent_llm() -> FakeLLM:
    return FakeLLM(lambda _: "university_search")


@pytest.fixture
def fake_profile_llm() -> FakeLLM:
    return FakeLLM(lambda prompt: f"analyzed:{prompt[:20]}")


@pytest.fixture
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    try:
        yield loop
    finally:
        loop.close()


# --- Общие тестовые фикстуры ---


@dataclass
class FakeAIClient:
    """Фейковый AI-клиент с одним методом generate."""

    response: str = "ok"

    async def generate(self, prompt: str) -> str:  # noqa: ARG002
        return self.response


@dataclass
class FakeUser:
    id: int


@dataclass
class FakeMessage:
    """Минимальный аналог aiogram Message для юнит-тестов."""

    text: str
    from_user: FakeUser

    async def answer(self, text: str) -> str:
        # имитируем отправку ответа
        return text


@pytest.fixture
def fake_ai_client() -> FakeAIClient:
    return FakeAIClient("stub-response")


@pytest.fixture
def fake_telegram_message() -> FakeMessage:
    return FakeMessage(text="Привет", from_user=FakeUser(id=123))


@pytest.fixture
def temp_universities_file(tmp_path: Path) -> Path:
    data = [
        {"name": "Test Uni", "city": "Москва", "programs": ["IT"], "deadline": "01.01"},
        {"name": "Another Uni", "city": "СПб", "programs": ["Math"], "deadline": "02.02"},
    ]
    file_path = tmp_path / "universities.json"
    file_path.write_text(str(data), encoding="utf-8")
    return file_path
