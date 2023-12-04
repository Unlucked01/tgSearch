import os
import random
import sys
import threading
from subprocess import check_output

import requests
from flask import flash
from sqlalchemy.exc import OperationalError
from telethon import errors
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import MemorySession, StringSession
import dotenv
import dataclasses
import asyncio
import re
from aiogram import Bot, Dispatcher
from bot.aiogram_bot import send_message, get_message
from misc.models import Users, dbSession as db_session
from telethon.sync import TelegramClient

dotenv.load_dotenv()
active_clients = {}
active_coroutines = {}
bot = Bot(os.getenv('BOT_TOKEN'))
dp = Dispatcher()
os.chdir(sys.path[0])

BOT_TOKEN = os.getenv('BOT_TOKEN_REQ')

UPDATES_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates'
SEND_MESSAGE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

apiURL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'


def remove_emojis(data):
    emoj = re.compile("["
                      u"\U0001F600-\U0001F64F"  # emoticons
                      u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                      u"\U0001F680-\U0001F6FF"  # transport & map symbols
                      u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                      u"\U00002500-\U00002BEF"  # chinese char
                      u"\U00002702-\U000027B0"
                      u"\U000024C2-\U0001F251"
                      u"\U0001f926-\U0001f937"
                      u"\U00010000-\U0010ffff"
                      u"\u2640-\u2642"
                      u"\u2600-\u2B55"
                      u"\u200d"
                      u"\u23cf"
                      u"\u23e9"
                      u"\u231a"
                      u"\ufe0f"  # dingbats
                      u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', data)


async def exec(client, all_data):
    if client:
        sent_messages = []

        async def findWholeWord(word, text):
            pattern = rf'(^|\W){re.escape(word)}($|\W)'
            matches = re.search(pattern, text, re.IGNORECASE)
            return bool(matches)

        async def send_message_to_telegram(chat_id, text_message):
            if not ([f"{search_title}", f"{message.id}"] in sent_messages):
                print("founded message!")
                if not chat_id.startswith('-'):
                    chat_id = f'-100{chat_id}'
                else:
                    chat_id = f'-100{chat_id[1:]}'
                print(chat_id)
                await bot.send_message(chat_id=int(chat_id), text=text_message, parse_mode='HTML')
                sent_messages.append([f"{search_title}", f"{message.id}"])

        while True:
            try:
                async with client:
                    chats = await client.get_dialogs()
                    for account_id, settings in all_data.items():
                        for chat in chats:
                            for search_title in settings['groups']:
                                curr_search_title = remove_emojis(search_title.lower().strip())
                                curr_chat_title = remove_emojis(chat.title.lower().strip())
                                if curr_search_title == curr_chat_title:
                                    messages = await client.get_messages(entity=chat, limit=100)
                                    for message in messages:
                                        try:
                                            for word in settings['keywords']:
                                                found_keyword = await findWholeWord(word, message.text)
                                                if found_keyword:
                                                    message_text = f"{message.text}\n\n"
                                                    message_text += f"Пользователь: <a href='https://t.me/@{message.sender.username}'>{message.sender.username}</a>\nГруппа:"
                                                    message_text += f"<a href='https://t.me/c/{message.peer_id.channel_id}'>{chat.title}</a>\n"
                                                    message_text += f"Ключ: {word}\n"
                                                    message_text += f"<a href='https://t.me/c/{message.peer_id.channel_id}/{message.id}'>Оригинал сообщения</a>"
                                                    await send_message_to_telegram(settings['chat_id'], message_text)
                                        except Exception as e:
                                            print(f"Error processing {chat.title}: {e}")
            except asyncio.CancelledError:
                break
    else:
        print("Ошибка подключения клиента")


def stop_user_coroutine(user_id):
    task = active_coroutines.get(user_id)
    if task:
        task.cancel()
        del active_coroutines[user_id]


async def run_bot(login):
    account = db_session.query(Users).filter_by(email=login).first()
    all_data = {}

    task = asyncio.ensure_future(exec(account, all_data))
    active_coroutines[account.id] = task

    if account:
        list_groups = []
        list_keywords = []
        chat_id = None

        for setting in account.settings:
            for group in setting.group.split(','):
                list_groups.append(group.strip())
            for key in setting.key.split(','):
                list_keywords.append(key.strip())
            chat_id = setting.chat_id

        if chat_id != '':
            user_data = {'groups': list_groups, 'keywords': list_keywords, 'chat_id': chat_id}
            all_data[account.id] = user_data
            print(all_data)
        else:
            print("Не заполнено поле chat_id")
    else:
        print("User not found.")

    try:
        client = TelegramClient(session=f'{account.telegram_account.api_id}.session',
                                api_id=account.telegram_account.api_id,
                                api_hash=account.telegram_account.api_hash)
    except:
        raise Exception("Нет телеграм клиента!")

    string = StringSession.save(client.session)
    try:
        await client.connect()
        print("connected")
    except:
        print("exception")
        client = TelegramClient(StringSession(string),
                                api_id=account.telegram_account.api_id,
                                api_hash=account.telegram_account.api_hash)
        await client.connect()
        print("connected")
    if not await client.is_user_authorized():
        print("Необходима авторизация телеграм аккаунта")
        await client.send_code_request(phone=account.telegram_account.phone)
        send_message(account.telegram_account.account_id, "Введите код доступа в формате\n"
                                                          "3 цифры . 2 оставшиеся\n"
                                                          "Например -> '123.45': ")
        await asyncio.sleep(20)
        code = get_message(account.telegram_account.account_id).replace(".", '')
        print(code)
        if code:
            print("sign-in")
            try:
                await client.sign_in(phone=account.telegram_account.phone, code=code)
            except SessionPasswordNeededError:
                send_message(account.telegram_account.account_id, "На аккаунте включена двухфакторная "
                                                                  "аутентификация, пожалуйста введите пароль: ")
                await asyncio.sleep(45)
                password = get_message(account.telegram_account.account_id)
                print(password)
                await client.sign_in(phone=account.telegram_account.phone, code=code, password=password)
            await exec(client, all_data)
            await client.disconnect()
    else:
        print("Аккаунт подключен успешно")
        await exec(client, all_data)

        await client.disconnect()

    return
