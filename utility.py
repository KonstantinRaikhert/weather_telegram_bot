import time


def get_greeting():
    current_hour = time.localtime().tm_hour
    if 6 < current_hour < 12:
        greeting = 'Доброе утро'
    if 12 <= current_hour < 18:
        greeting = 'Добрый день'
    if 18 <= current_hour < 23:
        greeting = 'Добрый вечер'
    else:
        greeting = 'Доброй ночи'
    return greeting


GREETING = get_greeting()
