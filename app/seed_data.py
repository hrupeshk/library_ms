from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from .database import async_session
from .models.book import Book
from .models.student import Student
from .models.book_issue import BookIssue, IssueStatus

# Sample books data
books_data = [
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "isbn": "9780743273565",
        "total_copies": 5,
        "available_copies": 5,
        "category": "Fiction"
    },
    {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "isbn": "9780446310789",
        "total_copies": 3,
        "available_copies": 3,
        "category": "Fiction"
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "isbn": "9780451524935",
        "total_copies": 4,
        "available_copies": 4,
        "category": "Science Fiction"
    },
    {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "isbn": "9780547928227",
        "total_copies": 6,
        "available_copies": 6,
        "category": "Fantasy"
    },
    {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "isbn": "9780141439518",
        "total_copies": 3,
        "available_copies": 3,
        "category": "Romance"
    },
    {
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "isbn": "9780316769488",
        "total_copies": 4,
        "available_copies": 4,
        "category": "Fiction"
    },
    {
        "title": "Lord of the Flies",
        "author": "William Golding",
        "isbn": "9780399501487",
        "total_copies": 5,
        "available_copies": 5,
        "category": "Fiction"
    },
    {
        "title": "The Alchemist",
        "author": "Paulo Coelho",
        "isbn": "9780062315007",
        "total_copies": 3,
        "available_copies": 3,
        "category": "Fiction"
    }
]

# Sample students data
students_data = [
    {
        "name": "John Smith",
        "roll_number": "CS2024001",
        "department": "Computer Science",
        "semester": 4,
        "phone": "1234567890",
        "email": "john.smith@example.com"
    },
    {
        "name": "Emma Johnson",
        "roll_number": "CS2024002",
        "department": "Computer Science",
        "semester": 4,
        "phone": "2345678901",
        "email": "emma.j@example.com"
    },
    {
        "name": "Michael Brown",
        "roll_number": "EE2024001",
        "department": "Electrical Engineering",
        "semester": 6,
        "phone": "3456789012",
        "email": "michael.b@example.com"
    },
    {
        "name": "Sarah Davis",
        "roll_number": "ME2024001",
        "department": "Mechanical Engineering",
        "semester": 2,
        "phone": "4567890123",
        "email": "sarah.d@example.com"
    },
    {
        "name": "David Wilson",
        "roll_number": "CS2024003",
        "department": "Computer Science",
        "semester": 4,
        "phone": "5678901234",
        "email": "david.w@example.com"
    }
]

async def seed_database():
    async with async_session() as session:
        # Clear existing data
        await session.execute(delete(BookIssue))
        await session.execute(delete(Book))
        await session.execute(delete(Student))
        await session.commit()

        # Add books
        for book_data in books_data:
            book = Book(**book_data)
            session.add(book)
        await session.commit()

        # Add students
        for student_data in students_data:
            student = Student(**student_data)
            session.add(student)
        await session.commit()

        # Get all books and students
        result = await session.execute(select(Book))
        books = result.scalars().all()
        result = await session.execute(select(Student))
        students = result.scalars().all()

        # Create overdue issues for student ID 1
        student = students[0]  # This is student ID 1
        for i in range(2):
            book = books[i]
            issue = BookIssue(
                book_id=book.id,
                student_id=student.id,
                issue_date=datetime.now() - timedelta(days=20),
                return_date=datetime.now() - timedelta(days=5),  # 5 days overdue
                status=IssueStatus.ISSUED
            )
            book.available_copies -= 1
            session.add(issue)

        await session.commit()

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_database()) 