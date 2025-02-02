-- Create temporary table with new schema
CREATE TABLE quizzes_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,
    reward_amount VARCHAR NOT NULL,
    eth_reward_amount VARCHAR NOT NULL DEFAULT '0.00001'
);

-- Copy data from old table to new table, converting reward_amount to string
INSERT INTO quizzes_new (id, name, reward_amount, eth_reward_amount)
SELECT id, name, CAST(reward_amount AS TEXT), eth_reward_amount
FROM quizzes;

-- Drop old table
DROP TABLE quizzes;

-- Rename new table to original name
ALTER TABLE quizzes_new RENAME TO quizzes;
