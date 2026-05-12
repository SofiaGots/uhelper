"""Очистка пользовательского текста перед передачей агентам."""

from html import escape
from string import ascii_letters

MAX_USER_MESSAGE_LENGTH = 2_000
CYRILLIC_LETTERS = "абвгдеежзийклмнопрстуфхцчшщъыьэюяё"


def sanitize_user_text(text: str, max_length: int = MAX_USER_MESSAGE_LENGTH) -> str:
    """Очищает пользовательский текст от опасной разметки и лишних символов.

    Args:
        text: Сырой текст пользователя.
        max_length: Максимальная длина текста после обрезки.

    Returns:
        Очищенный текст.

    Raises:
        ValueError: Если текст пустой или содержит неподдерживаемый язык.
    """

    normalized = " ".join(text.replace("\x00", "").split())
    if not normalized:
        raise ValueError("message is empty")

    trimmed = normalized[:max_length]
    if not _is_supported_language(trimmed):
        raise ValueError("message language is not supported")

    return escape(trimmed, quote=True)


def _is_supported_language(text: str) -> bool:
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return True

    allowed_letters = set(ascii_letters + CYRILLIC_LETTERS + CYRILLIC_LETTERS.upper())
    return all(char in allowed_letters for char in letters)
