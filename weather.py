import logging
import os

import requests
from dotenv import load_dotenv

from emoji_dictionary import CONDITION, DAYTIME, WIND_DIR
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


def get_geolocation_from_yandex(location):
    """
    Ответ геолокации
    """
    params = {
    'apikey': YA_GEO_TOKEN,
    'format': 'json',
    'geocode': location,
    'lang': 'ru_Ru',
    }
    try:
        response = requests.get(URL_2, params=params).json()
        return response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
    except requests.RequestException as error:
        logging.error(error)
