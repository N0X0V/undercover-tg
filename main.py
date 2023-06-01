import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
)
import time

JOINING, GAME = range(2)
PLAYERS = set([])
START_MESSAGE = -1


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Initiate the game
    """
    global START_MESSAGE
    yes_button = InlineKeyboardButton("Join", callback_data=JOINING)
    no_button = InlineKeyboardButton("Not now actually ^^'", callback_data="sleep")
    keyboard_markup = InlineKeyboardMarkup([[yes_button, no_button]])
    message = await update.message.reply_text(
        "A new game has been launched !",
        reply_markup=keyboard_markup,
    )
    if START_MESSAGE != -1:
        await update.message.reply_text(
            "A game is already being played",
            reply_markup=keyboard_markup,
        )
    START_MESSAGE = message
    await context.bot.pin_chat_message(
        chat_id=update.effective_chat.id, message_id=START_MESSAGE.message_id
    )
    return JOINING


async def joining(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Updates list of players"""
    query = update.callback_query
    await query.answer()
    user = update.callback_query.from_user.username
    if query.data != str(JOINING):
        if user in PLAYERS:
            PLAYERS.remove(str(user))
        message = f"@{user} is eepy and will not take part in the next game :/"
    if query.data == str(JOINING) and user in PLAYERS:
        message = "Already registered :)"
    if query.data == str(JOINING) and user not in PLAYERS:
        message = f"Welcome on board @{user}!"
        PLAYERS.add(user)
        baseString = "\n - @"
        await context.bot.edit_message_text(
            text=f"{START_MESSAGE.text}\n\nList of players:{baseString+baseString.join(PLAYERS)}",
            chat_id=update.effective_chat.id,
            message_id=START_MESSAGE.message_id,
        )

    welcome = await context.bot.send_message(
        chat_id=update.effective_chat.id, text=message
    )
    time.sleep(5)
    await context.bot.delete_message(
        chat_id=update.effective_chat.id, message_id=welcome.message_id
    )


async def gameStart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Launches the game
    """
    await update.message.reply_text(text="Okayyyyy let's go!")
    return GAME


async def game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Temporary
    Should manage the game in the future
    """
    await update.message.reply_text(text="G@ming")


async def showUpdate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the update received by the bot
    Useful to access message ids or the structure of an update
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text=str(update))


def main() -> None:
    load_dotenv()
    TOKEN = os.environ.get("TOKEN")

    # Build application
    application = ApplicationBuilder().token(TOKEN).build()

    # Create Handlers
    conversationHandler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            JOINING: [
                CommandHandler("begin", gameStart),
                CallbackQueryHandler(joining),
            ],
            GAME: [CommandHandler("game", game)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Add handlers to the app
    application.add_handler(conversationHandler)

    # For development
    # showUpdateHandler = MessageHandler(
    #     filters.TEXT & (~filters.COMMAND), showUpdate)
    # application.add_handler(showUpdateHandler)

    # Continuously run the app
    application.run_polling()


if __name__ == "__main__":
    main()
