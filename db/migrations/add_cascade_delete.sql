-- Drop existing foreign key constraint
DROP TABLE IF EXISTS user_quiz_completions_temp;

-- Create temporary table with same structure
CREATE TABLE user_quiz_completions_temp (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    quiz_id INTEGER NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    score INTEGER NOT NULL,
    passed BOOLEAN NOT NULL,
    nft_token_id TEXT,
    nft_transaction_hash TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
);

-- Copy data from old table
INSERT INTO user_quiz_completions_temp 
SELECT * FROM user_quiz_completions;

-- Drop old table
DROP TABLE user_quiz_completions;

-- Rename temp table to original name
ALTER TABLE user_quiz_completions_temp RENAME TO user_quiz_completions;
