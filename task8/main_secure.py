from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
import uvicorn
import logging
import re
import time
from collections import defaultdict

# ── Логирование ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── Приложение ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Tutor Platform API (Secure)",
    description="REST API для управления анкетами репетиторов — защищённая версия",
    version="2.0.0",
)

# ── ИСПРАВЛЕНИЕ 5: CORS — разрешаем только доверенные источники ──────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://tutor-platform.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# ── ИСПРАВЛЕНИЕ 3: Rate Limiting (простая реализация in-memory) ───────────────
# В продакшене использовать slowapi + Redis
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = 60        # запросов
RATE_WINDOW = 60.0     # секунд


def rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - RATE_WINDOW

    # Чистим старые метки
    _rate_limit_store[client_ip] = [
        ts for ts in _rate_limit_store[client_ip] if ts > window_start
    ]

    if len(_rate_limit_store[client_ip]) >= RATE_LIMIT:
        logger.warning("Rate limit exceeded for IP: %s", client_ip)
        raise HTTPException(
            status_code=429,
            detail="Слишком много запросов. Попробуйте позже.",
        )

    _rate_limit_store[client_ip].append(now)


# ── ИСПРАВЛЕНИЕ 2: Модели с валидацией email и дополнительными проверками ─────
class TutorBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="ФИО репетитора")
    # EmailStr проверяет корректный формат email (было: просто str)
    email: EmailStr = Field(..., description="Email репетитора")
    subject: str = Field(..., min_length=2, max_length=50, description="Предмет обучения")
    hourly_rate: float = Field(..., ge=0, le=100_000, description="Стоимость занятия в час (руб.)")
    experience_years: int = Field(..., ge=0, le=60, description="Опыт преподавания (лет)")
    education: str = Field(..., min_length=5, max_length=300, description="Образование")
    bio: Optional[str] = Field(None, max_length=1000, description="О себе")
    is_active: bool = Field(default=True, description="Активна ли анкета")

    # ИСПРАВЛЕНИЕ 6: Дополнительная валидация — защита от script-инъекций в текстовых полях
    @field_validator("full_name", "subject", "education", "bio", mode="before")
    @classmethod
    def strip_dangerous_chars(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Запрещаем HTML-теги (базовая XSS-защита)
        if re.search(r"<[^>]+>", v):
            raise ValueError("Поле не должно содержать HTML-теги")
        return v.strip()

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class TutorCreate(TutorBase):
    pass


class TutorUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    subject: Optional[str] = Field(None, min_length=2, max_length=50)
    hourly_rate: Optional[float] = Field(None, ge=0, le=100_000)
    experience_years: Optional[int] = Field(None, ge=0, le=60)
    education: Optional[str] = Field(None, min_length=5, max_length=300)
    bio: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None

    @field_validator("full_name", "subject", "education", "bio", mode="before")
    @classmethod
    def strip_dangerous_chars(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if re.search(r"<[^>]+>", v):
            raise ValueError("Поле не должно содержать HTML-теги")
        return v.strip()


class TutorResponse(TutorBase):
    id: int

    class ConfigDict:
        from_attributes = True


# ── База данных (in-memory, как в оригинале) ──────────────────────────────────
# ИСПРАВЛЕНИЕ 4: В продакшене заменить на реальную БД (PostgreSQL + SQLAlchemy)
# с транзакциями и connection pooling
tutors_db: dict[int, dict] = {}
_next_id: int = 1


# ── Эндпоинты ─────────────────────────────────────────────────────────────────

@app.get(
    "/tutors",
    response_model=list[TutorResponse],
    summary="Получить список всех репетиторов",
    # ИСПРАВЛЕНИЕ 1: в продакшене здесь добавить dependencies=[Depends(verify_token)]
)
def get_tutors(
    request: Request,
    _: None = Depends(rate_limit),
) -> list[TutorResponse]:
    logger.info("GET /tutors | IP: %s | count: %d", request.client.host if request.client else "?", len(tutors_db))
    return [TutorResponse(id=tid, **data) for tid, data in tutors_db.items()]


@app.post(
    "/tutors",
    response_model=TutorResponse,
    status_code=201,
    summary="Создать анкету репетитора",
)
def create_tutor(
    tutor: TutorCreate,
    request: Request,
    _: None = Depends(rate_limit),
) -> TutorResponse:
    global _next_id
    tutor_data = tutor.model_dump()
    tutors_db[_next_id] = tutor_data
    logger.info("POST /tutors | IP: %s | created id=%d", request.client.host if request.client else "?", _next_id)
    response = TutorResponse(id=_next_id, **tutor_data)
    _next_id += 1
    return response


@app.get(
    "/tutors/{tutor_id}",
    response_model=TutorResponse,
    summary="Получить репетитора по ID",
)
def get_tutor(
    tutor_id: int,
    request: Request,
    _: None = Depends(rate_limit),
) -> TutorResponse:
    if tutor_id not in tutors_db:
        logger.warning("GET /tutors/%d | not found | IP: %s", tutor_id, request.client.host if request.client else "?")
        raise HTTPException(status_code=404, detail=f"Репетитор с id={tutor_id} не найден")
    return TutorResponse(id=tutor_id, **tutors_db[tutor_id])


@app.put(
    "/tutors/{tutor_id}",
    response_model=TutorResponse,
    summary="Обновить анкету репетитора",
)
def update_tutor(
    tutor_id: int,
    tutor_update: TutorUpdate,
    request: Request,
    _: None = Depends(rate_limit),
) -> TutorResponse:
    if tutor_id not in tutors_db:
        raise HTTPException(status_code=404, detail=f"Репетитор с id={tutor_id} не найден")
    update_data = tutor_update.model_dump(exclude_none=True)
    tutors_db[tutor_id].update(update_data)
    logger.info("PUT /tutors/%d | IP: %s | fields: %s", tutor_id, request.client.host if request.client else "?", list(update_data.keys()))
    return TutorResponse(id=tutor_id, **tutors_db[tutor_id])


@app.delete(
    "/tutors/{tutor_id}",
    status_code=204,
    summary="Удалить анкету репетитора",
)
def delete_tutor(
    tutor_id: int,
    request: Request,
    _: None = Depends(rate_limit),
) -> None:
    if tutor_id not in tutors_db:
        raise HTTPException(status_code=404, detail=f"Репетитор с id={tutor_id} не найден")
    del tutors_db[tutor_id]
    logger.info("DELETE /tutors/%d | IP: %s", tutor_id, request.client.host if request.client else "?")


if __name__ == "__main__":
    uvicorn.run("main_secure:app", host="0.0.0.0", port=8000, reload=True)
