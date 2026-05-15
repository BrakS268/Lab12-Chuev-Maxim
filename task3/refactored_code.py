# refactored_code.py — рефакторинг bad_code.py
#
# Список изменений:
# 1. Функция calc() разбита на три самостоятельные функции с понятными именами:
#    calculate_revenue(), calculate_average_rating(), calculate_payout()
# 2. Магические числа (0.9, 0.8, 500, 0.06 и др.) вынесены в именованные константы
# 3. Добавлена обработка ошибок: ZeroDivisionError при пустом списке оценок,
#    ValueError при отрицательных значениях
# 4. Исправлены неинформативные имена: t→hours, s→ratings, r→cancellations,
#    x→revenue, nn→tax, cnt→count
# 5. Дублирование кода get_tutors_list / get_top устранено: оба используют
#    общий фильтр _filter_active_tutors(); сортировка заменена встроенным sorted()
# 6. Добавлены type hints и docstrings

from __future__ import annotations

from typing import Any

# ── Константы ────────────────────────────────────────────────────────────────

DISCOUNT_BY_EXPERIENCE: list[tuple[int, float]] = [
    (20, 0.70),
    (10, 0.80),
    (5,  0.90),
]

RATING_BONUS: list[tuple[float, float]] = [
    (4.5, 500.0),
    (4.0, 200.0),
]

CANCELLATION_PENALTY: list[tuple[int, float]] = [
    (20, 500.0),
    (10, 200.0),
    (3,  100.0),
]

TAX_RATE: float = 0.06          # налог самозанятого, %
TOP_TUTORS_COUNT: int = 10      # количество репетиторов в топе


# ── Вспомогательные функции ──────────────────────────────────────────────────

def calculate_average_rating(ratings: list[float]) -> float:
    """Вычисляет средний рейтинг репетитора.

    Args:
        ratings: список оценок занятий (от 1.0 до 5.0).

    Returns:
        Среднее арифметическое оценок.

    Raises:
        ValueError: если список оценок пуст.
    """
    if not ratings:
        raise ValueError("Список оценок не может быть пустым")
    return sum(ratings) / len(ratings)


def calculate_revenue(hours: float, hourly_rate: float, experience_years: int) -> float:
    """Рассчитывает выручку с учётом скидки за опыт репетитора.

    Args:
        hours: количество отработанных часов.
        hourly_rate: стоимость одного часа (руб.).
        experience_years: опыт преподавания (лет).

    Returns:
        Выручка до вычета налога и бонусов/штрафов.

    Raises:
        ValueError: если hours или hourly_rate отрицательны.
    """
    if hours < 0 or hourly_rate < 0:
        raise ValueError("Часы и ставка не могут быть отрицательными")

    base = hours * hourly_rate
    for min_years, factor in DISCOUNT_BY_EXPERIENCE:
        if experience_years >= min_years:
            return base * factor
    return base


def calculate_payout(
    hours: float,
    hourly_rate: float,
    experience_years: int,
    ratings: list[float],
    cancellations: int,
) -> dict[str, float]:
    """Рассчитывает итоговую выплату репетитору за период.

    Учитывает скидку за опыт, бонус за высокий рейтинг,
    штраф за отмены занятий и налог самозанятого.

    Args:
        hours: количество отработанных часов.
        hourly_rate: стоимость одного часа (руб.).
        experience_years: опыт преподавания (лет).
        ratings: список оценок занятий.
        cancellations: количество отменённых занятий.

    Returns:
        Словарь с ключами:
          - "revenue"   — выручка до корректировок
          - "bonus"     — рейтинговый бонус
          - "penalty"   — штраф за отмены
          - "tax"       — удержанный налог
          - "payout"    — итоговая выплата
          - "avg_rating"— средний рейтинг
    """
    avg_rating = calculate_average_rating(ratings)
    revenue = calculate_revenue(hours, hourly_rate, experience_years)

    bonus = next(
        (amount for threshold, amount in RATING_BONUS if avg_rating > threshold),
        0.0,
    )

    penalty = next(
        (amount for threshold, amount in CANCELLATION_PENALTY if cancellations > threshold),
        0.0,
    )

    gross = revenue + bonus - penalty
    tax = gross * TAX_RATE
    payout = gross - tax

    return {
        "revenue":    revenue,
        "bonus":      bonus,
        "penalty":    penalty,
        "tax":        tax,
        "payout":     payout,
        "avg_rating": avg_rating,
    }


# ── Работа со списком репетиторов ─────────────────────────────────────────────

def _filter_active_tutors(tutors_db: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    """Возвращает только активные анкеты из хранилища."""
    return [t for t in tutors_db.values() if t.get("is_active")]


def get_active_tutors(tutors_db: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    """Возвращает список всех активных репетиторов.

    Args:
        tutors_db: словарь {id: tutor_dict}.

    Returns:
        Список анкет активных репетиторов.
    """
    return _filter_active_tutors(tutors_db)


def get_top_tutors(
    tutors_db: dict[int, dict[str, Any]],
    count: int = TOP_TUTORS_COUNT,
) -> list[dict[str, Any]]:
    """Возвращает топ-N активных репетиторов по стоимости часа (по убыванию).

    Args:
        tutors_db: словарь {id: tutor_dict}.
        count: размер топа (по умолчанию TOP_TUTORS_COUNT).

    Returns:
        Список из не более чем ``count`` анкет.
    """
    active = _filter_active_tutors(tutors_db)
    return sorted(active, key=lambda t: t["hourly_rate"], reverse=True)[:count]