from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime, timedelta
from ..database import get_db
from ..models.book import Book
from ..models.student import Student
from ..models.book_issue import BookIssue, IssueStatus
from ..schemas.book_issue import BookIssueCreate, BookIssueResponse

router = APIRouter(prefix="/issues", tags=["book-issues"])

@router.post("/", response_model=BookIssueResponse)
async def issue_book(issue: BookIssueCreate, db: AsyncSession = Depends(get_db)):
    # Check if book exists and has available copies
    result = await db.execute(select(Book).where(Book.id == issue.book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="No copies available for this book")
    
    # Check if student exists
    result = await db.execute(select(Student).where(Student.id == issue.student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if student already has this book issued
    result = await db.execute(
        select(BookIssue).where(
            and_(
                BookIssue.book_id == issue.book_id,
                BookIssue.student_id == issue.student_id,
                BookIssue.status == IssueStatus.ISSUED
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Student already has this book issued"
        )
    
    # Create book issue
    db_issue = BookIssue(
        book_id=issue.book_id,
        student_id=issue.student_id,
        issue_date=issue.issue_date,
        return_date=issue.return_date,
        status=IssueStatus.ISSUED
    )
    
    # Update book available copies
    book.available_copies -= 1
    
    db.add(db_issue)
    await db.commit()
    await db.refresh(db_issue)
    return db_issue

@router.put("/{issue_id}/return", response_model=BookIssueResponse)
async def return_book(issue_id: int, db: AsyncSession = Depends(get_db)):
    # Get book issue
    result = await db.execute(
        select(BookIssue).where(
            and_(
                BookIssue.id == issue_id,
                BookIssue.status == IssueStatus.ISSUED
            )
        )
    )
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(
            status_code=404,
            detail="Active book issue not found"
        )
    
    # Update issue status and return date
    issue.status = IssueStatus.RETURNED
    issue.actual_return_date = datetime.now()
    
    # Update book available copies
    issue.book.available_copies += 1
    
    await db.commit()
    await db.refresh(issue)
    return issue

@router.get("/student/{student_id}", response_model=List[BookIssueResponse])
async def get_student_issues(student_id: int, db: AsyncSession = Depends(get_db)):
    # Check if student exists
    result = await db.execute(select(Student).where(Student.id == student_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get all issues for student
    query = (
        select(BookIssue)
        .options(selectinload(BookIssue.book), selectinload(BookIssue.student))
        .where(BookIssue.student_id == student_id)
        .order_by(BookIssue.created_at.desc())
    )
    result = await db.execute(query)
    issues = result.scalars().all()
    return issues

@router.get("/active", response_model=List[BookIssueResponse])
async def list_active_issues(
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all currently active book issues with pagination."""
    query = (
        select(BookIssue)
        .options(selectinload(BookIssue.book), selectinload(BookIssue.student))
        .where(BookIssue.status == IssueStatus.ISSUED)
        .order_by(BookIssue.return_date.asc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    
    result = await db.execute(query)
    issues = result.scalars().all()
    return issues

@router.get("/overdue", response_model=List[BookIssueResponse])
async def list_overdue_issues(
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all overdue book issues with pagination."""
    current_date = datetime.now()
    query = (
        select(BookIssue)
        .options(selectinload(BookIssue.book), selectinload(BookIssue.student))
        .where(
            and_(
                BookIssue.status == IssueStatus.ISSUED,
                BookIssue.return_date < current_date
            )
        )
        .order_by(BookIssue.return_date.asc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    
    result = await db.execute(query)
    issues = result.scalars().all()
    return issues

@router.get("/student/{student_id}/overdue", response_model=List[BookIssueResponse])
async def get_student_overdue_issues(
    student_id: int,
    db: AsyncSession = Depends(get_db)
):
    """List all overdue books for a specific student."""
    # Check if student exists
    result = await db.execute(select(Student).where(Student.id == student_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Student not found")
    
    current_date = datetime.now()
    query = (
        select(BookIssue)
        .options(selectinload(BookIssue.book), selectinload(BookIssue.student))
        .where(
            and_(
                BookIssue.student_id == student_id,
                BookIssue.status == IssueStatus.ISSUED,
                BookIssue.return_date < current_date
            )
        )
        .order_by(BookIssue.return_date.asc())
    )
    
    result = await db.execute(query)
    issues = result.scalars().all()
    return issues 