# Base Hackathon Project

A Telegram bot-based KYC system with wallet generation for Base blockchain. The system consists of three main components:

## Quick Start

```bash
# Clone and setup
git clone git@github.com:0xsamgreen/base-hackathon.git
cd base-hackathon
cp .env.example .env  # Add your Telegram bot token

# Install dependencies

## Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Node.js dependencies (important for wallet generation)
npm install
# If you encounter wallet generation errors, try:
rm -rf node_modules && npm install

## Admin setup
cd ../admin
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# Initialize database
python init_db.py

# Start services (in separate terminals)

## Terminal 1 - Start backend API
./dev.sh start

## Terminal 2 - Start Telegram bot
./dev.sh bot

## Terminal 3 - Run admin interface
./dev.sh admin

# Test it out
1. Message @basehackathon on Telegram
2. Send /start command to begin KYC process
3. Complete KYC form
4. Use admin CLI to approve and generate wallet
```

## Running the Services

Each service runs independently in its own terminal:

1. **Backend API** (`./dev.sh start`)
   - Handles API requests and wallet generation
   - Runs on http://0.0.0.0:8000
   - Must be started first

2. **Telegram Bot** (`./dev.sh bot`)
   - Handles user interactions
   - Collects KYC information
   - Notifies users of approval status

3. **Admin CLI** (`./dev.sh admin`)
   - Reviews pending KYC requests
   - Approves users
   - Triggers wallet generation
   - Shows generated wallet addresses

The services are designed to run independently, so you can:
- Restart the backend without affecting the bot or admin CLI
- Keep the admin CLI running while restarting other services
- Start/stop services as needed without impacting others

The system consists of three main components:

1. Telegram Bot - Handles user KYC data collection
2. Admin CLI - For KYC approval and user management
3. Backend API - Manages data and wallet operations

## Project Goals

- Provide a seamless KYC process through Telegram
- Generate Base blockchain wallets for approved users (using viem)
- Maintain secure user data handling
- Enable admin oversight of KYC process

## Dependencies

- Python 3.x with venv module
- Node.js (for wallet generation using viem)
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

### Components

- **Telegram Bot** (`backend/app/bot/`):
  - Collects user KYC information
  - Handles user interactions
  - Notifies users of KYC status

- **Backend API** (`backend/app/`):
  - FastAPI-based REST API
  - Manages user data and KYC status
  - Handles wallet generation using viem
  - SQLite database integration

- **Admin CLI** (`admin/`):
  - Reviews pending KYC requests
  - Approves/manages users
  - Monitors system status

## Setup

1. Clone the repository:
   ```bash
   git clone git@github.com:0xsamgreen/base-hackathon.git
   cd base-hackathon
   ```

2. Create Python virtual environments:
   ```bash
   # Backend venv
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   deactivate

   # Admin venv
   cd ../admin
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   deactivate
   cd ..
   ```

3. Install Node.js dependencies:
   ```bash
   cd backend
   npm install
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit .env and add:
   - `TELEGRAM_BOT_TOKEN` - Your Telegram bot token

## Running the System

Start all services with a single command:
```bash
./dev.sh start
```

This will:
- Start the backend API (new terminal window)
- Start the Telegram bot (new terminal window)
- Initialize the database if needed

To use the admin interface:
```bash
./dev.sh admin
```

## Development Commands

- `./dev.sh start` - Start all services
- `./dev.sh backend` - Run only the backend API
- `./dev.sh bot` - Run only the Telegram bot
- `./dev.sh admin` - Launch the admin CLI

## User Flow

1. User starts KYC:
   - Message @basehackathon on Telegram
   - Send /start command
   - Follow prompts to enter:
     * Full name
     * Birthday
     * Phone number
     * Email
     * PIN for wallet

2. Admin approval:
   - Admin reviews KYC in admin CLI
   - Upon approval, system generates Base wallet
   - User receives notification via Telegram

## Technical Details

- **Database**: SQLite (file: base-hackathon.db)
- **API**: FastAPI on port 8000
- **Wallet Generation**: viem (TypeScript)
- **Network**: Base Sepolia testnet

## Troubleshooting

### Wallet Generation Issues
If you encounter errors during wallet generation (usually during KYC approval):
1. Ensure Node.js dependencies are properly installed:
   ```bash
   cd backend
   rm -rf node_modules
   npm install
   ```
2. Restart the backend server:
   ```bash
   ./dev.sh start
   ```

### Common Issues
- If the backend fails to start, ensure no other process is using port 8000
- If wallet generation fails, try reinstalling Node.js dependencies as described above
- For database issues, you can reinitialize it using `python init_db.py`

## Project Structure

```
.
├── admin/              # Admin CLI tool
├── backend/
│   ├── app/
│   │   ├── api/       # REST API endpoints
│   │   ├── bot/       # Telegram bot
│   │   ├── db/        # Database
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   └── services/  # Business logic
│   └── requirements.txt
└── dev.sh             # Development utilities
```

## Contributing

1. Keep services modular and independent
2. Follow existing patterns for new features
3. Update documentation for significant changes

## Current Status

✅ Working Features:
- Telegram bot KYC data collection
- SQLite database integration
- Admin CLI for KYC approval
- Base Sepolia wallet generation
- Process management with dev.sh

🚧 In Development:
- Error handling improvements
- Rate limit handling for Telegram
- Process cleanup refinements

## Future Improvements

- [ ] Enhanced error handling and validation
- [ ] User dashboard/web interface
- [ ] Additional KYC verification methods
- [ ] Transaction monitoring
- [ ] Multi-admin support
- [ ] Automated testing
- [ ] CI/CD pipeline
