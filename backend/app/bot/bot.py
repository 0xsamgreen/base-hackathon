"""Main Telegram bot module."""
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
import asyncio
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
from ..models.quiz import Quiz, UserQuizCompletion
from ..services.backend_wallet import BackendWalletService
from ..config import get_settings

# Configure logging to be less verbose
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO  # Show info, warnings, and errors
)
logger = logging.getLogger(__name__)

# Disable polling logs from httpx
logging.getLogger("httpx").setLevel(logging.WARNING)

# Conversation states
NAME, BIRTHDAY, PHONE, EMAIL, PIN = range(5)
QUIZ_START, QUIZ_Q1, QUIZ_Q2, QUIZ_Q3 = range(5, 9)

# Quiz content
TRAINING_TEXT = """🌞 Solar Panel Cleaning Guide

Safety First:
• Turn off your solar panel system
• Stay on the ground - use long-handled tools
• Work in early morning or late afternoon

Cleaning Steps:
1. Mix mild soap with water (or use soap-free brushes)
2. Use soft-bristle brush with long handle
3. Gently clean panel surface
4. Rinse with gentle spray

❌ Never Use:
• Harsh chemicals
• Pressure washers
• Abrasive tools

❄️ For Snow:
• Use soft roof rake with plastic blade
• Start from lower edge
• When in doubt, let nature do the work
"""

QUIZ_QUESTIONS = [
    {
        "question": "When is the best time to clean solar panels?",
        "options": [
            "During the hottest part of the day",
            "Early morning or late afternoon",
            "Right after it rains"
        ],
        "correct": 1
    },
    {
        "question": "What should you avoid using when cleaning solar panels?",
        "options": [
            "Soft-bristle brush",
            "Mild, biodegradable soap",
            "Pressure washer"
        ],
        "correct": 2
    },
    {
        "question": "How should you remove snow from solar panels?",
        "options": [
            "Use a soft roof rake with a plastic blade",
            "Pour hot water over the panels",
            "Scrape with a metal shovel"
        ],
        "correct": 0
    }
]

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
    
    # Quiz feature - active if KYC approved
    quiz_text = "Learn to Clean Panels and Earn"
    if not user or not user.kyc:
        quiz_text = "⚪️ Learn to Clean Panels and Earn (Complete KYC First)"
    buttons.append([InlineKeyboardButton(quiz_text,
        callback_data="quiz" if user and user.kyc else "unavailable")])
    
    # Future feature - greyed out
    buttons.append([InlineKeyboardButton("⚪️ Train our AI and Earn (Coming Soon)", 
        callback_data="unavailable")])
    
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
    logger.info(f"Received callback data: {query.data}")
    logger.info(f"Current conversation state: {context.user_data.get('state', 'None')}")
    await query.answer()
    
    if query.data == "unavailable":
        logger.info("User clicked unavailable feature")
        await query.answer("This feature is not available yet", show_alert=True)
        return
    
    if query.data == "kyc":
        await query.message.reply_text(
            "Starting KYC process! 🚀\n\n"
            "Please enter your full name:"
        )
        return NAME
    
    if query.data == "quiz":
        logger.info(f"User {update.effective_user.id} starting quiz flow")
        db = next(get_db())
        user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
        logger.info(f"Found user: {user.id} (Telegram ID: {user.telegram_id})")
        
        # Check if user has already passed the quiz
        quiz = db.query(Quiz).filter(Quiz.name == "Solar Panel Cleaning").first()
        logger.info(f"Found quiz: {quiz.id} - {quiz.name}")
        
        passed_quiz = db.query(UserQuizCompletion).filter(
            UserQuizCompletion.user_id == user.id,
            UserQuizCompletion.quiz_id == quiz.id,
            UserQuizCompletion.passed == True
        ).first()
        logger.info(f"Previous passed quiz completion: {passed_quiz is not None}")
        
        if passed_quiz:
            await query.message.reply_text(
                "You've already passed this quiz and received your reward! 🎉"
            )
            return
        
        # Show training text
        quiz = db.query(Quiz).filter(Quiz.name == "Solar Panel Cleaning").first()
        await query.message.reply_text(
            f"Let's learn about solar panel cleaning! 📚\n\n{TRAINING_TEXT}\n\n"
            f"Ready to test your knowledge? Complete the quiz correctly to earn {quiz.eth_reward_amount} ETH (≈ $0.02)!\n\n"
            f"Would you like to start the quiz?",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Yes", callback_data="quiz_start"),
                    InlineKeyboardButton("No", callback_data="quiz_cancel")
                ]
            ])
        )
        logger.info(f"Transitioning to QUIZ_START state for user {update.effective_user.id}")
        return QUIZ_START
        
    elif query.data == "quiz_start":
        logger.info(f"User {update.effective_user.id} starting quiz questions")
        context.user_data['quiz_score'] = 0
        logger.info("Quiz score initialized to 0")
        await query.message.reply_text(
            f"Question 1: {QUIZ_QUESTIONS[0]['question']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(opt, callback_data=f"q1_{i}")]
                for i, opt in enumerate(QUIZ_QUESTIONS[0]['options'])
            ])
        )
        logger.info(f"Transitioning to QUIZ_Q1 state for user {update.effective_user.id}")
        return QUIZ_Q1
        
    elif query.data.startswith("q1_"):
        selected = int(query.data.split("_")[1])
        logger.info(f"User {update.effective_user.id} answered Q1: selected={selected}, correct={QUIZ_QUESTIONS[0]['correct']}")
        context.user_data['quiz_score'] = 0  # Reset score at start
        if selected == QUIZ_QUESTIONS[0]['correct']:
            context.user_data['quiz_score'] += 1
            logger.info(f"Q1 correct, score now: {context.user_data['quiz_score']}")
        else:
            logger.info("Q1 incorrect")
        
        await query.message.reply_text(
            f"Question 2: {QUIZ_QUESTIONS[1]['question']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(opt, callback_data=f"q2_{i}")]
                for i, opt in enumerate(QUIZ_QUESTIONS[1]['options'])
            ])
        )
        logger.info(f"Transitioning to QUIZ_Q2 state for user {update.effective_user.id}")
        return QUIZ_Q2
        
    elif query.data.startswith("q2_"):
        selected = int(query.data.split("_")[1])
        logger.info(f"User {update.effective_user.id} answered Q2: selected={selected}, correct={QUIZ_QUESTIONS[1]['correct']}")
        if selected == QUIZ_QUESTIONS[1]['correct']:
            context.user_data['quiz_score'] += 1
            logger.info(f"Q2 correct, score now: {context.user_data['quiz_score']}")
        else:
            logger.info("Q2 incorrect")
        
        await query.message.reply_text(
            f"Question 3: {QUIZ_QUESTIONS[2]['question']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(opt, callback_data=f"q3_{i}")]
                for i, opt in enumerate(QUIZ_QUESTIONS[2]['options'])
            ])
        )
        logger.info(f"Transitioning to QUIZ_Q3 state for user {update.effective_user.id}")
        return QUIZ_Q3
        
    elif query.data.startswith("q3_"):
        selected = int(query.data.split("_")[1])
        logger.info(f"User {update.effective_user.id} answered Q3: selected={selected}, correct={QUIZ_QUESTIONS[2]['correct']}")
        if selected == QUIZ_QUESTIONS[2]['correct']:
            context.user_data['quiz_score'] += 1
            logger.info(f"Q3 correct, score now: {context.user_data['quiz_score']}")
        else:
            logger.info("Q3 incorrect")
        
        score = context.user_data.get('quiz_score', 0)
        passed = score == 3
        logger.info(f"Quiz completed - Final score: {score}, Passed: {passed}")
        
        # Only save completion record if they passed
        if passed:
            db = next(get_db())
            user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
            logger.info(f"Retrieved user for completion: {user.id}")
            quiz = db.query(Quiz).filter(Quiz.name == "Solar Panel Cleaning").first()
            logger.info(f"Retrieved quiz for completion: {quiz.id}")
            
            completion = UserQuizCompletion(
                user_id=user.id,
                quiz_id=quiz.id,
                score=score,
                passed=passed
            )
            logger.info(f"Created completion record: user_id={user.id}, quiz_id={quiz.id}, score={score}, passed={passed}")
            
            try:
                db.add(completion)
                db.commit()
                logger.info("Successfully saved quiz completion")
            except Exception as e:
                logger.error(f"Error saving quiz completion: {e}")
                db.rollback()
                raise
        
        if passed:
            # Send ETH reward
            try:
                wallet_service = BackendWalletService()
                wallet_info = wallet_service.get_wallet_info()
                logger.info(f"Retrieved backend wallet info: {wallet_info['address']}")
                
                logger.info(f"Sending {quiz.eth_reward_amount} ETH to {user.wallet_address}")
                tx_hash = await wallet_service.sendTransaction(
                    wallet_info['private_key'],
                    user.wallet_address,
                    quiz.eth_reward_amount
                )
                logger.info(f"ETH reward sent successfully, tx_hash: {tx_hash}")

                await query.message.reply_text(
                    "🎉 Congratulations! You got all questions correct!\n\n"
                    f"Your reward of {quiz.eth_reward_amount} ETH (≈ $0.02) has been sent!\n\n"
                    f"View transaction: https://sepolia.basescan.org/tx/{tx_hash}"
                )
            except Exception as e:
                logger.error(f"Error sending ETH reward: {e}")
                await query.message.reply_text(
                    "🎉 Congratulations! You got all questions correct!\n\n"
                    "There was an issue sending your ETH reward. Please contact support."
                )
        else:
            await query.message.reply_text(
                f"You got {score}/3 questions correct. You need all correct answers to earn the reward.\n"
                "Feel free to try again after reviewing the training material!"
            )
        
        logger.info(f"Ending conversation for user {update.effective_user.id} after quiz completion")
        return ConversationHandler.END
        
    elif query.data == "quiz_cancel":
        await query.message.reply_text(
            "No problem! You can take the quiz anytime by selecting it from the menu."
        )
        logger.info(f"Ending conversation for user {update.effective_user.id} after quiz cancellation")
        return ConversationHandler.END
        
    elif query.data == "wallet":
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
        logger.error(f"Error context: {context.error_context}")
        logger.error(f"Update that caused error: {update}")
    
    application.add_error_handler(error_handler)

    # Create quiz handler
    quiz_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_callback, pattern="^quiz$")],
        states={
            QUIZ_START: [CallbackQueryHandler(button_callback, pattern="^(quiz_start|quiz_cancel)$")],
            QUIZ_Q1: [CallbackQueryHandler(button_callback, pattern="^q1_[0-2]$")],
            QUIZ_Q2: [CallbackQueryHandler(button_callback, pattern="^q2_[0-2]$")],
            QUIZ_Q3: [CallbackQueryHandler(button_callback, pattern="^q3_[0-2]$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
        name="quiz"
    )

    # Create KYC handler
    kyc_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_callback, pattern="^kyc$")],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_name)],
            BIRTHDAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_birthday)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_phone)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_email)],
            PIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_pin)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
        name="kyc"
    )
    
    # Add handlers
    application.add_handler(quiz_handler)
    application.add_handler(kyc_handler)
    application.add_handler(CommandHandler("start", start))
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
