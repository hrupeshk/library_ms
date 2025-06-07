from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models.book import Book
from ..models.student import Student
from ..models.book_issue import BookIssue
from pydantic import BaseModel
import json
import asyncio

router = APIRouter()

class Question(BaseModel):
    text: str

# Intent patterns and their corresponding queries
INTENT_PATTERNS = {
    "overdue_books": [
        "how many books are overdue",
        "list overdue books",
        "show me overdue books",
        "what books are overdue"
    ],
    "department_borrows": [
        "which department borrowed the most books",
        "department with most borrows",
        "top borrowing department",
        "most active department"
    ],
    "new_books": [
        "how many new books were added",
        "recently added books",
        "new books this week",
        "latest additions"
    ],
    "active_students": [
        "most active students",
        "top borrowers",
        "students with most books",
        "who borrowed the most"
    ],
    "popular_books": [
        "most popular books",
        "most borrowed books",
        "top books",
        "frequently borrowed books"
    ]
}

async def get_overdue_books(db: AsyncSession) -> List[Dict[str, Any]]:
    result = await db.execute(
        select(BookIssue, Book, Student)
        .join(Book, BookIssue.book_id == Book.id)
        .join(Student, BookIssue.student_id == Student.id)
        .where(
            and_(
                BookIssue.status == "ISSUED",
                BookIssue.return_date < datetime.now()
            )
        )
    )
    issues = result.all()
    return [
        {
            "book_title": issue.Book.title,
            "student_name": issue.Student.name,
            "days_overdue": (datetime.now() - issue.BookIssue.return_date).days
        }
        for issue in issues
    ]

async def get_department_borrows(db: AsyncSession) -> List[Dict[str, Any]]:
    result = await db.execute(
        select(
            Student.department,
            func.count(BookIssue.id).label("total_borrows")
        )
        .join(BookIssue, Student.id == BookIssue.student_id)
        .group_by(Student.department)
        .order_by(desc("total_borrows"))
    )
    return [{"department": dept, "total_borrows": count} for dept, count in result.all()]

async def get_new_books(db: AsyncSession) -> List[Dict[str, Any]]:
    week_ago = datetime.now() - timedelta(days=7)
    result = await db.execute(
        select(Book)
        .where(Book.created_at >= week_ago)
        .order_by(desc(Book.created_at))
    )
    books = result.scalars().all()
    return [
        {
            "title": book.title,
            "author": book.author,
            "added_date": book.created_at.strftime("%Y-%m-%d")
        }
        for book in books
    ]

async def get_active_students(db: AsyncSession) -> List[Dict[str, Any]]:
    result = await db.execute(
        select(
            Student.name,
            Student.department,
            func.count(BookIssue.id).label("total_borrows")
        )
        .join(BookIssue, Student.id == BookIssue.student_id)
        .group_by(Student.id)
        .order_by(desc("total_borrows"))
        .limit(5)
    )
    return [
        {
            "name": name,
            "department": dept,
            "total_borrows": count
        }
        for name, dept, count in result.all()
    ]

async def get_popular_books(db: AsyncSession) -> List[Dict[str, Any]]:
    result = await db.execute(
        select(
            Book.title,
            Book.author,
            func.count(BookIssue.id).label("borrow_count")
        )
        .join(BookIssue, Book.id == BookIssue.book_id)
        .group_by(Book.id)
        .order_by(desc("borrow_count"))
        .limit(5)
    )
    return [
        {
            "title": title,
            "author": author,
            "times_borrowed": count
        }
        for title, author, count in result.all()
    ]

def detect_intent(question: str) -> str:
    question = question.lower().strip()
    for intent, patterns in INTENT_PATTERNS.items():
        if any(pattern in question for pattern in patterns):
            return intent
    return "unknown"

async def generate_response(intent: str, db: AsyncSession) -> str:
    if intent == "overdue_books":
        overdue = await get_overdue_books(db)
        if not overdue:
            return "There are no overdue books at the moment."
        response = f"Found {len(overdue)} overdue books:\n"
        for book in overdue:
            response += f"- {book['book_title']} (borrowed by {book['student_name']}, {book['days_overdue']} days overdue)\n"
        return response

    elif intent == "department_borrows":
        dept_stats = await get_department_borrows(db)
        if not dept_stats:
            return "No borrowing data available."
        response = "Department borrowing statistics:\n"
        for dept in dept_stats:
            response += f"- {dept['department']}: {dept['total_borrows']} books borrowed\n"
        return response

    elif intent == "new_books":
        new_books = await get_new_books(db)
        if not new_books:
            return "No new books have been added in the last week."
        response = f"Added {len(new_books)} new books this week:\n"
        for book in new_books:
            response += f"- {book['title']} by {book['author']} (added on {book['added_date']})\n"
        return response

    elif intent == "active_students":
        students = await get_active_students(db)
        if not students:
            return "No borrowing data available."
        response = "Top 5 most active students:\n"
        for student in students:
            response += f"- {student['name']} ({student['department']}): {student['total_borrows']} books borrowed\n"
        return response

    elif intent == "popular_books":
        books = await get_popular_books(db)
        if not books:
            return "No borrowing data available."
        response = "Top 5 most popular books:\n"
        for book in books:
            response += f"- {book['title']} by {book['author']}: borrowed {book['times_borrowed']} times\n"
        return response

    else:
        return "I'm sorry, I don't understand that question. I can help you with:\n" + \
               "- Overdue books\n" + \
               "- Department borrowing statistics\n" + \
               "- New books added\n" + \
               "- Most active students\n" + \
               "- Most popular books"

async def stream_response(response: str):
    for char in response:
        yield char
        await asyncio.sleep(0.01)  # Small delay for streaming effect

@router.post("/ask")
async def ask_question(
    question: Question,
    db: AsyncSession = Depends(get_db)
):
    intent = detect_intent(question.text)
    response = await generate_response(intent, db)
    return StreamingResponse(
        stream_response(response),
        media_type="text/plain"
    ) 