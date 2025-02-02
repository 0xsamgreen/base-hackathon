from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# Get absolute path for SQLite database
db_path = os.path.abspath("base-hackathon.db")
DATABASE_URL = f"sqlite:///{db_path}"

# Create SQLite database and tables
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def check_db():
    """Check database tables."""
    with Session() as session:
        # Check tables
        result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        print("\nTables in database:")
        for row in result:
            print(f"- {row[0]}")
            
        # Check quizzes
        result = session.execute(text("SELECT * FROM quizzes;"))
        print("\nQuizzes in database:")
        for row in result:
            print(f"ID: {row[0]}, Name: {row[1]}, Reward: {row[2]}")

if __name__ == "__main__":
    check_db()
