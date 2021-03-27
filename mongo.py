import os

from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()


MONGO_AUTH = os.getenv('PASSWORD_MONGO')

client = MongoClient(MONGO_AUTH)
db = client.get_database('telegram_bot')


def search_or_save_user(db, effective_user, message):
    user = db.users.find_one({'user_id': effective_user.id})
    if not user:
        user = {
            'user_id': effective_user.id,
            'first_name': effective_user.first_name,
            'last_name': effective_user.last_name,
            'chat_id': message.chat.id,
        }
        db.users.insert_one(user)
    return user


def get_user_name(db, effective_chat):
    user = db.users.find_one({'user_id': effective_chat})
    return user['first_name']       


def save_user_name(db, effective_user, user_data):
    db.users.update_one(
        {'user_id': effective_user.id},
        {'$set': {'first_name': user_data['first_name']}}
    )


def save_user_geolocation(db, effective_user, user_coord, location):
    db.users.update_one(
        {'user_id': effective_user},
        {'$set': {
            'coordinates': {
                'longitude': user_coord['longitude'],
                'latitude': user_coord['latitude'],
            },
            'location': location,
        }}
    )


def get_user_coordinates(db, effective_user):
    user = db.users.find_one({'user_id': effective_user})
    if 'coordinates' in user:
        coordinates = user['coordinates']
        return coordinates
    else:
        return None


def save_user_timezone(db, effective_user, user_timezone):
    db.users.update_one(
        {'user_id': effective_user},
        {'$set': {'timezone': user_timezone}}
    )


def get_user_timezone(db, effective_user):
    user = db.users.find_one({'user_id': effective_user})
    default = 'Europe/Moscow'
    if 'timezone' in user:
        timezone = user['timezone']
        return timezone
    else:
        return default


def save_time_notification(db, effective_user, time_data):
    db.users.update_one(
        {'user_id': effective_user.id},
        {'$set': {'time_notification': time_data}}
    )


def get_time_notification(db, effective_user):
    user = db.users.find_one({'user_id': effective_user})
    default = [10, 0]
    if 'time_notification' in user:
        time_notification = list(
            map(int, user['time_notification'].split(':'))
        )
        return time_notification
    else:
        return default
