import sqlite3
import os

def cleanup_quizzes():
    """Clean up duplicate quizzes."""
    # Get absolute path for SQLite database
    db_path = os.path.abspath("base-hackathon.db")
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all quiz IDs for Solar Panel Cleaning, ordered by ID
        cursor.execute("""
            SELECT id FROM quizzes 
            WHERE name = 'Solar Panel Cleaning' 
            ORDER BY id
        """)
        quiz_ids = [row[0] for row in cursor.fetchall()]
        
        if len(quiz_ids) > 1:
            # Keep the first one, delete the rest
            keep_id = quiz_ids[0]
            delete_ids = quiz_ids[1:]
            
            # Delete duplicate quizzes
            cursor.execute("""
                DELETE FROM quizzes 
                WHERE id IN ({})
            """.format(','.join('?' * len(delete_ids))), delete_ids)
            
            # Delete associated NFT metadata
            cursor.execute("""
                DELETE FROM nft_metadata 
                WHERE quiz_id IN ({})
            """.format(','.join('?' * len(delete_ids))), delete_ids)
            
            # Update any quiz completions to point to the kept quiz
            cursor.execute("""
                UPDATE user_quiz_completions 
                SET quiz_id = ? 
                WHERE quiz_id IN ({})
            """.format(','.join('?' * len(delete_ids))), [keep_id] + delete_ids)
            
            conn.commit()
            print(f"Cleaned up {len(delete_ids)} duplicate quizzes")
        else:
            print("No duplicates found")
        
    except Exception as e:
        print(f"Error cleaning up quizzes: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup_quizzes()
