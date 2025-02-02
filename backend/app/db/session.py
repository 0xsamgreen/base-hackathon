from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

from ..config import get_settings

settings = get_settings()

# Ensure SQLite file is created in the correct directory
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../base-hackathon.db"))
DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Needed for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
