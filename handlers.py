import logging
from telegram import Update, ParseMode, replymarkup
from telegram.ext import CallbackContext
from weather import weather_now_formating
from mongo import db, get_user_coordinates, search_or_save_user, save_user_geolocation
from keyboard import *
from utility import GREETING

weather = {
    'condition': 'Облачно с прояснениями 🌥',
    'daytime': 'северный',
    'feels_like': -7,
    'humidity': 80,
    'icon': 'bkn_n',
    'obs_time': 1616180400,
    'polar': False,
    'pressure_mm': 745,
    'pressure_pa': 993,
    'season': 'spring',
    'temp': -3,
    'wind_dir': 'северный',
    'wind_gust': 5.4,
    'wind_speed': 2
}

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log'
)


def start(update: Update, _: CallbackContext):
    user = search_or_save_user(
        db, update.effective_user, update.effective_message
    )
    # print(user)
    text = (
        '{} {}!\n'
        '\n'
        'Каждый день в нужное время\n'
        'я буду присылать текущую погоду\n'
        'и прогноз погоды на день и ночь.\n'
        'В настройках можно выбрать\n'
        'текущий город и время оповещения.'
        ''.format(GREETING, user['first_name'])
    )
    update.message.reply_text(text,
        reply_markup=basic_keyboard()
    )


def get_geolocation(update: Update, _: CallbackContext):
    coord = update.message.location
    user = search_or_save_user(
        db, update.effective_user, update.effective_message
    )
    save_user_geolocation(db, user, coord)


def default_answer(update: Update, _: CallbackContext):
    text = (
        'Я пока не умею поддерживать диалог, но возможно меня скоро научат. 😎'
    )
    update.message.reply_text(text, reply_markup=basic_keyboard())

def send_weather(update: Update, _: CallbackContext):
    coordinates = get_user_coordinates(db, update.effective_user)
    # print(coordinates)
    if coordinates == None:
        text = 'Для начала укажите в настройках Ваше местоположение'
        update.message.reply_text(text, reply_markup=basic_keyboard())
    else:
    # print(weather_now_formating(get_user_coordinates(db, update.effective_user)))
        text = '''
        <b>Сейчас за окном (ну или где ты там):</b>
        <i>{condition}</i>
        <i>Температура</i> <b>{temp}°</b>.
        <i>А вот ощущается как</i> <b>{feels_like}°</b>.
        <i>Влажность воздуха</i> <b>{humidity} %</b>.
        <i>Давление</i> <b>{pressure_mm} мм. рт. ст.</b>
        <i>Ветер</i> <b>{wind_dir}</b>.
        <i>Скорость</i> <b>{wind_speed} м/с</b>.
        <i>Порывы</i> <b>{wind_gust} м/с</b>.
        '''.format(**weather_now_formating(coordinates))
        update.message.reply_text(
            text, parse_mode=ParseMode.HTML, reply_markup=basic_keyboard()
        )

