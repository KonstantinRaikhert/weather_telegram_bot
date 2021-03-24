import logging
import datetime, pytz

from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from telegram.ext.conversationhandler import ConversationHandler
from telegram.replykeyboardremove import ReplyKeyboardRemove

from keyboard import *
from mongo import *
from utility import GREETING
from weather import get_geolocation_from_yandex, weather_now_formating

# weather = {
#     'condition': 'Облачно с прояснениями 🌥',
#     'daytime': 'северный',
#     'feels_like': -7,
#     'humidity': 80,
#     'icon': 'bkn_n',
#     'obs_time': 1616180400,
#     'polar': False,
#     'pressure_mm': 745,
#     'pressure_pa': 993,
#     'season': 'spring',
#     'temp': -3,
#     'wind_dir': 'северный',
#     'wind_gust': 5.4,
#     'wind_speed': 2
# }


file_log = logging.FileHandler('bot.log')
console_out = logging.StreamHandler()
logging.basicConfig(
    handlers=(file_log, console_out),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)


def start(update: Update, _: CallbackContext):
    user = search_or_save_user(
        db, update.effective_user, update.effective_message
    )
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

# Реализация API https://timezonedb.com/references/get-time-zone
# Сохраненение и вызов из БД времени отправки сообщения о погоде
def get_geolocation(update: Update, context: CallbackContext):
    hour = 23
    minute = 53
    tzinfo = pytz.timezone('Europe/Moscow')
    text = (
        'Выберите удобный способ для\n'
        'определения Вашего местонахождения'
    )
    update.message.reply_text(text, reply_markup=geolocation_keyboard())
    context.job_queue.run_daily(
        send_weather_in_due_time,
        context=update.message.chat_id,
        time=datetime.time(
            hour=hour, minute=minute, tzinfo=tzinfo
        )
    )


# Реализация inline клавиатуры с кнопками выбора часа уведомления

def save_geolocation(update: Update, _: CallbackContext):
    coordinates = update.message.location
    coordinates_for_ya = (
        str(coordinates['longitude']) + ',' + str(coordinates['latitude'])
    )
    user = search_or_save_user(
        db, update.effective_user, update.effective_message
    )
    location = get_geolocation_from_yandex(
        coordinates_for_ya
    )['metaDataProperty']['GeocoderMetaData']['text']
    save_user_geolocation(db, user, coordinates, location)
    text = (
        'Готово {}. Буду присылать погоду для:\n'
        '{}'.format(user['first_name'], user['location'])
    )
    update.message.reply_text(text, reply_markup=basic_keyboard())

def change_city(update: Update, _: CallbackContext):
    text = (
        'Напишите область и населённый пункт.\n'
        'При необходимости можно указать страну.'
    )
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    return 'location'


def save_city(update: Update, _: CallbackContext):
    _._user_data['location'] = update.message.text
    user = search_or_save_user(
        db, update.effective_user, update.effective_message
    )
    location_for_ya = get_geolocation_from_yandex(_._user_data['location'])
    user_coord = {
        'longitude': float((location_for_ya['Point']['pos']).split()[0]),
        'latitude': float((location_for_ya['Point']['pos']).split()[1]),
    }
    location = location_for_ya['metaDataProperty']['GeocoderMetaData']['text']
    save_user_geolocation(db, user, user_coord, location)
    user = search_or_save_user(
        db, update.effective_user, update.effective_message
    )
    text = (
        'Готово {}. Буду присылать погоду для:\n'
        '{}'.format(user['first_name'], user['location'])
    )
    update.message.reply_text(text, reply_markup=basic_keyboard())
    return ConversationHandler.END


def default_answer(update: Update, context: CallbackContext):
    text = (
        'Я пока не умею поддерживать диалог, но возможно меня скоро научат. 😎'
    )
    update.message.reply_text(text, reply_markup=basic_keyboard())


def get_settings(update: Update, _: CallbackContext):
    text = (
        'Задайте своё местонахождение.\n'
        'А если Вам не нравится, как я к Вам\n'
        'обращаюсь, смените имя. 👻'
    )
    update.message.reply_text(text, reply_markup=settings_keyboard())


def change_name(update: Update, _: CallbackContext):
    text = 'Как изволите величать?'
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    return 'first_name'


def save_new_name(update: Update, _: CallbackContext):
    _.user_data['first_name'] = update.message.text
    save_user_name(db, update.effective_user, _.user_data)
    user = search_or_save_user(
        db, update.effective_user, update.effective_message
    )
    text = 'Теперь Вы для меня {}'.format(user['first_name'])
    update.message.reply_text(text, reply_markup=basic_keyboard())
    return ConversationHandler.END


def dont_know(update: Update, _: CallbackContext):
    text = (
        'Пожалуйста, не нужно мне ничего\n'
        'прысылать. Просто напиши своё новое имя.'
    )
    update.message.reply_text(text)


def send_weather(update: Update, context: CallbackContext):
    coordinates = get_user_coordinates(db, update.effective_user.id)
    if coordinates == None:
        text = 'Для начала укажите в настройках Ваше местоположение'
        update.message.reply_text(text, reply_markup=basic_keyboard())
    else:
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

# Сейчас только фактическая погода, реализовать прогноз на 2 след периода

def send_weather_in_due_time(context: CallbackContext):
    job = context.job
    coordinates = get_user_coordinates(db, job.context)
    if coordinates == None:
        text = (
            'Укажите в настройках Ваше местоположение\n'
            'и тогда я смогу присылать сводки погоды.'
        )
        context.bot.send_message(job.context, text)
    else:
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
    context.bot.send_message(job.context, text, parse_mode=ParseMode.HTML)