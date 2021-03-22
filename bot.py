import os
import logging

from dotenv import load_dotenv

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)
from handlers import *
from keyboard import (
    CALLBACK_BUTTON_WEATHER,
    CALLBACK_BUTTON_SETTINGS,
    CALLBACK_BUTTON_NAME,
)


load_dotenv()


TELEGA_TOKEN = os.getenv('TELEGRAM_TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log'
)


def main() -> None:
    updater = Updater(TELEGA_TOKEN)
    logging.info('Start bot')
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(
        MessageHandler(Filters.regex(CALLBACK_BUTTON_WEATHER), send_weather)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.regex(CALLBACK_BUTTON_SETTINGS), get_settings)
    )
    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(
                    Filters.regex(CALLBACK_BUTTON_NAME), change_name
                )
            ],
            states={
                'first_name': [MessageHandler(Filters.text, save_new_name)],
            },
            fallbacks=[MessageHandler(
                Filters.location |
                Filters.contact |
                Filters.voice |
                Filters.sticker |
                Filters.photo |
                Filters.video |
                Filters.audio |
                Filters.document,
                dont_know
            )]
        )
    )
    dispatcher.add_handler(MessageHandler(Filters.text, default_answer))
    dispatcher.add_handler(MessageHandler(Filters.location, get_geolocation))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
