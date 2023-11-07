import asyncio
import re

import dotenv
import os


from telethon.sync import TelegramClient
from aiogram import Bot, Dispatcher

dotenv.load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(bot)


async def check_connection():
    try:
        return await bot.get_chat(chat_id=os.getenv('PRIVATE_CHAT_ID'))
    except Exception as e:
        print(f"Bot {bot.id} is not in chat: {e}")


async def check_permission():
    try:
        bot_status = await bot.get_chat_member(chat_id=os.getenv('PRIVATE_CHAT_ID'), user_id=bot.id)
        return bot_status.status == 'administrator'
    except Exception as e:
        print(f"Bot {bot.id} has no required status, current is {bot_status.status}: {e}")


async def get_chat_name(chat_id):
    await check_connection()
    chat_info = await bot.get_chat(chat_id=os.getenv('PRIVATE_CHAT_ID'))
    return chat_info.username


async def bot_send_message(message_text):
    await bot.send_message(chat_id=os.getenv('PRIVATE_CHAT_ID'), text=message_text, parse_mode='HTML')
    await asyncio.sleep(10)


async def main():
    client = TelegramClient('your_session', int(api_id), api_hash)
    await client.start()

    keywords = ["тех задание", "зум", "задачка"]

    def find_keywords(message):
        for keyword in keywords:
            if keyword.lower() in message.message.lower():
                return message.message.lower()
        return None

        # return found_keywords

    chats = await client.get_dialogs()
    for chat in chats:
        if chat.title == "Avatarex Dev":
            messages = await client.get_messages(entity=chat, limit=100)
            for message in messages:
                try:
                    found_keywords = find_keywords(message)
                    print(found_keywords)
                    if found_keywords:
                        keyword_str = ", ".join(found_keywords)
                        message_text = f"{message.text}\n\n"
                        message_text += f"Пользователь: ({message.sender.username}), {message.sender.first_name}\nГруппа: "
                        message_text += f"<a href='https://t.me/{chat.title.replace(' ', '_')}'>{chat.title}</a>\n"
                        message_text += f"Ключ: {keyword_str}\n"
                        message_text += f"<a href='https://t.me/{chat.title.replace(' ', '_')}/{message.id}'>Оригинал сообщения</a>"

                        if await check_connection():
                            print("connected!")
                            if await check_permission():
                                print("permission granted!")
                                # await bot_send_message(message_text)
                                print("message sended!")

                except Exception as e:
                    print(f"Error processing {chat.title}: {e}")


if __name__ == '__main__':
    from aiogram import executor as ag_executor

    ag_executor.start(dp, main())

