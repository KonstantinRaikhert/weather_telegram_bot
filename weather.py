import os
import logging

import requests
from dotenv import load_dotenv
from dateutil.parser import parse

from emoji_dictionary import CONDITION, DAYTIME, MOON_CODE, WIND_DIR


load_dotenv()


TELEGA_TOKEN = os.getenv('TELEGRAM_TOKEN')
YA_TOKEN = os.getenv('YANDEX_API_KEY')
YA_GEO_TOKEN = os.getenv('YANDEX_GEO_KEY')
TIMEZONE_TOKEN = os.getenv('TIMEZONE_DB_API_KEY')


URL_WEATHER = 'https://api.weather.yandex.ru/v2/informers/'
URL_GEOCODER = 'https://geocode-maps.yandex.ru/1.x/'
URL_TIMEZONE = 'http://api.timezonedb.com/v2.1/get-time-zone'


def get_weather_from_yandex(coordinates):
    headers = {'X-Yandex-API-Key': YA_TOKEN}
    params = {
        'lat': str(coordinates['latitude']),
        'lon': str(coordinates['longitude']),
        'lang': 'ru_RU',
    }
    try:
        response = requests.get(URL_WEATHER, headers=headers, params=params)
        if response.status_code == '403':
            return None
        else:
            return response.json()
    except requests.RequestException as error:
        logging.error(error)


def weather_formating(coordinates):
    weather = get_weather_from_yandex(coordinates)
    if weather == None:
        return None
    else:
        weather_fact = weather['fact']
        weather_fact = {
            key: CONDITION.get(value, value)
            for key, value in weather_fact.items()
        }
        weather_fact = {
            key: WIND_DIR.get(value, value)
            for key, value in weather_fact.items()
        }

        weather_forecast = weather['forecast']
        weather_all_day = weather_forecast.pop('parts')
        weather_forecast = {
            key: MOON_CODE.get(value, value)
            for key, value in weather_forecast.items()
        }
        weather_forecast.update(
            date=parse(weather_forecast['date']).strftime('%d.%m.%Y')
        )

        weather_forecast_night = weather_all_day[0]
        weather_forecast_night = {
            key: DAYTIME.get(value, value)
            for key, value in weather_forecast_night.items()
        }
        weather_forecast_night = {
            key: CONDITION.get(value, value)
            for key, value in weather_forecast_night.items()
        }
        weather_forecast_night = {
            key: WIND_DIR.get(value, value)
            for key, value in weather_forecast_night.items()
        }

        weather_forecast_day = weather_all_day[1]
        weather_forecast_day = {
            key: DAYTIME.get(value, value)
            for key, value in weather_forecast_day.items()
        }
        weather_forecast_day = {
            key: CONDITION.get(value, value)
            for key, value in weather_forecast_day.items()
        }
        weather_forecast_day = {
            key: WIND_DIR.get(value, value)
            for key, value in weather_forecast_day.items()
        }
        weather_dict = {
            'fact': weather_fact,
            'forecast': weather_forecast,
            'forecast_night': weather_forecast_night,
            'forecast_day': weather_forecast_day,
        }

        return weather_dict


def get_geolocation_from_yandex(location):
    params = {
        'apikey': YA_GEO_TOKEN,
        'format': 'json',
        'geocode': location,
        'lang': 'ru_Ru',
    }
    try:
        response = requests.get(URL_GEOCODER, params=params).json()
        return response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
    except requests.RequestException as error:
        logging.error(error)


def get_timezone_for_geolocation(coordinates):
    params = {
        'key': TIMEZONE_TOKEN,
        'format': 'json',
        'by': 'position',
        'fields': 'zoneName',
        'lat': str(coordinates['latitude']),
        'lng': str(coordinates['longitude']),
    }
    try:
        response = requests.get(URL_TIMEZONE, params=params).json()
        return response['zoneName']
    except requests.RequestException as error:
        logging.error(error)
