import asyncio
import re

import dotenv
import os

from telethon.sync import TelegramClient
from aiogram import Bot, Dispatcher
import test_google_dock as tg

dotenv.load_dotenv()

api_id = os.getenv("API_ID_A")
api_hash = os.getenv("API_HASH_A")

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(bot)


async def check_connection():
    try:
        return await bot.get_chat(chat_id=os.getenv('PRIVATE_CHAT_ID'))
    except Exception as e:
        print(f"Bot {bot.id} is not in chat: {e}")


async def check_permission(chat_id):
    try:
        bot_status = await bot.get_chat_member(chat_id=chat_id, user_id=bot.id)
        return bot_status.status == 'administrator'
    except Exception as e:
        print(f"Bot {bot.id} has no required status, current is {bot_status.status}: {e}")


async def get_chat_name(chat_id):
    await check_connection()
    chat_info = await bot.get_chat(chat_id=os.getenv('PRIVATE_CHAT_ID'))
    return chat_info.username


async def bot_send_message(chat_id, message_text):
    await bot.send_message(chat_id=chat_id, text=message_text, parse_mode='HTML')
    # await asyncio.sleep(10)


async def main():
    client = TelegramClient('a', int(api_id), api_hash)
    await client.start()

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
                                            await bot_send_message(int(sheet_data['chat_id']), message_text)
                                            print("Message sended!")
                                            sent_messages.append([f"{search_title}", f"{message.id}"])

                                    # if await check_connection():
                                    #     print("connected!")
                                    #     if await check_permission():
                                    #         print("permission granted!")
                                    #         # await bot_send_message(message_text)
                                    #         print("message sended!")

                            except Exception as e:
                                print(f"Error processing {chat.title}: {e}")
        await asyncio.sleep(60)


if __name__ == '__main__':
    from aiogram import executor as ag_executor

    ag_executor.start(dp, main())
