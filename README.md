# Library Management System API

A FastAPI-based backend system for managing books, students, and book insurance for a college library.

## Features

- Book Management (CRUD operations)
- Student Management
- Book Issue & Return System
- Search and Filter functionality
- Pagination support
- RESTful API design
- Async/await support
- Input validation using Pydantic
- MySQL database integration

## Tech Stack

- FastAPI
- MySQL
- SQLAlchemy (ORM)
- Pydantic
- Python 3.8+

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root directory with the following variables:
   ```
   DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/library_db
   SECRET_KEY=your-secret-key
   ```
5. Create the MySQL database:
   ```sql
   CREATE DATABASE library_db;
   ```
6. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once the application is running, you can access:
- Swagger UI documentation: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

## API Endpoints

### Books
- `GET /api/books` - List all books (with filters and pagination)
- `GET /api/books/{book_id}` - Get book details
- `POST /api/books` - Add a new book
- `PUT /api/books/{book_id}` - Update a book
- `DELETE /api/books/{book_id}` - Delete a book

### Students
- `GET /api/students` - List all students (with filters)
- `GET /api/students/{student_id}` - Get student details
- `POST /api/students` - Add a new student
- `GET /api/students/{student_id}/books` - Get books issued to a student

### Book Issues
- `POST /api/issues` - Issue a book to a student
- `PUT /api/issues/{issue_id}/return` - Return a book
- `GET /api/issues/student/{student_id}` - Get all issues for a student

## Database Schema

### Books
- id (Primary Key)
- title
- author
- isbn
- total_copies
- available_copies
- category
- created_at
- updated_at

### Students
- id (Primary Key)
- name
- roll_number
- department
- semester
- phone
- email
- created_at
- updated_at

### Book Issues
- id (Primary Key)
- book_id (Foreign Key)
- student_id (Foreign Key)
- issue_date
- return_date
- actual_return_date
- status
- created_at
- updated_at 