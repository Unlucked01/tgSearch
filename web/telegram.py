import random

from telethon.errors import SessionPasswordNeededError
from telethon.sync import TelegramClient
import dotenv
import dataclasses


@dataclasses.dataclass
class TelegramUser:
    first_name: str
    username: str
    phone: str


dotenv.load_dotenv()

active_clients = {}


def create_telegram_client(api_id, api_hash, phone, code='', code_hash='', secret_password=''):
    global active_clients
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
    account = client.get_me()

    client.disconnect()
    del active_clients[session_name]
    return {'status': True, 'description': ''}


api_id = 2724818
api_hash = "6c677b0f0e2af14a53cbf0c0eafe5886"
phone = '89870739395'
passw = 'gelo23122003A!'
# response = create_telegram_client(api_id, api_hash, phone)
# print(response)
# if not response['status']:
#     create_telegram_client(api_id, api_hash, phone,
#                            input(response['description']),
#                           response['variables']['phone_code_hash'], passw)
