CREATE TABLE IF NOT EXISTS nft_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    image_url TEXT NOT NULL,
    attributes TEXT NOT NULL,  -- JSON string of additional attributes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
);

-- Add NFT address column to user_quiz_completions
ALTER TABLE user_quiz_completions ADD COLUMN nft_address TEXT;
