import os
import random
import threading

from pyrogram import Client
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
from misc.models import dbSession as db_session, TelegramAccounts, Users

from bot.amocrm import execute

dotenv.load_dotenv()
active_clients = {}
Bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(Bot)

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


async def run_bot(login):
    account = db_session.query(Users).filter_by(email=login).first()
    if account:
        all_data = {}
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

    # client = Client(os.path.join(os.path.dirname(__file__),
    #                              "../sessions/",
    #                              str(account.telegram_session_id)))
    client = Client(os.path.join(os.path.dirname(__file__),
                    "../sessions/test.session"),
                    api_id=24041156,
                    api_hash='1d7e76a039dfc4280b1c5fbfcdd99f4c')
    await client.start()
    with client:
        session = await client.export_session_string()
        print(session)
    # client = TelegramClient(session=f"{account.telegram_account.api_id}.session",
    #                         api_id=account.telegram_account.api_id,
    #                         api_hash=account.telegram_account.api_hash)

    return
    try:
        if not await client.is_user_authorized():
            await client.send_code_request(phone=account.telegram_account.phone)
            send_message(account.telegram_account.account_id, "Введите код подтверждения: ")
            await asyncio.sleep(8)  # Adjust the sleep duration as needed
            code = get_message(account.telegram_account.account_id)
            print(code['text'])
            return
            if code:
                try:
                    # Try to sign in with the obtained code
                    result = await client.sign_in(phone=account.telegram_account.phone, code=code)
                    print(result.stringify())

                except errors.rpcerrorlist.PhoneCodeExpiredError:
                    # Handle PhoneCodeExpiredError by continuing the loop
                    print("The confirmation code has expired. Requesting a new one.")
                    await client.send_code_request(phone=account.telegram_account.phone)
                    send_message(account.telegram_account.account_id, "Введите новый код подтверждения: ")


    except:
        pass

    return

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
                print(account_id)
                for chat in chats:
                    for search_title in settings['groups']:
                        print(search_title)
                        if chat.title.lower().replace(" ", "_") == search_title.lower().replace(" ", "_"):
                            messages = await client.get_messages(entity=chat, limit=100)
                            for message in messages:
                                try:
                                    for word in settings['keywords']:
                                        print(word)
                                        found_keyword = findWholeWord(word, message.message)
                                        if found_keyword:
                                            message_text = f"{message.text}\n\n"
                                            message_text += f"Пользователь: <a href='https://t.me/@{message.sender.username}'>{message.sender.username}</a>\nГруппа:"
                                            message_text += f"<a href='https://t.me/c/{message.peer_id.channel_id}'>{chat.title}</a>\n"
                                            message_text += f"Ключ: {word}\n"
                                            message_text += f"<a href='https://t.me/c/{message.peer_id.channel_id}/{message.id}'>Оригинал сообщения</a>"
                                            if not ([f"{search_title}", f"{message.id}"] in sent_messages):
                                                print(settings['chat_id'])
                                                await Bot.send_message(chat_id=int(settings['chat_id']),
                                                                       text=message_text, parse_mode='HTML')
                                                print("Message sended!")
                                                sent_messages.append([f"{search_title}", f"{message.id}"])
                                                # execute(username=message.sender.username)
                                except Exception as e:
                                    print(f"Error processing {chat.title}: {e}")

            await asyncio.sleep(60)
    else:
        print("No client")

# api_id = 24041156
# api_hash = "1d7e76a039dfc4280b1c5fbfcdd99f4c"
# phone = '89273683256'
# passw = ''
# response = create_telegram_client(api_id, api_hash, phone)
# print(response)
#
# if not response['status']:
#     create_telegram_client(api_id, api_hash, phone,
#                            input(response['description']),
#                           response['variables']['phone_code_hash'], passw)
