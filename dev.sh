#!/bin/bash

# Get the absolute path to the project root
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to activate virtual environment
activate_venv() {
    local service=$1
    echo "Activating $service virtual environment..."
    source "${PROJECT_ROOT}/$service/venv/bin/activate"
}

# Function to clean up port processes
cleanup_port() {
    local port=$1
    echo "Cleaning up port $port..."
    
    if lsof -ti :$port > /dev/null 2>&1; then
        echo "Killing process on port $port..."
        lsof -ti :$port | xargs kill -9
        sleep 1
    fi
    
    while lsof -ti :$port > /dev/null 2>&1; do
        echo "Waiting for port $port to be free..."
        sleep 1
    done
}

# Function to clean up processes
cleanup_processes() {
    echo "Cleaning up processes..."
    cleanup_port 8000  # Only clean up the backend API port
    echo "Cleanup complete"
}

# Function to run backend service
run_backend() {
    echo "Starting backend service..."
    cleanup_processes
    cd "${PROJECT_ROOT}/backend"
    activate_venv backend
    PYTHONPATH="${PROJECT_ROOT}" python run.py
}

# Function to run admin CLI
run_admin() {
    echo "Starting admin CLI..."
    cd "${PROJECT_ROOT}/admin"
    activate_venv admin
    PYTHONPATH="${PROJECT_ROOT}" python cli.py
}

# Function to run bot
run_bot() {
    echo "Starting Telegram bot..."
    
    # Clean up Telegram state
    source .env
    echo "Cleaning up Telegram state..."
    WEBHOOK_RESP=$(curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/deleteWebhook?drop_pending_updates=true")
    if ! echo "$WEBHOOK_RESP" | grep -q "error_code"; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/close"
        sleep 1
    fi
    
    # Start bot in current terminal
    cd "${PROJECT_ROOT}/backend"
    activate_venv backend
    PYTHONPATH="${PROJECT_ROOT}" python run_bot.py
}

# Function to start all services
start_all() {
    echo "Starting all services..."
    
    # Clean up any existing processes
    cleanup_processes
    
    # Start backend in foreground
    echo "Starting backend..."
    cd "${PROJECT_ROOT}/backend"
    activate_venv backend
    PYTHONPATH="${PROJECT_ROOT}" python run.py
    
    echo "All services started!"
    echo "Use './dev.sh admin' to run admin CLI when needed"
}

# Help message
show_help() {
    echo "Usage: ./dev.sh [command]"
    echo "Commands:"
    echo "  start    - Start all services (backend + bot)"
    echo "  backend  - Run the backend service"
    echo "  admin    - Run the admin CLI"
    echo "  bot      - Run the Telegram bot"
    echo "  help     - Show this help message"
}

# Main script
case "$1" in
    "start")
        start_all
        ;;
    "backend")
        run_backend
        ;;
    "admin")
        run_admin
        ;;
    "bot")
        run_bot
        ;;
    "help"|"")
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
