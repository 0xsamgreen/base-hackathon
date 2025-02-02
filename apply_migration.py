from sqlalchemy import create_engine, text
import os

# Get absolute path for SQLite database
db_path = os.path.abspath("base-hackathon.db")
DATABASE_URL = f"sqlite:///{db_path}"

# Create SQLite database engine
engine = create_engine(DATABASE_URL)

def apply_migration():
    """Remove pin column from users table."""
    with engine.begin() as conn:
        # SQLite doesn't support DROP COLUMN directly, so we need to:
        # 1. Create a new table without the pin column
        # 2. Copy data from old table
        # 3. Drop old table
        # 4. Rename new table
        
        conn.execute(text("""
            CREATE TABLE users_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                kyc BOOLEAN DEFAULT FALSE,
                wallet_address TEXT,
                private_key TEXT,
                full_name TEXT,
                birthday TEXT,
                phone TEXT,
                email TEXT
            )
        """))
        
        conn.execute(text("""
            INSERT INTO users_new 
            SELECT id, telegram_id, username, kyc, wallet_address, private_key, 
                   full_name, birthday, phone, email
            FROM users
        """))
        
        conn.execute(text("DROP TABLE users"))
        conn.execute(text("ALTER TABLE users_new RENAME TO users"))
        
        print("Successfully removed pin column from users table!")

if __name__ == "__main__":
    apply_migration()
