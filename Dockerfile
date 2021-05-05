FROM python:3.8.5

RUN mkdir /code_bot

COPY requirements.txt /code_bot

RUN pip install -r /code_bot/requirements.txt

COPY . /code_bot

WORKDIR /code_bot

CMD python bot.py