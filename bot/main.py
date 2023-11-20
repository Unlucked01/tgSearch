# main.py

import asyncio

from telegram_client import create_telegram_client
from aiogram_bot import bot, dp
import os
import re


async def main():
    telegram_client = await create_telegram_client()
    # "тех задание", "зум", "задачка"
    keywords = []
    while True:
        temp = input("Введите слова для поиска (stop для выхода): ")
        if temp == "stop":
            break
        keywords.append(temp)
    print(keywords)
    search_title = input("Название группы для поиска: ")

    def find_keywords(message):
        found_keywords = [keyword for keyword in keywords if
                          re.search(fr'\b{re.escape(keyword)}\b', message.text, re.IGNORECASE)]
        return found_keywords

    chats = await telegram_client.get_dialogs()

    for chat in chats:
        if chat.title == search_title:
            messages = await telegram_client.get_messages(entity=chat, limit=100)
            for message in messages:
                if message:
                    try:
                        found_keywords = find_keywords(message)
                        if found_keywords:
                            keyword_str = ", ".join(found_keywords)
                            message_text = f"{message.text}\n\n"
                            message_text += f"Пользователь: ({message.sender.username}), {message.sender.first_name}\nГруппа: "
                            message_text += f"<a href='https://t.me/{chat.title.replace(' ', '_')}'>{chat.title}</a>\n"
                            message_text += f"Ключ: {keyword_str}\n"
                            message_text += f"<a href='https://t.me/{chat.title.replace(' ', '_')}/{message.id}'>Оригинал сообщения</a>"

                            await bot.send_message(chat_id=os.getenv('PRIVATE_CHAT_ID'), text=message_text,
                                                   parse_mode='HTML')
                    except Exception as e:
                        print(f"Error processing {chat.title}: {e}")


if __name__ == '__main__':
    from aiogram import executor as ag_executor

    ag_executor.start(dp, main())
