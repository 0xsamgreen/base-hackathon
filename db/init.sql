CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR,
    kyc BOOLEAN DEFAULT FALSE,
    wallet_address VARCHAR,
    private_key TEXT,
    full_name VARCHAR,
    birthday VARCHAR,
    phone VARCHAR,
    email VARCHAR,
    pin VARCHAR
);
