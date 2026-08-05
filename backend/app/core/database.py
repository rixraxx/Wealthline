from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

# Create SQLAlchemy engine using SQLALCHEMY_DATABASE_URI
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,  # Automatically check connection health
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base class for all ORM models
class Base(DeclarativeBase):
    pass


# FastAPI Dependency Injection for database sessions
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()