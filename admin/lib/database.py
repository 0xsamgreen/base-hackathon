from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Create database URL - use the same SQLite database as backend
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../base-hackathon.db"))
DATABASE_URL = f"sqlite:///{db_path}"

# Create SQLAlchemy engine with SQLite-specific settings
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
