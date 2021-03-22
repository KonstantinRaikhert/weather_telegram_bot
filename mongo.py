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


def save_user_geolocation(db, user, user_coord):
    db.users.update_one(
        {'_id': user['_id']},
        {'$set': {
            'coordinates': {
                'longitude': user_coord['longitude'],
                'latitude': user_coord['latitude'],
            }
        }}
    )


def get_user_coordinates(db, effective_user):
    user = db.users.find_one({'user_id': effective_user.id})
    if 'coordinates' in user:
        coordinates = user['coordinates']
        return coordinates
    else:
        return None


def save_user_name(db, effective_user, user_data):
    db.users.update_one(
        {'user_id': effective_user.id},
        {'$set': {'first_name': user_data['first_name']}}
    )
    