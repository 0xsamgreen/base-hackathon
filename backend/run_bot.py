"""Script to run the Telegram bot."""
import os
import sys
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

from app.bot.bot import main

if __name__ == "__main__":
    main()
