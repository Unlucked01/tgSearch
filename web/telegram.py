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
bot = Bot(os.getenv('BOT_TOKEN'))
dp = Dispatcher()
os.chdir(sys.path[0])

BOT_TOKEN = os.getenv('BOT_TOKEN_REQ')

UPDATES_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates'
SEND_MESSAGE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

apiURL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'


async def create_telegram_client(api_id, api_hash, phone, code='', code_hash='', secret_password=''):
    global active_clients, client
    session_name = str(api_id)
    if session_name in active_clients.keys():
        client = active_clients[session_name]
    else:
        client = TelegramClient(session_name, int(api_id), api_hash)
        await client.connect()
        active_clients[session_name] = client

    if session_name in active_clients.keys():
        client = active_clients[session_name]

    if not await client.is_user_authorized():
        result = ""
        if code == '':
            try:
                phone_code_hash = await client.send_code_request(phone)
                result = phone_code_hash.phone_code_hash
            except Exception as e:
                print(e)
            active_clients[client] = client
            return {'status': False, 'description': 'Please, write sms code',
                    'variables': {'phone_code_hash': result}}
        try:
            await asyncio.create_task(client.sign_in(phone=phone, code=code, phone_code_hash=result))
        except SessionPasswordNeededError:
            await asyncio.create_task(client.sign_in(password=secret_password))
    print(await client.is_user_authorized())
    return {'status': True, 'description': ''}


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
    flash("Выполняется парсинг", 'success')
    if client is not None:
        sent_messages = []

        def findWholeWord(word, text):
            pattern = r'(^|[^\w]){}([^\w]|$)'.format(word)
            pattern = re.compile(pattern, re.IGNORECASE)
            matches = re.search(pattern, text)
            return bool(matches)

        while True:
            chats = await client.get_dialogs()
            flash("Чаты успешно подгружены", 'success')
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
                                        found_keyword = findWholeWord(word, message.message)
                                        if found_keyword:
                                            message_text = f"{message.text}\n\n"
                                            message_text += f"Пользователь: <a href='https://t.me/@{message.sender.username}'>{message.sender.username}</a>\nГруппа:"
                                            message_text += f"<a href='https://t.me/c/{message.peer_id.channel_id}'>{chat.title}</a>\n"
                                            message_text += f"Ключ: {word}\n"
                                            message_text += f"<a href='https://t.me/c/{message.peer_id.channel_id}/{message.id}'>Оригинал сообщения</a>"
                                            if not ([f"{search_title}", f"{message.id}"] in sent_messages):
                                                print(message_text)
                                                chat_id = str(settings['chat_id'])
                                                if chat_id[0] != '-':
                                                    chat_id = '-100' + chat_id
                                                else:
                                                    chat_id = '-100' + chat_id[1:]
                                                print(chat_id)
                                                await bot.send_message(chat_id=int(chat_id),
                                                                       text=message_text, parse_mode='HTML')

                                                flash("Сообщение отправлено", 'success')
                                                sent_messages.append([f"{search_title}", f"{message.id}"])
                                                # execute(username=message.sender.username)
                                except Exception as e:
                                    print(f"Error processing {chat.title}: {e}")

            await asyncio.sleep(60)
    else:
        flash("Ошибка подключения клиента", 'warning')


async def run_bot(login):
    account = db_session.query(Users).filter_by(email=login).first()
    all_data = {}
    if account:
        list_groups = []
        list_keywords = []
        chat_id: int

        for setting in account.settings:
            list_groups.append(setting.group)
            list_keywords.append(setting.key)
            chat_id = setting.chat_id

        user_data = {'groups': list_groups, 'keywords': list_keywords,
                     'chat_id': chat_id}
        all_data[account.id] = user_data

        print(all_data)
    else:
        print("User not found.")

    client = TelegramClient(session=f'{account.telegram_account.api_id}.session',
                            api_id=account.telegram_account.api_id,
                            api_hash=account.telegram_account.api_hash)
    string = StringSession.save(client.session)
    try:
        await client.connect()
    except:
        client = TelegramClient(StringSession(string),
                                api_id=account.telegram_account.api_id,
                                api_hash=account.telegram_account.api_hash)
        await client.connect()
    if not await client.is_user_authorized():
        flash("Необходима авторизация телеграм аккаунта", 'warning')
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
        flash("Аккаунт подключен успешно", 'success')
        await exec(client, all_data)
    return
