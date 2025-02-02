# Base Hackathon Project

A Telegram bot-based KYC system with wallet generation for Base blockchain. Users can complete KYC, receive a Base wallet, take educational quizzes, and earn ETH rewards.

## Quick Start

```bash
# Setup
git clone git@github.com:0xsamgreen/base-hackathon.git
cd base-hackathon
cp .env.example .env  # Add your Telegram bot token

# Install dependencies
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
npm install

cd ../admin
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Initialize database
python init_db.py

# Start services (in separate terminals)
./dev.sh start  # Backend API
./dev.sh bot    # Telegram bot
./dev.sh admin  # Admin interface
```

## Features

- **KYC System**
  - Simple user information collection via Telegram
    - Full name
    - Birthday
    - Phone number
    - Email address
  - Admin review and approval
  - Automatic Base wallet generation

- **Quiz System**
  - Educational content about solar panel cleaning
  - Multiple choice questions
  - Automatic ETH rewards for passing

- **Wallet Features**
  - Base Sepolia testnet integration
  - View wallet address and ETH balance
  - Send/receive ETH
  - Backend wallet for reward distribution

## Dependencies

- Python 3.x
- Node.js
- SQLite3

## System Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Telegram Bot│────▶│ Backend API  │◀────│  Admin CLI  │
└─────────────┘     └──────────────┘     └─────────────┘
                          │
                    ┌─────▼─────┐
                    │  SQLite   │
                    │ Database  │
                    └───────────┘
```

## User Flow

1. Start bot (@basehackathon)
2. Complete KYC process
3. Admin approves & wallet generated
4. Access features:
   - View wallet address and balance
   - Take quiz to earn ETH
   - Send ETH to other users

## Development Commands

- `./dev.sh start` - Start all services
- `./dev.sh backend` - Run backend API
- `./dev.sh bot` - Run Telegram bot
- `./dev.sh admin` - Launch admin CLI

## Project Structure

```
.
├── admin/              # Admin CLI tool
├── backend/
│   ├── app/
│   │   ├── api/       # REST API endpoints
│   │   ├── bot/       # Telegram bot
│   │   ├── models/    # Database models
│   │   └── services/  # Business logic
│   └── requirements.txt
└── db/                # Database migrations
```

## Current Status

✅ Working Features:
- Streamlined KYC system with admin approval
- Base wallet generation and balance tracking
- Educational quiz with ETH rewards
- Direct ETH transfers with improved user selection
- Admin management tools with enhanced user info display

🚧 Coming Soon:
- AI training opportunity
- Additional quiz topics
