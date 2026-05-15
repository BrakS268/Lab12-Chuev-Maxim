# Объяснение бизнес-логики: расчёт выплаты репетитору

## Фрагмент кода

```python
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

TAX_RATE: float = 0.06

def calculate_payout(
    hours: float,
    hourly_rate: float,
    experience_years: int,
    ratings: list[float],
    cancellations: int,
) -> dict[str, float]:
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
```

---

## Объяснение простым языком

### Что делает функция в целом

`calculate_payout` считает итоговую выплату репетитору за период — с учётом его опыта,
рейтинга от учеников и количества отменённых занятий. Возвращает не одно число,
а словарь с разбивкой: выручка, бонус, штраф, налог, итого.

---

### Шаг 1 — Базовая выручка с учётом опыта

```python
revenue = calculate_revenue(hours, hourly_rate, experience_years)
```

Внутри `calculate_revenue` список `DISCOUNT_BY_EXPERIENCE` читается сверху вниз.
Берётся **первый** подходящий порог:

| Опыт (лет) | Коэффициент | Пример: 10 ч × 1000 руб. |
|---|---|---|
| ≥ 20 | 0.70 | 7 000 руб. |
| ≥ 10 | 0.80 | 8 000 руб. |
| ≥ 5  | 0.90 | 9 000 руб. |
| < 5  | 1.00 | 10 000 руб. |

Логика кажется контринтуитивной: чем больше опыт — тем меньше коэффициент.
На самом деле это **скидка платформы** — опытные репетиторы привлекают больше учеников,
поэтому платформа берёт бо́льшую комиссию.

---

### Шаг 2 — Бонус за высокий рейтинг

```python
bonus = next(
    (amount for threshold, amount in RATING_BONUS if avg_rating > threshold),
    0.0,
)
```

`next()` берёт **первый** элемент генератора, который удовлетворяет условию,
или `0.0` если ни один не подошёл. Список `RATING_BONUS` отсортирован по убыванию порога —
это важно, иначе репетитор с рейтингом 4.8 получил бы бонус 200 вместо 500.

| Средний рейтинг | Бонус |
|---|---|
| > 4.5 | +500 руб. |
| > 4.0 | +200 руб. |
| ≤ 4.0 | 0 руб. |

---

### Шаг 3 — Штраф за отмены

```python
penalty = next(
    (amount for threshold, amount in CANCELLATION_PENALTY if cancellations > threshold),
    0.0,
)
```

Та же механика `next()`, но для отмён. Берётся только **один** штраф — наибольший подходящий:

| Отмен | Штраф |
|---|---|
| > 20 | −500 руб. |
| > 10 | −200 руб. |
| > 3  | −100 руб. |
| ≤ 3  | 0 руб. |

---

### Шаг 4 — Налог и итог

```python
gross = revenue + bonus - penalty
tax = gross * TAX_RATE   # 6% — налог самозанятого
payout = gross - tax
```

`TAX_RATE = 0.06` соответствует ставке налога на профессиональный доход (НПД)
для самозанятых в России. Налог считается от итоговой суммы после бонусов и штрафов.

---

## Предложения по улучшению

### 1. Защита от отрицательной выплаты
Если штраф больше выручки — `payout` уйдёт в минус. Стоит добавить ограничение:

```python
payout = max(0.0, gross - tax)
```

### 2. Логирование для аудита
В реальной системе каждый расчёт выплаты нужно логировать:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Payout calculated: tutor_id=%s, payout=%.2f", tutor_id, payout)
```

### 3. Вынести налоговую ставку в конфиг
`TAX_RATE` может меняться (например, для ИП ставка другая). Лучше читать из переменной окружения:

```python
import os
TAX_RATE: float = float(os.getenv("TAX_RATE", "0.06"))
```

### 4. Добавить dataclass вместо словаря
Возвращать типизированный объект надёжнее, чем `dict[str, float]`:

```python
from dataclasses import dataclass

@dataclass
class PayoutResult:
    revenue: float
    bonus: float
    penalty: float
    tax: float
    payout: float
    avg_rating: float
```