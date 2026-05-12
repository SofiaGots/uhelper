from src.agents.exceptions import (
    SAFE_USER_MESSAGE,
    AgentError,
    AgentProcessingError,
    CircuitBreakerOpenError,
    IntentDetectionError,
    LLMResponseError,
    log_agent_error,
)


def test_agent_error_has_context() -> None:
    err = AgentError("test", session_id="s1", intent="i1", agent="a1")
    assert err.session_id == "s1"
    assert err.intent == "i1"
    assert err.agent == "a1"
    assert "test" in str(err)


def test_intent_detection_error_inherits() -> None:
    err = IntentDetectionError("bad intent", session_id="s2")
    assert isinstance(err, AgentError)
    assert err.session_id == "s2"


def test_llm_response_error_inherits() -> None:
    err = LLMResponseError("llm fail", agent="llm_agent")
    assert isinstance(err, AgentError)
    assert err.agent == "llm_agent"


def test_agent_processing_error_inherits() -> None:
    err = AgentProcessingError("processing fail")
    assert isinstance(err, AgentError)


def test_circuit_breaker_open_error_inherits() -> None:
    err = CircuitBreakerOpenError("cb open")
    assert isinstance(err, AgentError)


def test_log_agent_error_returns_safe_message() -> None:
    err = RuntimeError("something bad")
    result = log_agent_error(err)
    assert result == SAFE_USER_MESSAGE


def test_log_agent_error_uses_agent_error_context() -> None:
    err = IntentDetectionError("fail", session_id="s3", intent="i3", agent="a3")
    result = log_agent_error(err)
    assert result == SAFE_USER_MESSAGE


def test_log_agent_error_merges_context_overrides() -> None:
    err = IntentDetectionError("fail", session_id="s_old", intent="i_old", agent="a_old")
    result = log_agent_error(err, {"session_id": "s_new", "agent": "a_new"})
    assert result == SAFE_USER_MESSAGE
