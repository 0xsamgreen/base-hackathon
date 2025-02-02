from sqlalchemy import create_engine, text
import os

# Get absolute path for SQLite database
db_path = os.path.abspath("base-hackathon.db")
DATABASE_URL = f"sqlite:///{db_path}"

# Create SQLite database and tables
engine = create_engine(DATABASE_URL)

# SQLite schemas
schemas = [
    """
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
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        reward_amount DECIMAL(10,2) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS user_quiz_completions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        quiz_id INTEGER NOT NULL,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        score INTEGER NOT NULL,
        passed BOOLEAN NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id),
        UNIQUE(user_id, quiz_id)
    )
    """
]

def init_db():
    """Initialize the SQLite database with schema."""
    with engine.begin() as conn:
        for schema in schemas:
            conn.execute(text(schema))
        
        # Insert the solar panel cleaning quiz
        conn.execute(
            text("INSERT OR IGNORE INTO quizzes (name, reward_amount) VALUES (:name, :reward)"),
            {"name": "Solar Panel Cleaning", "reward": 1.0}
        )
        print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
