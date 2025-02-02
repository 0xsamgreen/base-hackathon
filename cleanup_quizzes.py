from sqlalchemy import create_engine, text
import os

# Get absolute path for SQLite database
db_path = os.path.abspath("base-hackathon.db")
DATABASE_URL = f"sqlite:///{db_path}"

# Create SQLite database and tables
engine = create_engine(DATABASE_URL)

def cleanup_quizzes():
    """Clean up quizzes table and insert one quiz."""
    with engine.begin() as conn:
        # Delete all existing quizzes
        conn.execute(text("DELETE FROM quizzes"))
        
        # Insert single quiz
        conn.execute(
            text("INSERT INTO quizzes (name, reward_amount) VALUES (:name, :reward)"),
            {"name": "Solar Panel Cleaning", "reward": 1.0}
        )
        print("Quiz table cleaned up and quiz re-inserted!")

if __name__ == "__main__":
    cleanup_quizzes()
