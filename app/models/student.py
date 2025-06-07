from sqlalchemy import Column, Integer, String, DateTime, func
from ..database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    roll_number = Column(String(50), unique=True, nullable=False, index=True)
    department = Column(String(100), nullable=False, index=True)
    semester = Column(Integer, nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 