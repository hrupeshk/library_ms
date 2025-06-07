from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import relationship
import enum
from ..database import Base

class IssueStatus(str, enum.Enum):
    ISSUED = "issued"
    RETURNED = "returned"
    OVERDUE = "overdue"

class BookIssue(Base):
    __tablename__ = "book_issues"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    issue_date = Column(DateTime(timezone=True), nullable=False)
    return_date = Column(DateTime(timezone=True), nullable=False)
    actual_return_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(IssueStatus), nullable=False, default=IssueStatus.ISSUED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    book = relationship("Book", backref="issues")
    student = relationship("Student", backref="issues") 