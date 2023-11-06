import asyncio
import os
from telethon.sync import TelegramClient
import dotenv

dotenv.load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")


async def create_telegram_client():
    client = TelegramClient('your_session', int(api_id), api_hash)
    await client.start()
    return client
