import logging

logger = logging.getLogger(__name__)


class AgentError(Exception):
    def __init__(
        self,
        message: str,
        *,
        session_id: str = "-",
        intent: str = "-",
        agent: str = "-",
    ) -> None:
        self.session_id = session_id
        self.intent = intent
        self.agent = agent
        super().__init__(message)


class IntentDetectionError(AgentError): ...


class LLMResponseError(AgentError): ...


class AgentProcessingError(AgentError): ...


class CircuitBreakerOpenError(AgentError): ...


SAFE_USER_MESSAGE = "Извините, произошла ошибка. Попробуйте позже."


def log_agent_error(exc: Exception, context: dict[str, str] | None = None) -> str:
    ctx = context or {}
    session_id = ctx.get("session_id", "-")
    intent = ctx.get("intent", "-")
    agent = ctx.get("agent", "-")

    if isinstance(exc, AgentError):
        session_id = exc.session_id or session_id
        intent = exc.intent or intent
        agent = exc.agent or agent

    logger.exception(
        "Agent error [session=%s intent=%s agent=%s] %s",
        session_id,
        intent,
        agent,
        exc,
        extra={"session_id": session_id, "intent": intent, "agent": agent},
    )

    return SAFE_USER_MESSAGE
