import time
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from .session import SessionLocal


def check_db_connected() -> bool:
    """Check if the database is accepting connections."""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        return True
    except OperationalError:
        return False
    finally:
        db.close()


def wait_for_db(retries: int = 30, delay: int = 1) -> None:
    """Wait for database to become available."""
    for _ in range(retries):
        if check_db_connected():
            return
        time.sleep(delay)
    raise Exception("Database connection failed after multiple retries")
