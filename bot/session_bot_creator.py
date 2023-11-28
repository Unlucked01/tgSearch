import asyncio
import base64
import logging

import requests
from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types

import os
import dotenv


dotenv.load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()
TOKEN = bot.token

upload_file = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           "..", "testMidjourney/photos/"))

download_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            "..", "testMidjourney/generated_photos/"))

SEND_PHOTO = f'https://api.telegram.org/bot{TOKEN}/sendPhoto'
DOWNLOAD_PHOTO = f'https://api.telegram.org/bot{TOKEN}/getfile?file_id='


async def text_to_image(prompt, message):
    pass


def send_image(base64_image):
    pass


@dp.message()
async def get_message(message: types.Message):
    pass


async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
