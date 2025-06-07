from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .book import BookResponse
from .student import StudentResponse
from ..models.book_issue import IssueStatus

class BookIssueBase(BaseModel):
    book_id: int
    student_id: int
    issue_date: datetime
    return_date: datetime

class BookIssueCreate(BookIssueBase):
    pass

class BookIssueUpdate(BaseModel):
    actual_return_date: Optional[datetime] = None
    status: Optional[IssueStatus] = None

class BookIssueInDB(BookIssueBase):
    id: int
    actual_return_date: Optional[datetime] = None
    status: IssueStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BookIssueResponse(BookIssueInDB):
    book: BookResponse
    student: StudentResponse 