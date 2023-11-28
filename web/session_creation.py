from telethon.sync import TelegramClient
from telethon.sessions import StringSession, MemorySession, SQLiteSession

api_id = 24041156
api_hash = '1d7e76a039dfc4280b1c5fbfcdd99f4c'


with TelegramClient(MemorySession(), api_id=api_id, api_hash=api_hash) as client:
    # print(client.session.save())
    client.loop.run_until_complete(client.send_message('me', 'Hi'))



