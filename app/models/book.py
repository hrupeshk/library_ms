from sqlalchemy import Column, Integer, String, DateTime, func
from ..database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    isbn = Column(String(13), unique=True, nullable=False, index=True)
    total_copies = Column(Integer, nullable=False)
    available_copies = Column(Integer, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 