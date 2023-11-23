import os
import random
import threading

from telethon.errors import SessionPasswordNeededError
from telethon.sync import TelegramClient
import dotenv
import dataclasses
import asyncio
import re
from aiogram import Bot, Dispatcher
import bot.test_google_dock as tg
from misc.models import dbSession as db_session, TelegramAccounts, Users

from bot.amocrm import execute

dotenv.load_dotenv()
active_clients = {}
client: TelegramClient
Bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(Bot)


async def create_telegram_client(api_id, api_hash, phone='', code='', code_hash='', secret_password=''):
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

    if not (await client.is_user_authorized()):
        if code == '':
            try:
                phone_code_hash = await client.send_code_request(phone).phone_code_hash
            except Exception as e:
                print(e)
            active_clients[client] = client
            return {'status': False, 'description': 'Please, write sms code',
                    'variables': {'phone_code_hash': phone_code_hash}}
        try:
            await client.sign_in(phone=phone, code=code, phone_code_hash=code_hash)
        except SessionPasswordNeededError as err:
            await client.sign_in(password=secret_password)

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

    # client = TelegramClient(f"./{account.telegram_account.api_id}.session",
    #                         int(account.telegram_account.api_id),
    #                         account.telegram_account.api_hash)
    # await client.connect()
    print(await client.is_user_authorized())
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
