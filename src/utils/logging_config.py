"""Базовая настройка логирования для приложения."""

import logging
import re

_TOKEN_MASKS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(TELEGRAM_BOT_TOKEN[=:]\s*)\S+", re.IGNORECASE), r"\g<1>***MASKED***"),
    (re.compile(r"(OPENAI_API_KEY[=:]\s*)\S+", re.IGNORECASE), r"\g<1>***MASKED***"),
    (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "***MASKED***"),
    (re.compile(r"\d{8,10}:[a-zA-Z0-9_-]{30,}"), "***MASKED***"),
]


class _TokenMaskingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern, replacement in _TOKEN_MASKS:
                record.msg = pattern.sub(replacement, record.msg)
        return True


class _ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        for field in ("session_id", "request_id", "intent", "agent"):
            if not hasattr(record, field):
                setattr(record, field, "-")
        return True


def setup_logging(level: int = logging.INFO) -> None:
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s "
        "[session=%(session_id)s intent=%(intent)s agent=%(agent)s] "
        "%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.addFilter(_TokenMaskingFilter())
    handler.addFilter(_ContextFilter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)
