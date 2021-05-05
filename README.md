[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![example workflow](https://github.com/raikhert13/weather_telegram_bot/actions/workflows/bot_workflow.yml/badge.svg)
![](https://img.shields.io/pypi/v/python-telegram-bot)
![](https://img.shields.io/pypi/pyversions/python-telegram-bot)
![](https://img.shields.io/github/repo-size/raikhert13/weather_telegram_bot?style=plastic)

# Weather Bot for travelers.
***

### _This bot is for telegram. It will be convenient for people who often change their location._


***
 So what can this bot do:
 * show weather on demand;
 * notify at a specific time specified by the user;
 * it can accept the location of the city in two ways:
    1. sending geolocation by the user;
    2. entering a locality manually;
* сan call the user as he wants, by default, the name is taken from the telegram;

___

For the functioning of this bot, 3 API services were used:
* [API Yandex.Weather](https://yandex.ru/dev/weather/)
Returns the current weather and forecast by coordinates. The free version allows 50 requests per day.
* [API Yandex.Geocoder](https://yandex.ru/dev/maps/geocoder/)
Returns the name of the locality by coordinates, or coordinates by name. The free version allows 1000 requests per day.
* [TimeZoneDB](https://timezonedb.com/)
Returns the necessary time zone by coordinates. This is required to send a local time weather notification.

___
### The database used here is Mongodb. But you can change it to a more convenient one for you.
