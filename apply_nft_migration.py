from sqlalchemy import create_engine, text
import os

# Get absolute path for SQLite database
db_path = os.path.abspath("base-hackathon.db")
DATABASE_URL = f"sqlite:///{db_path}"

# Create SQLite database engine
engine = create_engine(DATABASE_URL)

def apply_migration():
    """Create NFT metadata tables."""
    with engine.begin() as conn:
        # Create NFT metadata table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS nft_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                image_url TEXT NOT NULL,
                attributes TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
            )
        """))
        
        # Add NFT address column to user_quiz_completions
        conn.execute(text("""
            ALTER TABLE user_quiz_completions 
            ADD COLUMN nft_address TEXT
        """))
        
        print("Successfully created NFT metadata tables!")

if __name__ == "__main__":
    apply_migration()
