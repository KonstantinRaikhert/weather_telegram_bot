import os
import logging

from dotenv import load_dotenv

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from handlers import *
from keyboard import CALLBACK_BUTTON_WEATHER

load_dotenv()

TELEGA_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log'
)


def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(TELEGA_TOKEN)
    logging.info('Start bot')
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(
        MessageHandler(Filters.regex(CALLBACK_BUTTON_WEATHER), send_weather)
    )
    dispatcher.add_handler(MessageHandler(Filters.text, default_answer))
    dispatcher.add_handler(MessageHandler(Filters.location, get_geolocation))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
