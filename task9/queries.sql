-- ============================================================
-- Задание 9: Аналитические SQL-запросы — Tutor Platform
-- ============================================================

-- Предполагаемая схема БД:
--   tutors(id, full_name, email, subject, hourly_rate, experience_years, education, bio, is_active)
--   students(id, full_name, email)
--   lessons(id, tutor_id, student_id, scheduled_at, duration_minutes, status)
--     status: 'completed' | 'cancelled' | 'scheduled'
--   reviews(id, tutor_id, student_id, rating, comment, created_at)


-- ────────────────────────────────────────────────────────────
-- Запрос 1: Топ-5 репетиторов по количеству проведённых занятий
--           за последние 30 дней с их средним рейтингом
-- ────────────────────────────────────────────────────────────
SELECT
    t.id,
    t.full_name,
    t.subject,
    t.hourly_rate,
    COUNT(l.id)                          AS lessons_count,
    ROUND(AVG(r.rating)::NUMERIC, 2)     AS avg_rating,
    COUNT(r.id)                          AS reviews_count
FROM tutors t
JOIN lessons l
    ON l.tutor_id = t.id
    AND l.status = 'completed'
    AND l.scheduled_at >= NOW() - INTERVAL '30 days'
LEFT JOIN reviews r
    ON r.tutor_id = t.id
WHERE t.is_active = TRUE
GROUP BY t.id, t.full_name, t.subject, t.hourly_rate
ORDER BY lessons_count DESC, avg_rating DESC
LIMIT 5;

/*
  Логика:
  1. JOIN lessons — берём только завершённые занятия за последние 30 дней.
  2. LEFT JOIN reviews — рейтинг может отсутствовать (новый репетитор),
     поэтому LEFT JOIN, а не INNER.
  3. GROUP BY — агрегируем по каждому репетитору.
  4. ORDER BY lessons_count DESC — сначала самые активные;
     avg_rating DESC — при равном числе занятий выше тот, у кого лучше рейтинг.
  5. LIMIT 5 — топ-5.
*/


-- ────────────────────────────────────────────────────────────
-- Запрос 2: Выручка каждого репетитора по месяцам за текущий год
--           (только завершённые занятия)
-- ────────────────────────────────────────────────────────────
SELECT
    t.full_name,
    t.subject,
    DATE_TRUNC('month', l.scheduled_at)          AS month,
    COUNT(l.id)                                  AS lessons_count,
    SUM(l.duration_minutes / 60.0 * t.hourly_rate)  AS revenue
FROM tutors t
JOIN lessons l
    ON l.tutor_id = t.id
    AND l.status = 'completed'
    AND EXTRACT(YEAR FROM l.scheduled_at) = EXTRACT(YEAR FROM NOW())
GROUP BY t.full_name, t.subject, month
ORDER BY t.full_name, month;

/*
  Логика:
  1. DATE_TRUNC('month', ...) — группируем по месяцу (2025-01-01, 2025-02-01, ...).
  2. duration_minutes / 60.0 * hourly_rate — переводим минуты в часы
     и умножаем на ставку, получая выручку за каждое занятие.
  3. SUM(...) — суммарная выручка за месяц.
  4. EXTRACT(YEAR FROM NOW()) — только текущий год.
*/


-- ────────────────────────────────────────────────────────────
-- Запрос 3: Студенты, которые занимались более чем с 2 репетиторами,
--           но ни одному не оставили отзыв (потенциальный churn)
-- ────────────────────────────────────────────────────────────
SELECT
    s.id,
    s.full_name,
    s.email,
    COUNT(DISTINCT l.tutor_id)   AS tutors_count,
    COUNT(l.id)                  AS total_lessons
FROM students s
JOIN lessons l
    ON l.student_id = s.id
    AND l.status = 'completed'
WHERE s.id NOT IN (
    SELECT DISTINCT student_id
    FROM reviews
)
GROUP BY s.id, s.full_name, s.email
HAVING COUNT(DISTINCT l.tutor_id) > 2
ORDER BY total_lessons DESC;

/*
  Логика:
  1. WHERE s.id NOT IN (SELECT student_id FROM reviews) — исключаем тех,
     кто хоть раз оставил отзыв.
  2. COUNT(DISTINCT l.tutor_id) > 2 (HAVING) — только те, кто попробовал
     больше 2 репетиторов (признак активного поиска / неудовлетворённости).
  3. ORDER BY total_lessons DESC — наиболее вовлечённые студенты без отзывов
     идут первыми — приоритет для retention-кампании.
*/
