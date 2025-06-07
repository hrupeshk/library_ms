from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    roll_number: str = Field(..., min_length=1, max_length=50)
    department: str = Field(..., min_length=1, max_length=100)
    semester: int = Field(..., gt=0, le=8)
    phone: str = Field(..., min_length=10, max_length=20)
    email: EmailStr

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    roll_number: Optional[str] = Field(None, min_length=1, max_length=50)
    department: Optional[str] = Field(None, min_length=1, max_length=100)
    semester: Optional[int] = Field(None, gt=0, le=8)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[EmailStr] = None

class StudentInDB(StudentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class StudentResponse(StudentInDB):
    pass 