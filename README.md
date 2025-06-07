# Library Management System

Hey there! 👋 This is my implementation of a Library Management System using FastAPI and MySQL. I built this as a fun project to explore modern web development practices.

## What's Inside?

- 📚 Book management (add, update, delete, search)
- 👥 Student management
- 📖 Book issue tracking
- 🤖 Cool chat interface for library stats
- ⚡ Async operations for better performance

## Tech Stack

- FastAPI (because it's fast and modern!)
- SQLAlchemy (for database operations)
- MySQL (my favorite database)
- Pydantic (for data validation)
- Uvicorn (ASGI server)

## Getting Started

1. First, clone this repo:
```bash
git clone <your-repo-url>
```

2. Set up your virtual environment (I use Python 3.12):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the requirements:
```bash
pip install -r requirements.txt
```

4. Create a MySQL database named `library_db`

5. Update the database connection in `app/config.py` with your credentials

6. Run the database migrations:
```bash
python seed_db.py
```

7. Start the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Books
- GET `/api/v1/books` - List all books
- POST `/api/v1/books` - Add a new book
- GET `/api/v1/books/{id}` - Get book details
- PUT `/api/v1/books/{id}` - Update a book
- DELETE `/api/v1/books/{id}` - Delete a book

### Students
- GET `/api/v1/students` - List all students
- POST `/api/v1/students` - Add a new student
- GET `/api/v1/students/{id}` - Get student details
- PUT `/api/v1/students/{id}` - Update a student
- DELETE `/api/v1/students/{id}` - Delete a student

### Book Issues
- GET `/api/v1/issues` - List all book issues
- POST `/api/v1/issues` - Issue a book
- PUT `/api/v1/issues/{id}/return` - Return a book
- GET `/api/v1/issues/student/{id}/overdue` - Get overdue books for a student

### Chat Interface
- POST `/api/v1/chat/ask` - Ask questions about library stats

Example chat questions:
- "How many books are overdue?"
- "Which department borrowed the most books?"
- "Show me the most popular books"
- "Who are the most active students?"



## My Development Notes

I chose FastAPI because it's modern, fast, and has great async support. The chat interface was particularly fun to implement - I used a simple intent-to-query mapping system that could be extended with more sophisticated NLP in the future.

The database schema is designed to be scalable and maintainable. I used SQLAlchemy's async features to ensure good performance even with many concurrent users.

