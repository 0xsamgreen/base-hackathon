import sqlite3
import os

def apply_migration():
    """Apply the completion timestamp fix migration."""
    # Get absolute path for SQLite database
    db_path = os.path.abspath("base-hackathon.db")
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Read and execute migration
        with open("db/migrations/fix_completion_timestamp.sql", "r") as f:
            migration = f.read()
            cursor.executescript(migration)
        
        conn.commit()
        print("Migration applied successfully!")
        
    except Exception as e:
        print(f"Error applying migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    apply_migration()
