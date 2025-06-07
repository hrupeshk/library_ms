from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional
from ..database import get_db
from ..models.book import Book
from ..schemas.book import BookCreate, BookUpdate, BookResponse

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/", response_model=BookResponse)
async def create_book(book: BookCreate, db: AsyncSession = Depends(get_db)):
    # Check if ISBN already exists
    result = await db.execute(select(Book).where(Book.isbn == book.isbn))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="ISBN already exists")
    
    # Create new book
    db_book = Book(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        total_copies=book.total_copies,
        available_copies=book.total_copies,
        category=book.category
    )
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book

@router.get("/", response_model=List[BookResponse])
async def list_books(
    title: Optional[str] = None,
    author: Optional[str] = None,
    category: Optional[str] = None,
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(Book)
    
    # Apply filters
    if title:
        query = query.where(Book.title.ilike(f"%{title}%"))
    if author:
        query = query.where(Book.author.ilike(f"%{author}%"))
    if category:
        query = query.where(Book.category.ilike(f"%{category}%"))
    
    # Apply pagination
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    books = result.scalars().all()
    return books

@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book_update: BookUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Book).where(Book.id == book_id))
    db_book = result.scalar_one_or_none()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Update book fields
    update_data = book_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_book, field, value)
    
    # If total_copies is updated, adjust available_copies
    if "total_copies" in update_data:
        difference = update_data["total_copies"] - db_book.total_copies
        db_book.available_copies += difference
    
    await db.commit()
    await db.refresh(db_book)
    return db_book

@router.delete("/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Check if book has any active issues
    if book.available_copies < book.total_copies:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete book with active issues"
        )
    
    await db.delete(book)
    await db.commit()
    return {"message": "Book deleted successfully"} 