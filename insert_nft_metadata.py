import sqlite3
import os

def insert_nft_metadata():
    """Insert NFT metadata for the solar panel cleaning quiz."""
    # Get absolute path for SQLite database
    db_path = os.path.abspath("base-hackathon.db")
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get quiz ID
        cursor.execute("""
            SELECT id FROM quizzes 
            WHERE name = 'Solar Panel Cleaning'
        """)
        quiz_id = cursor.fetchone()[0]
        
        # Insert NFT metadata
        cursor.execute("""
            INSERT INTO nft_metadata (
                quiz_id, name, description, image_url, attributes
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            quiz_id,
            "Solar Panel Cleaning Expert",
            "Awarded for mastering solar panel cleaning safety and best practices",
            "https://example.com/solar-badge.png",  # Replace with actual image URL
            '{"skill_level": "Expert", "category": "Solar Maintenance", "score": "100%"}'
        ))
        
        conn.commit()
        print("NFT metadata inserted successfully!")
        
    except Exception as e:
        print(f"Error inserting NFT metadata: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    insert_nft_metadata()
