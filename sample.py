import os
from telegram import Update, update
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import ParseMode
import telegram
from telegram.ext import Updater
from telegram.ext import CallbackContext
from telegram.ext import Filters
from telegram.ext import MessageHandler
from dotenv import load_dotenv
from weather import get_geolocation_from_yandex

load_dotenv()

TELEGA_TOKEN = os.getenv('TELEGRAM_TOKEN')

BUTTON_HELP = 'Кнопка'

def log_error(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(f'Ошибка: {e}')
            raise e
    return inner

weather = get_weather_from_yandex()['fact']['temp']
@log_error
def button_help_handler(update: Update, context: CallbackContext):
    update.message.reply_text(
        text=(
        # '<strong>Доброе утро Солнышко! 💞</strong>\n'
             f'Сейчас у нас за окном {weather}° 🌤\n'
            #  'А вот ощущается как -5°\n'
            #  'Ветер 2,7 м/с\n'
             ''),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.HTML,
    )

@log_error
def message_handler(update: Update, context: CallbackContext):
    text = update.message.text
    if text == BUTTON_HELP:
        return button_help_handler(update=update, context=context)

    reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUTTON_HELP)],
        ],
        resize_keyboard=True,

    )
    update.message.reply_text(
        text='Hello World',
        reply_markup=reply_markup,
    )

def location(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    user_location = update.message.location
    # logger.info(
    #     "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    # )
    update.message.reply_text(
        'Maybe I can visit you sometime! At last, tell me something about yourself.'
    )

    print(user_location)

def main():
    updater = Updater(
        token=TELEGA_TOKEN,
        use_context=True,
    )
    updater.dispatcher.add_handler(
        MessageHandler(filters=Filters.all, callback=message_handler)
        )

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    '''<b>🌤</b>, <strong>bold</strong>
            <i>italic</i>, <em>italic</em>
            <u>underline</u>, <ins>underline</ins>
            <s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
            <b>bold <i>italic bold <s>italic bold strikethrough</s> <u>underline italic bold</u></i> bold</b>
            <a href="http://www.example.com/">inline URL</a>
            <a href="tg://user?id=123456789">inline mention of a user</a>
            <code>inline fixed-width code</code>
            <pre>pre-formatted fixed-width code block</pre>
            <pre><code class="language-python">pre-formatted fixed-width code block written in the Python programming language</code></pre>
            ☀️'''



#########################################################


GENDER, PHOTO, LOCATION, BIO = range(4)


def start(update: Update, _: CallbackContext) -> int:
    reply_keyboard = [['Boy', 'Girl', 'Other']]

    update.message.reply_text(
        'Hi! My name is Professor Bot. I will hold a conversation with you. '
        'Send /cancel to stop talking to me.\n\n'
        'Are you a boy or a girl?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return GENDER


def gender(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'I see! Please send me a photo of yourself, '
        'so I know what you look like, or send /skip if you don\'t want to.',
        reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO


def photo(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'Gorgeous! Now, send me your location please, or send /skip if you don\'t want to.'
    )

    return LOCATION


def skip_photo(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text(
        'I bet you look great! Now, send me your location please, or send /skip.'
    )

    return LOCATION


def location(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )
    update.message.reply_text(
        'Maybe I can visit you sometime! At last, tell me something about yourself.'
    )

    return BIO


def skip_location(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text(
        'You seem a bit paranoid! At last, tell me something about yourself.'
    )

    return BIO


def bio(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thank you! I hope we can talk again some day.')

    return ConversationHandler.END


def cancel(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(TELEGA_TOKEN)
    logging.info('Start bot')
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GENDER: [MessageHandler(Filters.regex('^(Boy|Girl|Other)$'), gender)],
            PHOTO: [MessageHandler(Filters.photo, photo), CommandHandler('skip', skip_photo)],
            LOCATION: [
                MessageHandler(Filters.location, location),
                CommandHandler('skip', skip_location),
            ],
            BIO: [MessageHandler(Filters.text & ~Filters.command, bio)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()