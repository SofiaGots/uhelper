import io
import logging

from src.utils.logging_config import _ContextFilter, _TokenMaskingFilter, setup_logging


def test_context_filter_adds_defaults() -> None:
    filter_ = _ContextFilter()
    record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
    assert filter_.filter(record)
    assert record.session_id == "-"
    assert record.intent == "-"
    assert record.agent == "-"


def test_context_filter_preserves_existing() -> None:
    filter_ = _ContextFilter()
    record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
    record.session_id = "s1"
    record.intent = "i1"
    assert filter_.filter(record)
    assert record.session_id == "s1"
    assert record.intent == "i1"
    assert record.agent == "-"


def test_token_masking_masks_telegram_token() -> None:
    filter_ = _TokenMaskingFilter()
    token = "8574516887:AAFTxF2D4YU7FqUPf1752DjDZeUm9mkoRKw"
    record = logging.LogRecord("test", logging.INFO, "", 0, f"Token: {token}", (), None)
    assert filter_.filter(record)
    assert "***MASKED***" in record.msg
    assert "AAFTxF2" not in record.msg


def test_token_masking_masks_openai_key() -> None:
    filter_ = _TokenMaskingFilter()
    key = "sk-test1234567890abcdefghijklmnopqrs"
    record = logging.LogRecord("test", logging.INFO, "", 0, f"Key: {key}", (), None)
    assert filter_.filter(record)
    assert "***MASKED***" in record.msg


def test_token_masking_leaves_clean_text() -> None:
    filter_ = _TokenMaskingFilter()
    record = logging.LogRecord(
        "test", logging.INFO, "", 0, "Normal log message without tokens", (), None
    )
    assert filter_.filter(record)
    assert record.msg == "Normal log message without tokens"


def test_setup_logging_has_masking_and_context() -> None:
    setup_logging(logging.DEBUG)
    root = logging.getLogger()
    assert len(root.handlers) == 1
    handler = root.handlers[0]
    filters = handler.filters
    assert any(isinstance(f, _TokenMaskingFilter) for f in filters)
    assert any(isinstance(f, _ContextFilter) for f in filters)


def test_log_output_contains_intent_and_agent(capsys: io.StringIO) -> None:
    setup_logging(logging.DEBUG)
    test_logger = logging.getLogger("test_logger")
    test_logger.info(
        "hello",
        extra={"session_id": "s1", "intent": "university_search", "agent": "UniversityAgent"},
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err
    assert "session=s1" in output
    assert "intent=university_search" in output
    assert "agent=UniversityAgent" in output
    assert "hello" in output


def test_masked_token_in_log_output(capsys: io.StringIO) -> None:
    setup_logging(logging.DEBUG)
    test_logger = logging.getLogger("test_logger")
    test_logger.info("TELEGRAM_BOT_TOKEN=8574516887:AAFTxF2D4YU7FqUPf1752DjDZeUm9mkoRKw")
    captured = capsys.readouterr()
    output = captured.out + captured.err
    assert "***MASKED***" in output
    assert "AAFTxF2D4YU7FqUPf" not in output
