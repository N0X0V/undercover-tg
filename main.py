import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command
    """
    yes_button = InlineKeyboardButton("Yes ! Let's go !", callback_data="1")
    no_button = InlineKeyboardButton("Not now ^^'", callback_data="2")
    keyboard_markup = InlineKeyboardMarkup([[yes_button, no_button]])
    await update.message.reply_text(
        "Do you want to start a new game of Undercover ?", reply_markup=keyboard_markup
    )


async def showUpdate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the update received by the bot
    Useful to access message ids or the structure of an update
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text=str(update))


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and edits message"""
    query = update.callback_query
    await query.answer()
    message = (
        "A new game has been launched ! Click on the button below if you want to join !"
        if query.data == "1"
        else "Returning to sleep"
    )
    yes_button = InlineKeyboardButton("I'm in !", callback_data="1")
    no_button = InlineKeyboardButton("Not for me this time", callback_data="2")
    new_reply_markup = InlineKeyboardMarkup([[yes_button, no_button]])
    await query.edit_message_text(
        text=message,
    )
    await query.edit_message_reply_markup(reply_markup=new_reply_markup)


def main() -> None:
    load_dotenv()
    TOKEN = os.environ.get("TOKEN")

    # Build application
    application = ApplicationBuilder().token(TOKEN).build()

    # Create Handlers
    start_handler = CommandHandler("start", start)

    # Add handlers to the app
    application.add_handler(start_handler)
    application.add_handler(CallbackQueryHandler(button))

    # For development
    # showUpdateHandler = MessageHandler(
    #     filters.TEXT & (~filters.COMMAND), showUpdate)
    # application.add_handler(showUpdateHandler)

    # Continuously run the app
    application.run_polling()


if __name__ == "__main__":
    main()
