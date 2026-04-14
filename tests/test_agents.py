import pytest

from src.agents.base_agent import BaseAgent
from src.agents.orchestrator import OrchestratorAgent
from src.agents.profile_analyzer_agent import ProfileAnalyzerAgent
from src.agents.university_data_agent import UniversityDataAgent
from src.models.base import BaseAgentMessage
from tests.conftest import FakeLLM


class DummyAgent(BaseAgent):
    """Простой агент-заглушка для маршрутизации."""

    def __init__(self, intent: str) -> None:
        super().__init__()
        self.intent = intent
        self.processed = False

    def can_handle(self, intent: str) -> bool:
        return intent == self.intent

    async def process(self, message: BaseAgentMessage) -> BaseAgentMessage:
        self.processed = True
        message.agent_response = {"agent": self.intent, "response": "ok"}
        return message


@pytest.mark.asyncio
async def test_orchestrator_routes_to_matching_agent(fake_intent_llm: FakeLLM) -> None:
    university_agent = DummyAgent("university_search")
    profile_agent = DummyAgent("profile_analysis")
    orch = OrchestratorAgent((university_agent, profile_agent))
    orch.llm = fake_intent_llm  # подменяем LLM, чтобы вернуть нужный интент

    msg = BaseAgentMessage(
        user_id="1",
        session_id="1",
        intent="",
        message="Хочу про университеты",
        context={},
    )

    result = await orch.process(msg)

    assert university_agent.processed is True
    assert result.agent_response is not None
    assert result.agent_response["agent"] == "university_search"


@pytest.mark.asyncio
async def test_university_agent_filters_by_city() -> None:
    agent = UniversityDataAgent()
    response = await agent._search_universities("Москва")
    assert "Москва" in response
    assert "🏛️" in response


def test_profile_gpa_and_strengths(fake_profile_llm: FakeLLM) -> None:
    agent = ProfileAnalyzerAgent()
    agent.llm = fake_profile_llm

    grades = {"math": 5.0, "physics": 4.8, "history": 3.0}

    gpa = agent.calculate_gpa(grades)
    strengths = agent.identify_strengths(grades)

    assert pytest.approx(gpa, rel=1e-3) == 4.266
    assert "math" in strengths and "physics" in strengths
