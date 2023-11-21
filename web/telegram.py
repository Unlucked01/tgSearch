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

from bot.amocrm import execute

dotenv.load_dotenv()
active_clients = {}
client = None
Bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(Bot)


def create_telegram_client(api_id, api_hash, phone, code='', code_hash='', secret_password=''):
    global active_clients, client
    session_name = str(api_id)
    if session_name in active_clients.keys():
        client = active_clients[session_name]
    else:
        client = TelegramClient(session_name, int(api_id), api_hash)
        client.connect()
        active_clients[session_name] = client

    if session_name in active_clients.keys():
        client = active_clients[session_name]

    if not client.is_user_authorized():
        if code == '':
            try:
                phone_code_hash = client.send_code_request(phone).phone_code_hash
            except:
                pass
            active_clients[client] = client
            return {'status': False, 'description': 'Please, write sms code',
                    'variables': {'phone_code_hash': phone_code_hash}}
        try:
            client.sign_in(phone=phone, code=code, phone_code_hash=code_hash)
        except SessionPasswordNeededError as err:
            client.sign_in(password=secret_password)
    else:
        from aiogram import executor as ag_executor
        ag_executor.start(dp, run_bot())

    client.disconnect()

    del active_clients[session_name]
    return {'status': True, 'description': ''}


async def run_bot():
    if client is not None:
        sent_messages = []

        def findWholeWord(word, text):
            pattern = r'(^|[^\w]){}([^\w]|$)'.format(word)
            pattern = re.compile(pattern, re.IGNORECASE)
            matches = re.search(pattern, text)
            return bool(matches)

        while True:
            chats = await client.get_dialogs()
            sheet_dict = tg.read()
            for sheet_name, sheet_data in sheet_dict.items():
                print(sheet_name)
                for chat in chats:
                    for search_title in sheet_data['titles']:
                        if chat.title.lower().replace(" ", "_") == search_title.lower().replace(" ", "_"):
                            messages = await client.get_messages(entity=chat, limit=100)
                            for message in messages:
                                try:
                                    for word in sheet_data['keywords']:
                                        found_keyword = findWholeWord(word, message.message)
                                        if found_keyword:
                                            message_text = f"{message.text}\n\n"
                                            message_text += f"Пользователь: ({message.sender.username})\nГруппа:"
                                            message_text += f"<a href='https://t.me/c/{message.peer_id.channel_id}'>{chat.title}</a>\n"
                                            message_text += f"Ключ: {word}\n"
                                            message_text += f"<a href='https://t.me/c/{message.peer_id.channel_id}/{message.id}'>Оригинал сообщения</a>"
                                            if not ([f"{search_title}", f"{message.id}"] in sent_messages):
                                                print(sheet_data['chat_id'])
                                                await Bot.send_message(chat_id=int(sheet_data['chat_id']), text=message_text, parse_mode='HTML')
                                                print("Message sended!")
                                                sent_messages.append([f"{search_title}", f"{message.id}"])
                                                execute(message.sender.username)
                                except Exception as e:
                                    print(f"Error processing {chat.title}: {e}")

            await asyncio.sleep(60)



# api_id = 24041156
# api_hash = "1d7e76a039dfc4280b1c5fbfcdd99f4c"
# phone = '89273683256'
# passw = 'Hochupitsu01!'
# response = create_telegram_client(api_id, api_hash, phone)
# print(response)
#
# if not response['status']:
#     create_telegram_client(api_id, api_hash, phone,
#                            input(response['description']),
#                           response['variables']['phone_code_hash'], passw)
