import logging
import datetime, pytz

from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from telegram.ext.conversationhandler import ConversationHandler
from telegram.replykeyboardremove import ReplyKeyboardRemove

from utility import GREETING
from keyboard import *
from mongo import *
from weather import *


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


def get_geolocation_and_set_time(update: Update, context: CallbackContext):
    hour, minute = get_time_notification(db, update.effective_user.id)
    tzinfo = pytz.timezone(get_user_timezone(db, update.effective_user.id))
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

# локация еще не приходит пересмотреть вводы
def save_geolocation(update: Update, _: CallbackContext):
    coordinates = update.message.location
    timezone = get_timezone_for_geolocation(coordinates)
    coordinates_for_ya = (
        str(coordinates['longitude']) + ',' + str(coordinates['latitude'])
    )
    location = get_geolocation_from_yandex(coordinates_for_ya)['metaDataProperty']['GeocoderMetaData']['text']
    save_user_geolocation(db, update.effective_user.id, coordinates, location)
    user = search_or_save_user(
        db, update.effective_user, update.effective_message
    )
    save_user_geolocation(db, update.effective_user.id, coordinates, location)
    save_user_timezone(db, update.effective_user.id, timezone)
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


def save_city(update: Update, context: CallbackContext):
    context._user_data['location'] = update.message.text
    location_for_ya = get_geolocation_from_yandex(
        context._user_data['location']
    )
    user_coord = {
        'longitude': float((location_for_ya['Point']['pos']).split()[0]),
        'latitude': float((location_for_ya['Point']['pos']).split()[1]),
    }
    location = location_for_ya['metaDataProperty']['GeocoderMetaData']['text']
    timezone = get_timezone_for_geolocation(user_coord)
    save_user_geolocation(db, update.effective_user.id, user_coord, location)
    save_user_timezone(db, update.effective_user.id, timezone)
    user = search_or_save_user(
        db, update.effective_user, update.effective_message
    )
    text = (
        'Готово {}. Буду присылать погоду для:\n'
        '{}'.format(user['first_name'], user['location'])
    )
    update.message.reply_text(text, reply_markup=basic_keyboard())
    return ConversationHandler.END


def change_time_notification(update: Update, context: CallbackContext):
    text = 'В какое время удобно получать сводку погоды?'
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=text,
        reply_markup=change_time_keyboard()
    )


def change_time_inlinebutton_pressed(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    text = 'Отлично! Буду уведовмлять в {}'.format(data)
    save_time_notification(db, update.effective_user, data)
    context.bot.edit_message_text(
        text=text,
        chat_id=query.message.chat.id,
        message_id=query.message.message_id
    )


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


def save_new_name(update: Update, context: CallbackContext):
    context.user_data['first_name'] = update.message.text
    save_user_name(db, update.effective_user, context.user_data)
    user = search_or_save_user(
        db, update.effective_user, update.effective_message
    )
    text = 'Теперь Вы для меня {}'.format(user['first_name'])
    update.message.reply_text(text, reply_markup=basic_keyboard())
    return ConversationHandler.END


def default_answer(update: Update, context: CallbackContext):
    text = (
        'Я пока не умею поддерживать диалог, но возможно меня скоро научат. 😎'
    )
    update.message.reply_text(text, reply_markup=basic_keyboard())


def cancel_return_basic_keyboard(update: Update, _: CallbackContext):
    text = 'Попробуйте ещё раз... Ну... или потом.'
    update.message.reply_text(text, reply_markup=basic_keyboard())


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
        weather = weather_formating(coordinates)
        text_fact = (
            '<b>{}, сейчас за окном:</b>\n'
            '   <i>{condition}</i>\n'
            '   <i>Температура</i> <b>{temp}°</b>.\n'
            '   <i>А вот ощущается как</i> <b>{feels_like}°</b>.\n'
            '   <i>Влажность воздуха</i> <b>{humidity} %</b>.\n'
            '   <i>Давление</i> <b>{pressure_mm} мм. рт. ст.</b>\n'
            '   <i>Ветер</i> <b>{wind_dir}</b>.\n'
            '   <i>Скорость</i> <b>{wind_speed} м/с</b>.\n'
            '   <i>Порывы</i> <b>{wind_gust} м/с</b>.\n'
        ).format(get_user_name(db, update.effective_user.id), **weather['fact'])
        text_forecast = (
            '   <b>Прогноз на {date}:</b>\n'
            '   <i>Восход - <b>{sunrise}</b>, Закат - <b>{sunrise}</b>.</i>\n'
            '   <i>Фаза Луны - {moon_text}</i>\n'
        ).format(**weather['forecast'])
        text_forecast_night = (
            '<b>{part_name} ожидается:</b>\n'
            '   <i>{condition}</i>\n'
            '   <i>Средняя температура</i> <b>{temp_avg}°</b>.\n'
            '   <i>мин. - </i> <b>{temp_min}°</b>.'
            '   <i>макс. - </i> <b>{temp_max}°</b>.\n'
            '   <i>Будет ощущаться</i> <b>{feels_like}°</b>.\n'
            '   <i>Влажность воздуха</i> <b>{humidity} %</b>.\n'
            '   <i>Давление</i> <b>{pressure_mm} мм. рт. ст.</b>\n'
            '   <i>Ветер</i> <b>{wind_dir}</b>.\n'
            '   <i>Скорость</i> <b>{wind_speed} м/с</b>.\n'
            '   <i>Порывы</i> <b>{wind_gust} м/с</b>.\n'
        ).format(**weather['forecast_night'])
        text_forecast_day = (
            '<b>{part_name}:</b>\n'
            '   <i>{condition}</i>\n'
            '   <i>Средняя температура</i> <b>{temp_avg}°</b>.\n'
            '   <i>мин. - </i> <b>{temp_min}°</b>.'
            '   <i>макс. - </i> <b>{temp_max}°</b>.\n'
            '   <i>Будет ощущаться</i> <b>{feels_like}°</b>.\n'
            '   <i>Влажность воздуха</i> <b>{humidity} %</b>.\n'
            '   <i>Давление</i> <b>{pressure_mm} мм. рт. ст.</b>\n'
            '   <i>Ветер</i> <b>{wind_dir}</b>.\n'
            '   <i>Скорость</i> <b>{wind_speed} м/с</b>.\n'
            '   <i>Порывы</i> <b>{wind_gust} м/с</b>.\n'
        ).format(**weather['forecast_day'])
        text = (
            text_fact + text_forecast + text_forecast_night + text_forecast_day
        )
        update.message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=basic_keyboard()
        )


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
        weather = weather_formating(coordinates)
        username = get_user_name(db, job.context)
        text_fact = (
            '<b>{}, сейчас за окном:</b>\n'
            '   <i>{condition}</i>\n'
            '   <i>Температура</i> <b>{temp}°</b>.\n'
            '   <i>А вот ощущается как</i> <b>{feels_like}°</b>.\n'
            '   <i>Влажность воздуха</i> <b>{humidity} %</b>.\n'
            '   <i>Давление</i> <b>{pressure_mm} мм. рт. ст.</b>\n'
            '   <i>Ветер</i> <b>{wind_dir}</b>.\n'
            '   <i>Скорость</i> <b>{wind_speed} м/с</b>.\n'
            '   <i>Порывы</i> <b>{wind_gust} м/с</b>.\n'
        ).format(username, **weather['fact'])
        text_forecast = (
            '   <b>Прогноз на {date}:</b>\n'
            '   <i>Восход - <b>{sunrise}</b>, Закат - <b>{sunrise}</b>.</i>\n'
            '   <i>Фаза Луны - {moon_text}</i>\n'
        ).format(**weather['forecast'])
        text_forecast_night = (
            '<b>{part_name} ожидается:</b>\n'
            '   <i>{condition}</i>\n'
            '   <i>Средняя температура</i> <b>{temp_avg}°</b>.\n'
            '   <i>мин. - </i> <b>{temp_min}°</b>.'
            '   <i>макс. - </i> <b>{temp_max}°</b>.\n'
            '   <i>Будет ощущаться</i> <b>{feels_like}°</b>.\n'
            '   <i>Влажность воздуха</i> <b>{humidity} %</b>.\n'
            '   <i>Давление</i> <b>{pressure_mm} мм. рт. ст.</b>\n'
            '   <i>Ветер</i> <b>{wind_dir}</b>.\n'
            '   <i>Скорость</i> <b>{wind_speed} м/с</b>.\n'
            '   <i>Порывы</i> <b>{wind_gust} м/с</b>.\n'
        ).format(**weather['forecast_night'])
        text_forecast_day = (
            '<b>{part_name}:</b>\n'
            '   <i>{condition}</i>\n'
            '   <i>Средняя температура</i> <b>{temp_avg}°</b>.\n'
            '   <i>мин. - </i> <b>{temp_min}°</b>.'
            '   <i>макс. - </i> <b>{temp_max}°</b>.\n'
            '   <i>Будет ощущаться</i> <b>{feels_like}°</b>.\n'
            '   <i>Влажность воздуха</i> <b>{humidity} %</b>.\n'
            '   <i>Давление</i> <b>{pressure_mm} мм. рт. ст.</b>\n'
            '   <i>Ветер</i> <b>{wind_dir}</b>.\n'
            '   <i>Скорость</i> <b>{wind_speed} м/с</b>.\n'
            '   <i>Порывы</i> <b>{wind_gust} м/с</b>.\n'
        ).format(**weather['forecast_day'])
        text = (
            text_fact + text_forecast + text_forecast_night + text_forecast_day
        )
    context.bot.send_message(job.context, text, parse_mode=ParseMode.HTML)
