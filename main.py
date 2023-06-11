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
import random

JOINING, GAME = range(2)
PLAYERS = {}
TURNS = []
CURRENT_PLAYER = -1
START_MESSAGE = -1
NUM_PLAYERS = -1


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Initiate the game
    """
    global START_MESSAGE
    yes_button = InlineKeyboardButton("Join", callback_data=JOINING)
    no_button = InlineKeyboardButton("Not now actually ^^'", callback_data="sleep")
    keyboard_markup = InlineKeyboardMarkup([[yes_button, no_button]])
    # sending a message returns a message object, send it to yourself to see
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
    # await context.bot.pin_chat_message(
    #     chat_id=update.effective_chat.id, message_id=START_MESSAGE.message_id
    # )
    return JOINING


async def joining(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Updates list of players"""
    global PLAYERS
    query = update.callback_query
    await query.answer()
    user = update.callback_query.from_user
    if query.data != str(JOINING):
        if user.username in PLAYERS:
            PLAYERS.remove(user.username)
        message = f"@{user.username} is eepy and will not take part in the next game :/"
    if query.data == str(JOINING) and user.username in PLAYERS:
        message = "Already registered :)"
    if query.data == str(JOINING) and user.username not in PLAYERS:
        message = f"Welcome on board @{user.username}!"
        PLAYERS[user.username] = user
        baseString = "\n - @"
        await context.bot.edit_message_text(
            text=f"{START_MESSAGE.text}\n\nList of players:{baseString+baseString.join(PLAYERS.keys())}",
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
    global PLAYERS, NUM_PLAYERS
    NUM_PLAYERS = len(PLAYERS)
    await update.message.reply_text(
        text="Okayyyyy let's go! \nAll players shall receive their word in DMs in a few seconds..."
    )
    composition = dispatchWords()
    for player in PLAYERS.keys():
        secretWord = composition.pop()
        await context.bot.send_message(
            chat_id=f"{PLAYERS[player].id}", text=f"Your secret word is {secretWord}"
        )
    return GAME


def selectWord(language="EN") -> str:
    with open(f"./data/words-{language}.txt", "r") as file:
        words = file.readlines()
        selectedWords = words[random.randrange(len(words))].split("..")
        selectedWords[1] = selectedWords[1][:-1]
    return selectedWords


def repartition() -> list:
    global NUM_PLAYERS
    compositions = {
        3: [(2, 1)],
        4: [(3, 1)],
        5: [(4, 1), (3, 2)],
        6: [(5, 1), (4, 2)],
        7: [(6, 1), (5, 2), (4, 3)],
        8: [(7, 1), (6, 2), (5, 3)],
        9: [(8, 1), (7, 2), (6, 3), (5, 4)],
    }  # Could be simplified by choosing only one, the other can be deduced, will probably make it easier to introduce Mr. White
    composition = (1, 0)
    # if numPlayers < 3:
    #     raise ValueError("Not enough players or too many to hold a game")
    # if numPlayers > 9:
    #     raise ValueError("Too many players for this version :/")
    # composition = compositions[numPlayers][
    #     random.randrange(len(compositions[numPlayers]))
    # ]
    return composition


def dispatchWords(language="EN") -> list:
    words = selectWord(language=language)
    composition = repartition()
    firstWord = random.randrange(2)
    result = []
    for _ in range(composition[0]):
        result.append(words[firstWord])
    for _ in range(composition[1]):
        result.append(words[1 - firstWord])
    random.shuffle(result)
    return result


async def game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Temporary
    Should manage the game in the future
    """
    global NUM_PLAYERS
    if TURNS == []:
        TURNS = random.shuffle(PLAYERS.keys())
    CURRENT_PLAYER = (CURRENT_PLAYER + 1) % NUM_PLAYERS

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"It is time for @{TURNS[CURRENT_PLAYER]} to say a word !",
    )


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
