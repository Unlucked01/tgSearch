import os
import random
import threading

from telethon import errors
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import MemorySession
from telethon.sync import TelegramClient
import dotenv
import dataclasses
import asyncio
import re
from aiogram import Bot, Dispatcher
import bot.test_google_dock as tg
from bot.aiogram_bot import send_message, get_message
from bot.session_bot_creator import bot
from misc.models import TelegramAccounts, Users, dbSession as db_session
from bot.amocrm import execute

dotenv.load_dotenv()
active_clients = {}
Bot = Bot(os.getenv('BOT_TOKEN'))
dp = Dispatcher()

BOT_TOKEN = os.getenv('BOT_TOKEN_REQ')

UPDATES_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates'
SEND_MESSAGE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'


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


async def exec(client, all_data):
    if client is not None:
        sent_messages = []

        def findWholeWord(word, text):
            pattern = r'(^|[^\w]){}([^\w]|$)'.format(word)
            pattern = re.compile(pattern, re.IGNORECASE)
            matches = re.search(pattern, text)
            return bool(matches)

        while True:
            chats = await client.get_dialogs()
            for account_id, settings in all_data.items():
                for chat in chats:
                    for search_title in settings['groups']:
                        if findWholeWord(search_title, chat.title):
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
                                                id = settings['chat_id']
                                                if id[0] != '-':
                                                    id = '-' + id
                                                await Bot.send_message(chat_id=int(id),
                                                                       text=message_text, parse_mode='HTML')
                                                print("Message sended!")
                                                sent_messages.append([f"{search_title}", f"{message.id}"])
                                                # execute(username=message.sender.username)
                                except Exception as e:
                                    print(f"Error processing {chat.title}: {e}")

            await asyncio.sleep(60)
    else:
        print("No client")


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
    await client.connect()
    if not await client.is_user_authorized():
        await client.send_code_request(phone=account.telegram_account.phone)
        send_message(account.telegram_account.account_id, "Введите код доступа в формате\n"
                                                          "3 цифры . 2 оставшиеся\n"
                                                          "Например -> '123.45': ")
        await asyncio.sleep(20)
        code = get_message(account.telegram_account.account_id).replace(".", '')
        print(code)
        if code:
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
    else:
        print("connected")
        await client.connect()
        await exec(client, all_data)
    return

