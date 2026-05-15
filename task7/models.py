from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from database import Base


class Tutor(Base):
    __tablename__ = "tutors"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    subject = Column(String(50), nullable=False, index=True)
    hourly_rate = Column(Float, nullable=False)
    experience_years = Column(Integer, nullable=False)
    education = Column(String(300), nullable=False)
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
