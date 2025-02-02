-- Add eth_reward_amount column to quizzes table
ALTER TABLE quizzes ADD COLUMN eth_reward_amount VARCHAR(255) NOT NULL DEFAULT '0.00001';
