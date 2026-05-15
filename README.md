# Lab12-Chuev-Maxim
**Лабораторная работа 12**

**Студент:** Чуев Максим Сергеевич 

**Группа:** 220032-11 

**Вариант:** 29

**Сложность:** средняя

---

# Tutor Platform API

## Содержание

- [Описание проекта](#описание-проекта)
- [Структура репозитория](#структура-репозитория)
- [Технологии](#технологии)
- [Установка и запуск](#установка-и-запуск)
  - [Локальный запуск](#локальный-запуск)
  - [Запуск через Docker](#запуск-через-docker)
- [Переменные окружения](#переменные-окружения)
- [API — эндпоинты](#api--эндпоинты)
- [Примеры запросов](#примеры-запросов)
- [Запуск тестов](#запуск-тестов)

---

## Описание проекта

Платформа предоставляет REST API для работы с анкетами репетиторов: создание, просмотр, редактирование и удаление профилей. Каждая анкета содержит контактные данные, преподаваемый предмет, стоимость занятий, опыт и образование репетитора.

Предметная область охватывает: анкеты, предметы, расписание, занятия, отзывы.

---

## Технологии

| Компонент    | Версия / инструмент         |
|--------------|-----------------------------|
| Python       | 3.12                        |
| FastAPI      | последняя стабильная        |
| Pydantic     | v2                          |
| PostgreSQL   | 16-alpine (Docker)          |
| Alembic      | миграции БД                 |
| Uvicorn      | ASGI-сервер                 |
| Docker       | Dockerfile + docker-compose |
| Pytest       | модульные тесты             |

---

## Установка и запуск

### Локальный запуск

> Требуется Python 3.12+ и работающий PostgreSQL.

```bash
# 1. Клонировать репозиторий
git clone https://github.com/BrakS268/Lab12-Chuev-Maxim.git
cd Lab12-Chuev-Maxim

# 2. Создать и активировать виртуальное окружение
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Установить зависимости
pip install -r task1-2/requirements.txt

# 4. Настроить переменные окружения
cp .env.example .env
# Отредактируй .env под свою БД

# 5. Применить миграции
alembic upgrade head

# 6. Запустить приложение
uvicorn task1-2.main:app --host 0.0.0.0 --port 8000 --reload
```

Приложение будет доступно на `http://localhost:8000`.  
Swagger UI — `http://localhost:8000/docs`.

---

### Запуск через Docker

> Требуется Docker и Docker Compose.

```bash
# 1. Клонировать репозиторий
git clone https://github.com/BrakS268/Lab12-Chuev-Maxim.git
cd Lab12-Chuev-Maxim

# 2. Настроить переменные окружения
cp .env.example .env
# При необходимости отредактируй .env

# 3. Собрать и запустить все сервисы
docker compose up --build
```

Docker Compose поднимает два сервиса:

- **db** — PostgreSQL 16, хранит данные в именованном volume `postgres_data`
- **app** — FastAPI-приложение; при старте автоматически выполняет `alembic upgrade head`, затем запускает uvicorn

Приложение будет доступно на `http://localhost:8000`.

Для остановки:
```bash
docker compose down
```

Для полной очистки (включая данные БД):
```bash
docker compose down -v
```

---

## Переменные окружения

Скопируй `.env.example` в `.env` и заполни своими значениями:

| Переменная          | Значение по умолчанию                                      | Описание                              |
|---------------------|------------------------------------------------------------|---------------------------------------|
| `POSTGRES_DB`       | `tutor_platform`                                           | Имя базы данных PostgreSQL            |
| `POSTGRES_USER`     | `tutor`                                                    | Пользователь PostgreSQL               |
| `POSTGRES_PASSWORD` | `secret`                                                   | Пароль PostgreSQL                     |
| `APP_ENV`           | `production`                                               | Окружение приложения                  |
| `DATABASE_URL`      | `postgresql://tutor:secret@db:5432/tutor_platform`         | Строка подключения к БД               |

> ⚠️ В продакшене обязательно смени `POSTGRES_PASSWORD` на надёжный пароль и не коммить `.env` в репозиторий.

---

## API — эндпоинты

Базовый URL: `http://localhost:8000`

| Метод    | Путь                  | Описание                             |
|----------|-----------------------|--------------------------------------|
| `GET`    | `/tutors`             | Получить список всех репетиторов     |
| `POST`   | `/tutors`             | Создать анкету репетитора            |
| `GET`    | `/tutors/{id}`        | Получить репетитора по ID            |
| `PUT`    | `/tutors/{id}`        | Обновить анкету (частичное/полное)   |
| `DELETE` | `/tutors/{id}`        | Удалить анкету репетитора            |

### Модель репетитора

| Поле               | Тип      | Обязательное | Описание                            |
|--------------------|----------|:------------:|-------------------------------------|
| `id`               | `int`    | авто         | Уникальный идентификатор            |
| `full_name`        | `str`    | ✅           | ФИО репетитора (2–100 символов)     |
| `email`            | `str`    | ✅           | Email репетитора                    |
| `subject`          | `str`    | ✅           | Преподаваемый предмет (2–50 симв.)  |
| `hourly_rate`      | `float`  | ✅           | Стоимость занятия в час, руб. (≥ 0) |
| `experience_years` | `int`    | ✅           | Опыт преподавания, лет (0–60)       |
| `education`        | `str`    | ✅           | Образование (5–300 символов)        |
| `bio`              | `str`    | ❌           | О себе (до 1000 символов)           |
| `is_active`        | `bool`   | ❌           | Активна ли анкета (default: `true`) |

---

## Примеры запросов

### Создать анкету репетитора

```bash
curl -X POST http://localhost:8000/tutors \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Иванов Иван Иванович",
    "email": "ivanov@example.com",
    "subject": "Математика",
    "hourly_rate": 1500.0,
    "experience_years": 5,
    "education": "МГУ, мехмат, специалитет",
    "bio": "Готовлю к ЕГЭ и ОГЭ"
  }'
```

**Ответ `201 Created`:**
```json
{
  "id": 1,
  "full_name": "Иванов Иван Иванович",
  "email": "ivanov@example.com",
  "subject": "Математика",
  "hourly_rate": 1500.0,
  "experience_years": 5,
  "education": "МГУ, мехмат, специалитет",
  "bio": "Готовлю к ЕГЭ и ОГЭ",
  "is_active": true
}
```

---

### Получить список всех репетиторов

```bash
curl http://localhost:8000/tutors
```

**Ответ `200 OK`:**
```json
[
  {
    "id": 1,
    "full_name": "Иванов Иван Иванович",
    "subject": "Математика",
    "hourly_rate": 1500.0,
    ...
  }
]
```

---

### Получить репетитора по ID

```bash
curl http://localhost:8000/tutors/1
```

**Ответ `404 Not Found` (если не существует):**
```json
{
  "detail": "Репетитор с id=1 не найден"
}
```

---

### Частичное обновление анкеты

```bash
curl -X PUT http://localhost:8000/tutors/1 \
  -H "Content-Type: application/json" \
  -d '{"hourly_rate": 2000.0, "is_active": false}'
```

---

### Удалить анкету

```bash
curl -X DELETE http://localhost:8000/tutors/1
```

**Ответ `204 No Content`** — тело пустое.

---

## Запуск тестов

```bash
cd task1-2
pip install pytest httpx
pytest test_main.py -v
```

Тесты покрывают: CREATE (6), READ (4), UPDATE (4), DELETE (3), граничные случаи (3) — итого **22 теста**.

---

> Интерактивная документация Swagger доступна по адресу `http://localhost:8000/docs` после запуска приложения.
