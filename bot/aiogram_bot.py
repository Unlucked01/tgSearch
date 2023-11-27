import os
from aiogram import Bot, Dispatcher
import dotenv

import requests
import time

dotenv.load_dotenv()


# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
BOT_TOKEN = os.getenv('BOT_TOKEN_REQ')

# Замените 'TARGET_USER_ID' на ID пользователя, которому вы хотите отправить сообщение
TARGET_USER_ID = 735406398

# URL для получения обновлений (новых сообщений) от бота
UPDATES_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates'

# URL для отправки сообщения
SEND_MESSAGE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'


def get_updates(offset=None):
    params = {'offset': offset, 'timeout': 30}
    response = requests.get(UPDATES_URL, params=params)
    return response.json()


def get_message(user_id):
    # Forming request parameters for getting user messages
    params = {'chat_id': user_id, 'limit': 1}
    response = requests.get(UPDATES_URL, params=params)
    messages = response.json().get('result', [])
    print(messages)
    if messages:
        return messages[0]['message']
    else:
        return None


def send_message(chat_id, text):
    params = {'chat_id': chat_id, 'text': text}
    response = requests.post(SEND_MESSAGE_URL, data=params)
    return response.json()


def main():
    offset = None

    while True:
        updates = get_updates(offset)
        for update in updates.get('result', []):
            message = update.get('message')
            if message:
                chat_id = message['chat']['id']
                text = message.get('text', 'No text')
                send_message(chat_id, f'You said: {text}')
                offset = update['update_id'] + 1
        time.sleep(5)


if __name__ == "__main__":
    # main()
    send_message(TARGET_USER_ID, "privet")
