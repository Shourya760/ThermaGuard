"""
app/db/session.py

SQLAlchemy session configuration.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# If no DATABASE_URL is provided, default to a local SQLite database file in the backend directory.
SQLALCHEMY_DATABASE_URL = getattr(settings, "database_url", "sqlite:///./coolblock.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
