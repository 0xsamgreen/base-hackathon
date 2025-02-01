CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username TEXT,
    kyc BOOLEAN DEFAULT FALSE,
    wallet_address TEXT,
    full_name TEXT,
    birthday TEXT,
    phone TEXT,
    email TEXT,
    pin TEXT
);
