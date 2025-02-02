-- Drop unique constraint from user_quiz_completions
DROP INDEX IF EXISTS user_quiz_completions_user_id_quiz_id_key;
DROP INDEX IF EXISTS ix_user_quiz_completions_user_id_quiz_id;
