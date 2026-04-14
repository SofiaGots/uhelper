"""Базовая настройка логирования для приложения."""

import logging


class _ContextFilter(logging.Filter):
    """Гарантирует наличие полей session_id и request_id в записях логов."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        if not hasattr(record, "session_id"):
            record.session_id = "-"
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


def setup_logging(level: int = logging.INFO) -> None:
    """Инициализирует конфигурацию логов (stdout, INFO/ERROR).

    Args:
        level: Минимальный уровень логирования.
    """

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s "
        "[session=%(session_id)s request=%(request_id)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.addFilter(_ContextFilter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)
