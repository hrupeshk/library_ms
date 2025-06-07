from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+aiomysql://root:password@localhost:3306/library_db")
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Library Management System"
    
    class Config:
        case_sensitive = True

settings = Settings() 