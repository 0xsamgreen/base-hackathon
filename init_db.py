from sqlalchemy import create_engine, text
import os

# Get absolute path for SQLite database
db_path = os.path.abspath("base-hackathon.db")
DATABASE_URL = f"sqlite:///{db_path}"

# Create SQLite database and tables
engine = create_engine(DATABASE_URL)

# SQLite schema
schema = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    kyc BOOLEAN DEFAULT FALSE,
    wallet_address TEXT,
    private_key TEXT,
    full_name TEXT,
    birthday TEXT,
    phone TEXT,
    email TEXT,
    pin TEXT
);
"""

def init_db():
    """Initialize the SQLite database with schema."""
    with engine.begin() as conn:
        conn.execute(text(schema))
        print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
