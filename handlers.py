import logging
import datetime
import pytz

from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from telegram.ext.conversationhandler import ConversationHandler
from telegram.replykeyboardremove import ReplyKeyboardRemove

from utility import GREETING
from keyboard import (
    basic_keyboard,
    settings_keyboard,
    geolocation_keyboard,
    change_time_keyboard,
)
from mongo import (
    db,
    search_or_save_user,
    search_user,
    get_user_name,
    save_user_name,
    save_user_geolocation,
    get_user_coordinates,
    save_user_timezone,
    get_user_timezone,
    save_time_notification,
    get_time_notification,
)
from weather import (
    get_geolocation_from_yandex,
    get_timezone_for_geolocation,
    weather_formating,
)


file_log = logging.FileHandler("bot.log")
console_out = logging.StreamHandler()
logging.basicConfig(
    handlers=(file_log, console_out),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def start(update: Update, _: CallbackContext):
    update.message.reply_text("Введите пароль для использования")


def starting(update: Update, _: CallbackContext):
    user = search_or_save_user(
        db, update.effective_user, update.effective_message
    )
    text = (
        "{} {}!\n"
        "\n"
        "Каждый день в нужное время\n"
        "я буду присылать текущую погоду\n"
        "и прогноз погоды на день и ночь.\n"
        "В настройках нужно выбрать\n"
        "текущий город и время оповещения."
        "".format(GREETING, user["first_name"])
    )
    update.message.reply_text(text, reply_markup=basic_keyboard())


def remove_job(name: str, context: CallbackContext):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    for job in current_jobs:
        job.schedule_removal()


def get_geolocation(update: Update, context: CallbackContext):
    text = "Выберите удобный способ для\n" "определения Вашего местонахождения"
    update.message.reply_text(text, reply_markup=geolocation_keyboard())


def save_geolocation(update: Update, _: CallbackContext):
    coordinates = update.message.location
    timezone = get_timezone_for_geolocation(coordinates)
    coordinates_for_ya = (
        str(coordinates["longitude"]) + "," + str(coordinates["latitude"])
    )
    location = get_geolocation_from_yandex(coordinates_for_ya)[
        "metaDataProperty"
    ]["GeocoderMetaData"]["text"]
    save_user_geolocation(db, update.effective_user.id, coordinates, location)
    user = search_or_save_user(
        db, update.effective_user, update.effective_message
    )
    save_user_geolocation(db, update.effective_user.id, coordinates, location)
    save_user_timezone(db, update.effective_user.id, timezone)
    text = "Готово {}. Буду присылать погоду для:\n" "{}".format(
        user["first_name"], user["location"]
    )
    update.message.reply_text(text, reply_markup=basic_keyboard())


def change_city(update: Update, _: CallbackContext):
    text = (
        "Напишите область и населённый пункт.\n"
        "При необходимости можно указать страну."
    )
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    return "location"


def save_city(update: Update, context: CallbackContext):
    context._user_data["location"] = update.message.text
    location_for_ya = get_geolocation_from_yandex(
        context._user_data["location"]
    )
    user_coord = {
        "longitude": float((location_for_ya["Point"]["pos"]).split()[0]),
        "latitude": float((location_for_ya["Point"]["pos"]).split()[1]),
    }
    location = location_for_ya["metaDataProperty"]["GeocoderMetaData"]["text"]
    timezone = get_timezone_for_geolocation(user_coord)
    save_user_geolocation(db, update.effective_user.id, user_coord, location)
    save_user_timezone(db, update.effective_user.id, timezone)
    user = search_or_save_user(
        db, update.effective_user, update.effective_message
    )
    text = "Готово {}. Буду присылать погоду для:\n" "{}".format(
        user["first_name"], user["location"]
    )
    update.message.reply_text(text, reply_markup=basic_keyboard())
    return ConversationHandler.END


def change_time_notification(update: Update, context: CallbackContext):
    text = "В какое время удобно получать сводку погоды?"
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=text,
        reply_markup=change_time_keyboard(),
    )


def change_time_inlinebutton_pressed(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat.id
    data = query.data
    save_time_notification(db, update.effective_user, data)
    time = get_time_notification(db, update.effective_user.id)
    hour = time[0]
    minute = time[1]
    tzinfo = pytz.timezone(get_user_timezone(db, update.effective_user.id))
    text = "Буду уведовмлять в {}".format(data)
    sticker_id = "CAACAgIAAxkBAAECJG5gaNIygx4rNnhNevnPojRaUi8u1AAC3QMAAvJ-ggxtuk_XOcwsnR4E" # noqa
    context.bot.edit_message_text(
        text=text,
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
    )
    update.effective_chat.send_sticker(
        sticker=sticker_id, reply_markup=basic_keyboard()
    )
    remove_job(str(chat_id), context)
    context.job_queue.run_daily(
        send_weather_in_due_time,
        time=datetime.time(hour=hour, minute=minute, tzinfo=tzinfo),
        context=chat_id,
        name=str(chat_id),
    )


def get_settings(update: Update, _: CallbackContext):
    text = (
        "Задайте своё местонахождение.\n"
        "А если Вам не нравится, как я к Вам\n"
        "обращаюсь, смените имя. 👻"
    )
    update.message.reply_text(text, reply_markup=settings_keyboard())


def change_name(update: Update, _: CallbackContext):
    text = "Как изволите величать?"
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    return "first_name"


def save_new_name(update: Update, context: CallbackContext):
    context.user_data["first_name"] = update.message.text
    save_user_name(db, update.effective_user, context.user_data)
    user = search_or_save_user(
        db, update.effective_user, update.effective_message
    )
    text = "Теперь Вы для меня {}".format(user["first_name"])
    update.message.reply_text(text, reply_markup=basic_keyboard())
    return ConversationHandler.END


def default_answer(update: Update, context: CallbackContext):
    user = search_user(db, update.effective_user)
    if user:
        text = (
            "Я пока не умею поддерживать диалог, "
            "но возможно меня скоро научат. 😎"
        )
        update.message.reply_text(text, reply_markup=basic_keyboard())
    else:
        update.message.reply_text("Неправильный пароль")


def cancel_return_basic_keyboard(update: Update, _: CallbackContext):
    text = "Попробуйте ещё раз... Ну... или потом."
    update.message.reply_text(text, reply_markup=basic_keyboard())


def dont_know(update: Update, _: CallbackContext):
    text = (
        "Пожалуйста, не нужно мне ничего\n"
        "прысылать. Просто напиши своё новое имя."
    )
    update.message.reply_text(text)


def send_weather(update: Update, context: CallbackContext):
    coordinates = get_user_coordinates(db, update.effective_user.id)
    time = get_time_notification(db, update.effective_user.id)
    if coordinates is None:
        text = (
            "Для начала укажите в настройках Ваше местоположение\n"
            "и время оповещения."
        )
        update.message.reply_text(text, reply_markup=basic_keyboard())
    elif time is None:
        text = "Bремя оповещения забыли указать..."
        update.message.reply_text(text, reply_markup=basic_keyboard())
    else:
        weather = weather_formating(coordinates)
        if weather is not None:
            text_fact = (
                "<b>{}, сейчас за окном:</b>\n"
                "   <i>{condition}</i>\n"
                "   <i>Температура</i> <b>{temp}°</b>.\n"
                "   <i>А вот ощущается как</i> <b>{feels_like}°</b>.\n"
                "   <i>Влажность воздуха</i> <b>{humidity} %</b>.\n"
                "   <i>Давление</i> <b>{pressure_mm} мм. рт. ст.</b>\n"
                "   <i>Ветер</i> <b>{wind_dir}</b>.\n"
                "   <i>Скорость</i> <b>{wind_speed} м/с</b>.\n"
                "   <i>Порывы</i> <b>{wind_gust} м/с</b>.\n"
            ).format(
                get_user_name(db, update.effective_user.id), **weather["fact"]
            )
            text_forecast = (
                "   <b>Прогноз на {date}:</b>\n"
                "   <i>Восход - <b>{sunrise}</b>, "
                "   Закат - <b>{sunset}</b>.</i>\n"
                "   <i>Фаза Луны - {moon_text}</i>\n"
            ).format(**weather["forecast"])
            text_forecast_night = (
                "<b>{part_name} ожидается:</b>\n"
                "   <i>{condition}</i>\n"
                "   <i>Средняя температура</i> <b>{temp_avg}°</b>.\n"
                "   <i>мин.:  </i> <b>{temp_min}°</b>."
                "   <i>макс.:  </i> <b>{temp_max}°</b>.\n"
                "   <i>Будет ощущаться</i> <b>{feels_like}°</b>.\n"
                "   <i>Влажность воздуха</i> <b>{humidity} %</b>.\n"
                "   <i>Давление</i> <b>{pressure_mm} мм. рт. ст.</b>\n"
                "   <i>Ветер</i> <b>{wind_dir}</b>.\n"
                "   <i>Скорость</i> <b>{wind_speed} м/с</b>.\n"
                "   <i>Порывы</i> <b>{wind_gust} м/с</b>.\n"
            ).format(**weather["forecast_night"])
            text_forecast_day = (
                "<b>{part_name}:</b>\n"
                "   <i>{condition}</i>\n"
                "   <i>Средняя температура</i> <b>{temp_avg}°</b>.\n"
                "   <i>мин.:  </i> <b>{temp_min}°</b>."
                "   <i>макс.:  </i> <b>{temp_max}°</b>.\n"
                "   <i>Будет ощущаться</i> <b>{feels_like}°</b>.\n"
                "   <i>Влажность воздуха</i> <b>{humidity} %</b>.\n"
                "   <i>Давление</i> <b>{pressure_mm} мм. рт. ст.</b>\n"
                "   <i>Ветер</i> <b>{wind_dir}</b>.\n"
                "   <i>Скорость</i> <b>{wind_speed} м/с</b>.\n"
                "   <i>Порывы</i> <b>{wind_gust} м/с</b>.\n"
            ).format(**weather["forecast_day"])
            text = (
                text_fact
                + text_forecast
                + text_forecast_night
                + text_forecast_day
            )
            update.message.reply_text(
                text, parse_mode=ParseMode.HTML, reply_markup=basic_keyboard()
            )
        else:
            text = (
                "Похоже сегодня я уже устал смотреть на погоду.\n"
                "обращайтесь завтра!"
            )
            update.message.reply_text(text, reply_markup=basic_keyboard())


def send_weather_in_due_time(context: CallbackContext):
    job = context.job
    coordinates = get_user_coordinates(db, job.context)
    weather = weather_formating(coordinates)
    username = get_user_name(db, job.context)
    if weather is not None:
        text_fact = (
            "<b>{}, сейчас за окном:</b>\n"
            "   <i>{condition}</i>\n"
            "   <i>Температура</i> <b>{temp}°</b>.\n"
            "   <i>А вот ощущается как</i> <b>{feels_like}°</b>.\n"
            "   <i>Влажность воздуха</i> <b>{humidity} %</b>.\n"
            "   <i>Давление</i> <b>{pressure_mm} мм. рт. ст.</b>\n"
            "   <i>Ветер</i> <b>{wind_dir}</b>.\n"
            "   <i>Скорость</i> <b>{wind_speed} м/с</b>.\n"
            "   <i>Порывы</i> <b>{wind_gust} м/с</b>.\n"
        ).format(username, **weather["fact"])
        text_forecast = (
            "   <b>Прогноз на {date}:</b>\n"
            "   <i>Восход - <b>{sunrise}</b>, Закат - <b>{sunset}</b>.</i>\n"
            "   <i>Фаза Луны - {moon_text}</i>\n"
        ).format(**weather["forecast"])
        text_forecast_night = (
            "<b>{part_name} ожидается:</b>\n"
            "   <i>{condition}</i>\n"
            "   <i>Средняя температура</i> <b>{temp_avg}°</b>.\n"
            "   <i>мин.:  </i> <b>{temp_min}°</b>."
            "   <i>макс.:  </i> <b>{temp_max}°</b>.\n"
            "   <i>Будет ощущаться</i> <b>{feels_like}°</b>.\n"
            "   <i>Влажность воздуха</i> <b>{humidity} %</b>.\n"
            "   <i>Давление</i> <b>{pressure_mm} мм. рт. ст.</b>\n"
            "   <i>Ветер</i> <b>{wind_dir}</b>.\n"
            "   <i>Скорость</i> <b>{wind_speed} м/с</b>.\n"
            "   <i>Порывы</i> <b>{wind_gust} м/с</b>.\n"
        ).format(**weather["forecast_night"])
        text_forecast_day = (
            "<b>{part_name}:</b>\n"
            "   <i>{condition}</i>\n"
            "   <i>Средняя температура</i> <b>{temp_avg}°</b>.\n"
            "   <i>мин.:  </i> <b>{temp_min}°</b>."
            "   <i>макс.:  </i> <b>{temp_max}°</b>.\n"
            "   <i>Будет ощущаться</i> <b>{feels_like}°</b>.\n"
            "   <i>Влажность воздуха</i> <b>{humidity} %</b>.\n"
            "   <i>Давление</i> <b>{pressure_mm} мм. рт. ст.</b>\n"
            "   <i>Ветер</i> <b>{wind_dir}</b>.\n"
            "   <i>Скорость</i> <b>{wind_speed} м/с</b>.\n"
            "   <i>Порывы</i> <b>{wind_gust} м/с</b>.\n"
        ).format(**weather["forecast_day"])
        text = (
            text_fact + text_forecast + text_forecast_night + text_forecast_day
        )
        context.bot.send_message(job.context, text, parse_mode=ParseMode.HTML)
    else:
        text = (
            "Похоже сегодня я уже устал смотреть на погоду.\n"
            "обращайтесь завтра!"
        )
        context.bot.send_message(job.context, text)
