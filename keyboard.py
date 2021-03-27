from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
)


CALLBACK_BUTTON_WEATHER = 'Узнать погоду 🌈'
CALLBACK_BUTTON_CITY = 'Выбрать город 🌆'
CALLBACK_BUTTON_SETTINGS = 'Настройки ⚙'
CALLBACK_BUTTON_SELECT_CITY = 'Ввести вручную ✍'
CALLBACK_BUTTON_NAME = 'Сменить имя 🧘'
CALLBACK_BUTTON_TIME = 'Установить время уведомления ⏰'
CALLBACK_BUTTON_CANCEL = 'Отмена ❌'
CALLBACK_BUTTON_GEOPOSITION = KeyboardButton(
    'Отправить своё местоположение 🗺',
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
            [CALLBACK_BUTTON_CANCEL],
        ],
        resize_keyboard=True
    )
    return keyboard


def settings_keyboard():
    keyboard = ReplyKeyboardMarkup(
        [
            [CALLBACK_BUTTON_CITY],
            [CALLBACK_BUTTON_TIME],
            [CALLBACK_BUTTON_NAME],
            [CALLBACK_BUTTON_CANCEL],
        ],
        resize_keyboard=True
    )
    return keyboard


def change_time_keyboard():
    button_list = [
        [
            InlineKeyboardButton('00:00', callback_data='00:00'),
            InlineKeyboardButton('01:00', callback_data='01:00'),
            InlineKeyboardButton('02:00', callback_data='02:00'),
            InlineKeyboardButton('03:00', callback_data='03:00'),
        ],
        [
            InlineKeyboardButton('04:00', callback_data='04:00'),
            InlineKeyboardButton('05:00', callback_data='05:00'),
            InlineKeyboardButton('06:00', callback_data='06:00'),
            InlineKeyboardButton('07:00', callback_data='07:00'),
        ],
        [
            InlineKeyboardButton('08:00', callback_data='08:00'),
            InlineKeyboardButton('09:00', callback_data='09:00'),
            InlineKeyboardButton('10:00', callback_data='10:00'),
            InlineKeyboardButton('11:00', callback_data='11:00'),
        ],
        [
            InlineKeyboardButton('12:00', callback_data='12:00'),
            InlineKeyboardButton('13:00', callback_data='13:00'),
            InlineKeyboardButton('14:00', callback_data='14:00'),
            InlineKeyboardButton('15:00', callback_data='15:00'),
        ],
        [
            InlineKeyboardButton('16:00', callback_data='16:00'),
            InlineKeyboardButton('17:00', callback_data='17:00'),
            InlineKeyboardButton('18:00', callback_data='18:00'),
            InlineKeyboardButton('19:00', callback_data='19:00'),
        ],
        [
            InlineKeyboardButton('20:00', callback_data='20:00'),
            InlineKeyboardButton('21:00', callback_data='21:00'),
            InlineKeyboardButton('22:00', callback_data='22:00'),
            InlineKeyboardButton('23:00', callback_data='23:00'),
        ],
    ]
    keyboard = InlineKeyboardMarkup(button_list)
    return keyboard
