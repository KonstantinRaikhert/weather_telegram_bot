from telegram import ReplyKeyboardMarkup, KeyboardButton

# Реализовать кнопку отмена для отображения basic

CALLBACK_BUTTON_WEATHER = 'Узнать погоду 🌈'
CALLBACK_BUTTON_CITY = 'Выбрать город 🌆'
CALLBACK_BUTTON_SETTINGS = 'Настройки ⚙'
CALLBACK_BUTTON_SELECT_CITY = 'Ввести вручную'
CALLBACK_BUTTON_NAME = 'Сменить имя'
CALLBACK_BUTTON_GEOPOSITION = KeyboardButton(
    'Отправить своё местоположение',
    request_location=True
)


def basic_keyboard():
    keyboard = ReplyKeyboardMarkup(
        [
            [CALLBACK_BUTTON_WEATHER],
            [CALLBACK_BUTTON_SETTINGS],
        ],
        resize_keyboard=True
    )
    return keyboard


def geolocation_keyboard():
    keyboard = ReplyKeyboardMarkup(
        [
            [CALLBACK_BUTTON_SELECT_CITY],
            [CALLBACK_BUTTON_GEOPOSITION],
        ],
        resize_keyboard=True
    )
    return keyboard


def settings_keyboard():
    keyboard = ReplyKeyboardMarkup(
        [
            [CALLBACK_BUTTON_CITY],
            [CALLBACK_BUTTON_NAME],
        ],
        resize_keyboard=True
    )
    return keyboard