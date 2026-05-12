import pytest
from pydantic import ValidationError

from src.models.base import BaseAgentMessage
from src.utils.text_sanitizer import MAX_USER_MESSAGE_LENGTH, sanitize_user_text


def test_sanitize_user_text_escapes_html() -> None:
    sanitized = sanitize_user_text("<b>МГУ</b> & help")

    assert sanitized == "&lt;b&gt;МГУ&lt;/b&gt; &amp; help"


def test_base_agent_message_truncates_text() -> None:
    message = BaseAgentMessage(
        user_id="1",
        session_id="1",
        intent="",
        message="a" * (MAX_USER_MESSAGE_LENGTH + 100),
        context={},
    )

    assert len(message.message) == MAX_USER_MESSAGE_LENGTH


def test_base_agent_message_rejects_unsupported_language() -> None:
    with pytest.raises(ValidationError):
        BaseAgentMessage(
            user_id="1",
            session_id="1",
            intent="",
            message="你好",
            context={},
        )
