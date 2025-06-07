from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: str = Field(..., min_length=10, max_length=13)
    total_copies: int = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=100)

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)
    total_copies: Optional[int] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=100)

class BookInDB(BookBase):
    id: int
    available_copies: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BookResponse(BookInDB):
    pass 