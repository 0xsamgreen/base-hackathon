# Base Hackathon Project

A Telegram bot with admin CLI for managing KYC (Know Your Customer) verifications.

## Features

- Telegram bot for collecting KYC information
- Admin CLI for managing KYC verifications
- PostgreSQL database for data storage
- Docker-based deployment

## Prerequisites

- Docker and Docker Compose
- Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))

## Setup

1. Clone the repository:
```bash
git clone git@github.com:0xsamgreen/base-hackathon.git
cd base-hackathon
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update the `.env` file with your configuration:
- Set PostgreSQL credentials
- Add your Telegram Bot Token

4. Build and start the services:
```bash
docker-compose up -d
```

## Usage

### Telegram Bot

1. Start a chat with your bot on Telegram
2. Use the `/start` command to begin KYC verification
3. Follow the prompts to submit your information:
   - Full Name
   - Birthday
   - Phone Number
   - Email
   - PIN for Wallet

### Admin CLI

The admin CLI provides tools for managing KYC verifications:

1. Access the CLI:
```bash
docker exec -it admin_cli python cli.py
```

2. Available commands:
   - Option 1: List Pending KYC - View all pending verifications
   - Option 2: Approve KYC - Select and approve pending verifications
   - Option 3: List Approved Users - View all approved users
   - Option 4: Exit

## Project Structure

```
.
├── admin/              # Admin CLI application
├── backend/           # Backend API and Telegram bot
├── db/               # Database initialization
├── docker-compose.yml
└── .env.example
```

## Development

To add new features or modify existing ones:

1. Make changes to the relevant components
2. Rebuild the affected services:
```bash
docker-compose up -d --build <service_name>
```

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- Regularly rotate the database credentials and bot token
- All sensitive user data is stored securely in the PostgreSQL database
