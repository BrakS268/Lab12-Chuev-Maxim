from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import uvicorn

app = FastAPI(
    title="Tutor Platform API",
    description="REST API для управления анкетами репетиторов",
    version="1.0.0",
)


class TutorBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="ФИО репетитора")
    email: str = Field(..., description="Email репетитора")
    subject: str = Field(..., min_length=2, max_length=50, description="Предмет обучения")
    hourly_rate: float = Field(..., ge=0, description="Стоимость занятия в час (руб.)")
    experience_years: int = Field(..., ge=0, le=60, description="Опыт преподавания (лет)")
    education: str = Field(..., min_length=5, max_length=300, description="Образование")
    bio: Optional[str] = Field(None, max_length=1000, description="О себе")
    is_active: bool = Field(default=True, description="Активна ли анкета")


class TutorCreate(TutorBase):
    pass


class TutorUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = None
    subject: Optional[str] = Field(None, min_length=2, max_length=50)
    hourly_rate: Optional[float] = Field(None, ge=0)
    experience_years: Optional[int] = Field(None, ge=0, le=60)
    education: Optional[str] = Field(None, min_length=5, max_length=300)
    bio: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None


class TutorResponse(TutorBase):
    id: int

    class ConfigDict:
        from_attributes = True



tutors_db: dict[int, dict] = {}
_next_id: int = 1



@app.get("/tutors", response_model=list[TutorResponse], summary="Получить список всех репетиторов")
def get_tutors() -> list[TutorResponse]:
    return [TutorResponse(id=tid, **data) for tid, data in tutors_db.items()]


@app.post("/tutors", response_model=TutorResponse, status_code=201, summary="Создать анкету репетитора")
def create_tutor(tutor: TutorCreate) -> TutorResponse:
    global _next_id
    tutor_data = tutor.model_dump()
    tutors_db[_next_id] = tutor_data
    response = TutorResponse(id=_next_id, **tutor_data)
    _next_id += 1
    return response


@app.get("/tutors/{tutor_id}", response_model=TutorResponse, summary="Получить репетитора по ID")
def get_tutor(tutor_id: int) -> TutorResponse:
    if tutor_id not in tutors_db:
        raise HTTPException(status_code=404, detail=f"Репетитор с id={tutor_id} не найден")
    return TutorResponse(id=tutor_id, **tutors_db[tutor_id])


@app.put("/tutors/{tutor_id}", response_model=TutorResponse, summary="Обновить анкету репетитора")
def update_tutor(tutor_id: int, tutor_update: TutorUpdate) -> TutorResponse:
    if tutor_id not in tutors_db:
        raise HTTPException(status_code=404, detail=f"Репетитор с id={tutor_id} не найден")
    
    update_data = tutor_update.model_dump(exclude_none=True)
    tutors_db[tutor_id].update(update_data)
    return TutorResponse(id=tutor_id, **tutors_db[tutor_id])


@app.delete("/tutors/{tutor_id}", status_code=204, summary="Удалить анкету репетитора")
def delete_tutor(tutor_id: int) -> None:
    if tutor_id not in tutors_db:
        raise HTTPException(status_code=404, detail=f"Репетитор с id={tutor_id} не найден")
    del tutors_db[tutor_id]


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    