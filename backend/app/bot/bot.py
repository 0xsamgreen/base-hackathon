"""Main Telegram bot module."""
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
from ..db.session import get_db
from ..models.user import User
from ..config import get_settings

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

def build_menu(user: User = None) -> InlineKeyboardMarkup:
    """Build the menu keyboard based on user state."""
    buttons = []
    
    # KYC button - greyed out if already approved
    kyc_text = "Enter KYC Info"
    if user and user.kyc:
        kyc_text = "⚪️ KYC Already Approved"
    buttons.append([InlineKeyboardButton(kyc_text, 
        callback_data="kyc" if not user or not user.kyc else "unavailable")])
    
    # Wallet button - active only if KYC approved
    wallet_text = "Get Wallet Address"
    if not user or not user.kyc:
        wallet_text = "⚪️ Get Wallet Address (Complete KYC First)"
    buttons.append([InlineKeyboardButton(wallet_text, 
        callback_data="wallet" if user and user.kyc else "unavailable")])
    
    # Future features - greyed out
    buttons.extend([
        [InlineKeyboardButton("⚪️ Learn to Clean Panels and Earn (Coming Soon)", 
            callback_data="unavailable")],
        [InlineKeyboardButton("⚪️ Train our AI and Earn (Coming Soon)", 
            callback_data="unavailable")]
    ])
    
    return InlineKeyboardMarkup(buttons)

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the main menu."""
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
    
    await update.message.reply_text(
        "Welcome to Base Hackathon Bot! 🚀\n"
        "Please select an option:",
        reply_markup=build_menu(user)
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler."""
    await show_menu(update, context)
    return ConversationHandler.END

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu command handler."""
    await show_menu(update, context)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "unavailable":
        await query.answer("This feature is not available yet", show_alert=True)
        return
    
    if query.data == "kyc":
        await query.message.reply_text(
            "Starting KYC process! 🚀\n\n"
            "Please enter your full name:"
        )
        return NAME
    
    if query.data == "wallet":
        db = next(get_db())
        user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
        
        if not user:
            await query.message.reply_text("Please complete KYC first")
            return
        
        if not user.kyc:
            await query.message.reply_text("Your KYC is pending approval")
            return
        
        if not user.wallet_address:
            await query.message.reply_text("No wallet has been generated yet")
            return
        
        await query.message.reply_text(f"Your wallet address is: {user.wallet_address}")

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

import asyncio

async def notify_kyc_approved(telegram_id: int, wallet_address: str):
    """Send notification to user when KYC is approved."""
    settings = get_settings()
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("Cannot send notification: No bot token")
        return
        
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    max_retries = 3
    retry_delay = 5  # seconds
    
    try:
        for attempt in range(max_retries):
            try:
                await bot.send_message(
                    chat_id=telegram_id,
                    text=f"🎉 Congratulations! Your KYC has been approved!\n\n"
                         f"Your Base wallet address is:\n`{wallet_address}`\n\n"
                         f"Use /menu to see all available options.",
                    parse_mode='Markdown'
                )
                break
            except Exception as e:
                if "Flood control exceeded" in str(e) and attempt < max_retries - 1:
                    logger.warning(f"Rate limited, waiting {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                logger.error(f"Failed to send KYC approval notification: {e}")
                break
    finally:
        await bot.close()

def create_application() -> Application:
    """Create and configure the bot application."""
    # Create application with custom settings
    settings = get_settings()
    if not settings.TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is required for bot operation")
        
    application = Application.builder().token(
        settings.TELEGRAM_BOT_TOKEN
    ).build()

    # Configure error handlers
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.error(f"Exception while handling an update: {context.error}")
    
    application.add_error_handler(error_handler)

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(button_callback, pattern="^kyc$")
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_name)],
            BIRTHDAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_birthday)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_phone)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_email)],
            PIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_pin)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CallbackQueryHandler(button_callback))

    return application

def main() -> None:
    """Start the bot."""
    try:
        print("Creating application...")
        app = create_application()
        print("Starting bot polling...")
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"Error running bot: {e}")
        raise

if __name__ == "__main__":
    main()
