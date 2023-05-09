import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command
    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Do you want to start a new game of Undercover ?",
    )


async def showUpdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show the update received by the bot
    Useful to access message ids or the structure of an update
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text=str(update))


if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.environ.get("TOKEN")

    # Build application
    application = ApplicationBuilder().token(TOKEN).build()

    # Create Handlers
    start_handler = CommandHandler("start", start)

    # Add handlers to the app
    application.add_handler(start_handler)

    # For development
    # showUpdateHandler = MessageHandler(
    #     filters.TEXT & (~filters.COMMAND), showUpdate)
    # application.add_handler(showUpdateHandler)

    # Continuously run the app
    application.run_polling()
