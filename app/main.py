from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import books, students, book_issues
from .config import settings
from .database import engine, Base
from .models import book, student, book_issue

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
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
app.include_router(books.router, prefix=settings.API_V1_STR)
app.include_router(students.router, prefix=settings.API_V1_STR)
app.include_router(book_issues.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Library Management System API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    } 