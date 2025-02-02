#!/bin/bash

# Get the absolute path to the project root
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to activate virtual environment
activate_venv() {
    local service=$1
    echo "Activating $service virtual environment..."
    source "${PROJECT_ROOT}/$service/venv/bin/activate"
}

# Function to kill processes using a port
kill_port() {
    local port=$1
    local pid=$(lsof -ti :$port)
    if [ ! -z "$pid" ]; then
        echo "Killing process using port $port..."
        kill -9 $pid
        sleep 1
    fi
}

# Function to kill existing processes
kill_existing() {
    local process=$1
    local port=$2
    echo "Checking for existing $process processes..."
    
    # Only kill processes that match the exact command
    local pids=$(pgrep -f "^python.*$process$" || true)
    if [ ! -z "$pids" ]; then
        echo "Killing processes: $pids"
        for pid in $pids; do
            kill -9 $pid 2>/dev/null || true
        done
        sleep 1
    fi

    # If port is specified, ensure it's free
    if [ ! -z "$port" ]; then
        kill_port $port
    fi
}

# Function to run backend service
run_backend() {
    echo "Starting backend service..."
    kill_existing "run.py" "8000"  # FastAPI runs on port 8000
    cd "${PROJECT_ROOT}/backend"
    activate_venv backend
    python run.py
}

# Function to run admin CLI
run_admin() {
    echo "Starting admin CLI..."
    kill_existing "cli.py"  # CLI doesn't use a port
    cd "${PROJECT_ROOT}/admin"
    activate_venv admin
    PYTHONPATH="${PROJECT_ROOT}" python cli.py
}

# Function to run bot
run_bot() {
    echo "Starting Telegram bot..."
    # Kill only the bot process
    kill_existing "run_bot.py" "8443"  # Bot uses port 8443
    
    # Clean up Telegram state
    source .env
    echo "Cleaning up Telegram state..."
    WEBHOOK_RESP=$(curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/deleteWebhook?drop_pending_updates=true")
    if ! echo "$WEBHOOK_RESP" | grep -q "error_code"; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/close"
        sleep 1
    fi
    
    # Start bot in new terminal window
    cd "${PROJECT_ROOT}/backend"
    activate_venv backend
    osascript -e 'tell app "Terminal" to do script "cd \"'"${PROJECT_ROOT}"'/backend\" && source venv/bin/activate && python run_bot.py"'
}

# Function to start all services
start_all() {
    echo "Starting all services..."
    
    # Kill any existing processes
    pkill -f "python"
    sleep 2
    
    # Start backend
    echo "Starting backend..."
    osascript -e 'tell app "Terminal" to do script "cd \"'"${PROJECT_ROOT}"'\" && ./dev.sh backend"'
    sleep 2
    
    # Start bot
    echo "Starting bot..."
    osascript -e 'tell app "Terminal" to do script "cd \"'"${PROJECT_ROOT}"'/backend\" && source venv/bin/activate && python run_bot.py"'
    
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
