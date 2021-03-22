import os
import logging
import requests

from dotenv import load_dotenv
from pprint import pprint
from emoji_dictionary import CONDITION, WIND_DIR, DAYTIME
from mongo import db, get_user_coordinates


load_dotenv()


TELEGA_TOKEN = os.getenv('TELEGRAM_TOKEN')
YA_TOKEN = os.getenv('YANDEX_API_KEY')
YA_GEO_TOKEN = os.getenv('YANDEX_GEO_KEY')


URL_1 = 'https://api.weather.yandex.ru/v2/informers/'
URL_2 = 'https://geocode-maps.yandex.ru/1.x/'


def get_weather_from_yandex(coordinates):
    """
    Ответ погодных значений
    """
    headers = {'X-Yandex-API-Key': YA_TOKEN}
    params = {
        'lat': str(coordinates['latitude']),
        'lon': str(coordinates['longitude']),
        'lang': 'ru_RU',
    }
    try:
        response = requests.get(URL_1, headers=headers, params=params).json()
        return response
    except requests.RequestException as error:
        logging.error(error)


def weather_now_formating(coordinates):
    weather_now = get_weather_from_yandex(coordinates)['fact']
    weather_now = {
        key: CONDITION.get(value, value) for key, value in weather_now.items()
    }
    weather_now = {
        key: WIND_DIR.get(value, value) for key, value in weather_now.items()
    }
    return weather_now


# weather = weather_now_formating()



def get_geolocation_from_yandex():
    """
    Ответ геолокации
    """
    # headers = {'X-Yandex-API-Key': YA_TOKEN}
    params = {
    'apikey': YA_GEO_TOKEN,
    'geocode': 'Москва беловежская 61',
    'format': 'json',
    # 'geocode': '37.395675,55.704343',
    # 'lang': 'ru_RU',
    }
    try:
        response = requests.get(URL_2, params=params).json()
        return response
    except requests.RequestException as error:
        logging.error(error)


# pprint(get_geolocation_from_yandex())


# bot = telebot.TeleBot(TELEGA_TOKEN)
# keyboard_start = telebot.types.ReplyKeyboardMarkup()
# keyboard_start.row('Погода')

# @bot.message_handler(commands=['start'])
# def start_message(message):
#     bot.send_message(message.chat.id, 'Хаюшки', reply_markup=keyboard_start)


# @bot.message_handler(content_types=['text'])
# def send_text(message):
#     if message.text == 'Класс':
#         bot.send_message(message.chat.id, f'Сейчас погода <b>{feels_like}</b>')


# bot.polling()



