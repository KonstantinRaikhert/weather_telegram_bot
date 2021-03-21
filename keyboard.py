from telegram import ReplyKeyboardMarkup, KeyboardButton


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
            [CALLBACK_BUTTON_GEOPOSITION],
            [CALLBACK_BUTTON_SELECT_CITY],
        ],
        resize_keyboard=True
    )
    return keyboard


def settings_keyboard():
    keyboard = ReplyKeyboardMarkup(
        [
            [CALLBACK_BUTTON_NAME],
            [CALLBACK_BUTTON_CITY],
        ],
        resize_keyboard=True
    )
    return keyboard