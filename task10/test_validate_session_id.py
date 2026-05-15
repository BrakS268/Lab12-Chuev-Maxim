import re
import pytest

# Регулярное выражение для ID занятия репетитора (формат: TUT-YYYY-XX)
SESSION_ID_PATTERN = re.compile(r'^TUT-20\d{2}-[A-Z]{2}$')


def validate_session_id(session_id: str) -> bool:
    return bool(SESSION_ID_PATTERN.match(session_id))


# ── Валидные ID ───────────────────────────────────────────────────────────────

@pytest.mark.parametrize("session_id", [
    "TUT-2024-MA",   # Математика, 2024
    "TUT-2025-EN",   # Английский, 2025
    "TUT-2000-PH",   # Физика, 2000 (граница диапазона)
    "TUT-2099-CH",   # Химия, 2099 (граница диапазона)
    "TUT-2010-RU",   # Русский, 2010
    "TUT-2033-BI",   # Биология, 2033
])
def test_valid_session_ids(session_id: str) -> None:
    assert validate_session_id(session_id), f"Ожидался валидный ID: {session_id!r}"


# ── Невалидные ID ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("session_id, reason", [
    ("TUT-999-MA",    "год из 3 цифр"),
    ("TUT-2024-M",    "одна буква предмета"),
    ("TUT-2024-Math", "слишком длинный суффикс предмета"),
    ("tut-2024-MA",   "строчный префикс"),
    ("TUT-2024-12",   "цифры вместо букв предмета"),
    ("TUT2024MA",     "нет дефисов"),
    ("TUT-1999-MA",   "год вне диапазона 2000–2099"),
    ("TUT-2024-",     "нет суффикса предмета"),
    ("",              "пустая строка"),
    ("TUT-2024-MAT",  "три буквы предмета"),
    (" TUT-2024-MA",  "пробел в начале строки"),
])
def test_invalid_session_ids(session_id: str, reason: str) -> None:
    assert not validate_session_id(session_id), f"Ожидался невалидный ID ({reason}): {session_id!r}"
