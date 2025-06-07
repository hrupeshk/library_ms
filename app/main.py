from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import books, students, book_issues, conversation
from .config import settings
from .database import engine, Base
from .models import book, student, book_issue

app = FastAPI(
    title="Library Management System",
    description="API for managing a library system with books, students, and book issues",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(books.router, prefix="/api/v1/books", tags=["books"])
app.include_router(students.router, prefix="/api/v1/students", tags=["students"])
app.include_router(book_issues.router, prefix="/api/v1/issues", tags=["book_issues"])
app.include_router(conversation.router, prefix="/api/v1/chat", tags=["conversation"])

@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Welcome to the Library Management System API"} 