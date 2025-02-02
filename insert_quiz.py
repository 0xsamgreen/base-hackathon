from sqlalchemy import create_engine, text
import os

# Get absolute path for SQLite database
db_path = os.path.abspath("base-hackathon.db")
DATABASE_URL = f"sqlite:///{db_path}"

# Create SQLite database and tables
engine = create_engine(DATABASE_URL)

def insert_quiz():
    """Insert the solar panel cleaning quiz."""
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO quizzes (name, reward_amount, eth_reward_amount) VALUES (:name, :reward, :eth_reward)"),
            {"name": "Solar Panel Cleaning", "reward": "1.0", "eth_reward": "0.00001"}
        )
        print("Quiz inserted successfully!")

if __name__ == "__main__":
    insert_quiz()
