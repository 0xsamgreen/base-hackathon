"""Main Telegram bot module."""
import logging
import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
from ..db.session import get_db
from ..models.user import User

# Configure logging to be less verbose
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.WARNING  # Only show warnings and errors
)
logger = logging.getLogger(__name__)

# Disable polling logs from httpx
logging.getLogger("httpx").setLevel(logging.WARNING)

# Conversation states
NAME, BIRTHDAY, PHONE, EMAIL, PIN = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the KYC conversation."""
    await update.message.reply_text(
        "Welcome to the KYC verification process! 🚀\n\n"
        "Please enter your full name:"
    )
    return NAME

async def collect_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collect user's name and ask for birthday."""
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        "Thanks! Now please enter your birthday (YYYY-MM-DD):"
    )
    return BIRTHDAY

async def collect_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collect user's birthday and ask for phone."""
    context.user_data['birthday'] = update.message.text
    await update.message.reply_text(
        "Great! Now please enter your phone number:"
    )
    return PHONE

async def collect_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collect user's phone and ask for email."""
    context.user_data['phone'] = update.message.text
    await update.message.reply_text(
        "Perfect! Now please enter your email address:"
    )
    return EMAIL

async def collect_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collect user's email and ask for PIN."""
    context.user_data['email'] = update.message.text
    await update.message.reply_text(
        "Almost done! Finally, please enter a 6-digit PIN for your wallet:"
    )
    return PIN

async def collect_pin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collect user's PIN and save all data."""
    context.user_data['pin'] = update.message.text
    
    # Get database session
    db = next(get_db())
    
    try:
        # Try to get existing user or create new one
        user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
        if user:
            # Update existing user
            user.username = update.effective_user.username
            user.kyc = False  # Reset to pending approval
            user.full_name = context.user_data['name']
            user.birthday = context.user_data['birthday']
            user.phone = context.user_data['phone']
            user.email = context.user_data['email']
            user.pin = context.user_data['pin']
        else:
            # Create new user
            user = User(
                telegram_id=update.effective_user.id,
                username=update.effective_user.username,
                kyc=False,  # Pending approval
                full_name=context.user_data['name'],
                birthday=context.user_data['birthday'],
                phone=context.user_data['phone'],
                email=context.user_data['email'],
                pin=context.user_data['pin']
            )
            db.add(user)
        db.commit()
        
        await update.message.reply_text(
            "Thank you! Your KYC information has been submitted for review. "
            "You will be notified once it's approved. ✅"
        )
    except Exception as e:
        logger.error(f"Error saving user data: {e}")
        db.rollback()
        await update.message.reply_text(
            "Sorry, there was an error processing your information. "
            "Please try again later or contact support."
        )
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text(
        "KYC process cancelled. You can start again with /start"
    )
    return ConversationHandler.END

def create_application() -> Application:
    """Create and configure the bot application."""
    # Create application with custom settings
    application = Application.builder().token(
        os.getenv("TELEGRAM_BOT_TOKEN")
    ).get_updates_read_timeout(42).get_updates_write_timeout(42).build()

    # Configure error handlers
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        print(f"Exception while handling an update: {context.error}")
    
    application.add_error_handler(error_handler)

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_name)],
            BIRTHDAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_birthday)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_phone)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_email)],
            PIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_pin)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    return application

def main() -> None:
    """Start the bot."""
    app = create_application()
    app.run_polling(
        allowed_updates=["message"],
        drop_pending_updates=True,
        pool_timeout=30.0,  # Longer timeout
        read_timeout=30.0,  # Longer timeout
        connect_timeout=30.0  # Longer timeout
    )

if __name__ == "__main__":
    main()
