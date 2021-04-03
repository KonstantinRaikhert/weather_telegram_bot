import os
import logging

from dotenv import load_dotenv

from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
    Filters,
    MessageHandler,
    Updater
)

from keyboard import (
    CALLBACK_BUTTON_CITY,
    CALLBACK_BUTTON_NAME,
    CALLBACK_BUTTON_SETTINGS,
    CALLBACK_BUTTON_WEATHER,
    CALLBACK_BUTTON_CANCEL,
    CALLBACK_BUTTON_TIME,
    CALLBACK_BUTTON_SELECT_CITY
)
from mongo import db
from handlers import *


load_dotenv()


TELEGA_TOKEN = os.getenv('TELEGRAM_TOKEN')
PASSWORD_FOR_USE = os.getenv('PASSWORD_FOR_USE')


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log'
)


def run_jobs(update):
    users = db.users.find()
    for user in users:
        chat_id = user['chat_id']
        time = get_time_notification(db, chat_id)
        hour = time[0]
        minute = time[1]
        tzinfo = pytz.timezone(get_user_timezone(db, chat_id))
        update.job_queue.run_daily(
            callback=send_weather_in_due_time,
            time=datetime.time(
                hour=hour, minute=minute, tzinfo=tzinfo
            ),
            context=chat_id,
            name=str(chat_id)
        )


def main() -> None:
    updater = Updater(TELEGA_TOKEN)

    logging.info('Start bot')

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(
        MessageHandler(Filters.regex(str(PASSWORD_FOR_USE)), starting)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.regex(CALLBACK_BUTTON_WEATHER), send_weather)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.regex(CALLBACK_BUTTON_SETTINGS), get_settings)
    )
    dispatcher.add_handler(
        MessageHandler(
            Filters.regex(CALLBACK_BUTTON_TIME), change_time_notification
        )
    )
    dispatcher.add_handler(
        MessageHandler(
            Filters.regex(CALLBACK_BUTTON_CANCEL), cancel_return_basic_keyboard
        )
    )
    dispatcher.add_handler(
        CallbackQueryHandler(change_time_inlinebutton_pressed)
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
    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(
                    Filters.regex(CALLBACK_BUTTON_SELECT_CITY), change_city
                )
            ],
            states={
                'location': [MessageHandler(Filters.text, save_city)],
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
    dispatcher.add_handler(
        MessageHandler(Filters.regex(CALLBACK_BUTTON_CITY), get_geolocation)
    )
    dispatcher.add_handler(MessageHandler(Filters.location, save_geolocation))
    dispatcher.add_handler(MessageHandler(Filters.text, default_answer))

    updater.start_polling(bootstrap_retries=-1)
    run_jobs(updater)
    updater.idle()


if __name__ == '__main__':
    main()
