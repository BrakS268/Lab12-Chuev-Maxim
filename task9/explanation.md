# Задание 9: Аналитические SQL-запросы — Tutor Platform

## Схема базы данных

```
tutors    (id, full_name, email, subject, hourly_rate, experience_years, education, bio, is_active)
students  (id, full_name, email)
lessons   (id, tutor_id, student_id, scheduled_at, duration_minutes, status)
reviews   (id, tutor_id, student_id, rating, comment, created_at)
```

---

## Запрос 1: Топ-5 репетиторов по занятиям за 30 дней

**Бизнес-задача:** Найти самых активных репетиторов за последний месяц вместе с их рейтингом — для витрины платформы или расчёта бонусов.

```sql
SELECT
    t.id,
    t.full_name,
    t.subject,
    t.hourly_rate,
    COUNT(l.id)                       AS lessons_count,
    ROUND(AVG(r.rating)::NUMERIC, 2)  AS avg_rating,
    COUNT(r.id)                       AS reviews_count
FROM tutors t
JOIN lessons l
    ON l.tutor_id = t.id
    AND l.status = 'completed'
    AND l.scheduled_at >= NOW() - INTERVAL '30 days'
LEFT JOIN reviews r ON r.tutor_id = t.id
WHERE t.is_active = TRUE
GROUP BY t.id, t.full_name, t.subject, t.hourly_rate
ORDER BY lessons_count DESC, avg_rating DESC
LIMIT 5;
```

**Разбор логики:**

| Элемент | Зачем |
|---|---|
| `JOIN lessons` с фильтром `status = 'completed'` | Считаем только реально проведённые занятия |
| `scheduled_at >= NOW() - INTERVAL '30 days'` | Скользящее окно — последние 30 дней, а не календарный месяц |
| `LEFT JOIN reviews` | Репетитор без отзывов не пропадёт из результата |
| `AVG(r.rating)::NUMERIC` | Приводим к NUMERIC для `ROUND` (в PostgreSQL AVG возвращает float8) |
| `ORDER BY lessons_count DESC, avg_rating DESC` | Двойная сортировка: при равном числе занятий побеждает рейтинг |

---

## Запрос 2: Выручка репетиторов по месяцам за текущий год

**Бизнес-задача:** Финансовый отчёт — сколько заработал каждый репетитор помесячно для расчёта комиссии платформы.

```sql
SELECT
    t.full_name,
    t.subject,
    DATE_TRUNC('month', l.scheduled_at)             AS month,
    COUNT(l.id)                                     AS lessons_count,
    SUM(l.duration_minutes / 60.0 * t.hourly_rate)  AS revenue
FROM tutors t
JOIN lessons l
    ON l.tutor_id = t.id
    AND l.status = 'completed'
    AND EXTRACT(YEAR FROM l.scheduled_at) = EXTRACT(YEAR FROM NOW())
GROUP BY t.full_name, t.subject, month
ORDER BY t.full_name, month;
```

**Разбор логики:**

| Элемент | Зачем |
|---|---|
| `DATE_TRUNC('month', ...)` | Обрезает дату до начала месяца → удобная группировка |
| `duration_minutes / 60.0` | Делим на `60.0` (float), а не `60` (int) — иначе целочисленное деление |
| `* t.hourly_rate` | Ставка репетитора берётся из его анкеты |
| `EXTRACT(YEAR FROM NOW())` | Текущий год — работает без хардкода `2025` |

---

## Запрос 3: Студенты без отзывов, занимавшиеся с 2+ репетиторами

**Бизнес-задача:** Найти потенциально недовольных студентов (churn risk) — они активно пробовали разных репетиторов, но так ни разу не оставили отзыв.

```sql
SELECT
    s.id,
    s.full_name,
    s.email,
    COUNT(DISTINCT l.tutor_id)  AS tutors_count,
    COUNT(l.id)                 AS total_lessons
FROM students s
JOIN lessons l
    ON l.student_id = s.id
    AND l.status = 'completed'
WHERE s.id NOT IN (
    SELECT DISTINCT student_id FROM reviews
)
GROUP BY s.id, s.full_name, s.email
HAVING COUNT(DISTINCT l.tutor_id) > 2
ORDER BY total_lessons DESC;
```

**Разбор логики:**

| Элемент | Зачем |
|---|---|
| `WHERE ... NOT IN (subquery)` | Исключаем всех, кто хоть раз написал отзыв |
| `COUNT(DISTINCT l.tutor_id)` | Считаем уникальных репетиторов, а не занятия |
| `HAVING > 2` | Фильтр после агрегации — нельзя в `WHERE` |
| `ORDER BY total_lessons DESC` | Самые активные студенты без отзывов — первые кандидаты для retention |

> **Альтернатива `NOT IN`:** можно использовать `NOT EXISTS` или `LEFT JOIN ... WHERE r.id IS NULL` — они эффективнее при больших таблицах, так как `NOT IN` плохо работает при наличии NULL в подзапросе.
