import os
from aiogram import Bot, Dispatcher
import dotenv

dotenv.load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(bot)
