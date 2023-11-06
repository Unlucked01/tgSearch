import asyncio
import dotenv
import os


from telethon.sync import TelegramClient
from aiogram import Bot, Dispatcher

dotenv.load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(bot)


async def main():
    client = TelegramClient('your_session', int(api_id), api_hash)
    await client.start()

    keywords = ["нет ссылки", "зум", "задачка"]

    def find_keywords(message):
        found_keyword = [keyword for keyword in keywords if keyword.lower() in message.text.lower()]
        return found_keyword

    chats = await client.get_dialogs()
    for chat in chats:
        if chat.title == "Avatarex Dev":
            messages = await client.get_messages(entity=chat, limit=100)
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
                            await asyncio.sleep(10)
                    except Exception as e:
                        print(f"Error processing {chat.title}: {e}")


if __name__ == '__main__':
    # Run the Telethon and Aiogram main functions
    from aiogram import executor as ag_executor

    ag_executor.start(dp, main())

