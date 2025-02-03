-- Drop existing table
DROP TABLE IF EXISTS user_quiz_completions;

-- Create table with new structure
CREATE TABLE user_quiz_completions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    quiz_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    score INTEGER NOT NULL,
    passed BOOLEAN NOT NULL,
    nft_token_id TEXT,
    nft_transaction_hash TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
);
