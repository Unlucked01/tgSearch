from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
import dotenv

dotenv.load_dotenv()
dotenv_values = dotenv.dotenv_values()

Base = declarative_base()

engine = create_engine(
    f'postgresql://{dotenv_values["DB_USER"]}:{dotenv_values["DB_PASSWORD"]}'
    f'@{dotenv_values["DB_HOST"]}:5432/{dotenv_values["DB_NAME"]}'
)


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    telegram_account_id = Column(Integer, ForeignKey('telegram_accounts.id'))
    amocrm_account_id = Column(Integer, ForeignKey('amocrm_accounts.id'))

    # Define the one-to-one relationships
    telegram_account = relationship("TelegramAccounts", uselist=False)
    amocrm_account = relationship("AmocrmAccounts", uselist=False)
    channels_to_post = relationship("ChannelsToPost")
    chats_and_channels = relationship("ChatsAndChannels")


class TelegramAccounts(Base):
    __tablename__ = "telegram_accounts"
    id = Column(Integer, primary_key=True)
    api_id = Column(String)
    api_hash = Column(String)
    session_file_path = Column(String)


class AmocrmAccounts(Base):
    __tablename__ = 'amocrm_accounts'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(String)
    host = Column(String)
    api_hash = Column(String)


class ChannelsToPost(Base):
    __tablename__ = "channels_to_post"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    is_bot_added = Column(Boolean)
    is_bot_has_access = Column(Boolean)
    user_id = Column(Integer, ForeignKey('users.id'))


class ChatsAndChannels(Base):
    __tablename__ = 'chats_and_channels'
    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer)
    last_message_id = Column(Integer)
    link = Column(String)
    is_bot_added = Column(Boolean)
    user_id = Column(Integer, ForeignKey('users.id'))
    messages = relationship("Messages")


class Messages(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    username = Column(String)
    date = Column(DateTime)
    first_name = Column(String)
    last_name = Column(String)
    key = Column(String)
    original_message_url = Column(String)
    chat_and_channel_id = Column(Integer, ForeignKey('chats_and_channels.id'))


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


# user = Users(email="odpash.itmo@gmail.com", password='developer2023')
# session.add(user)
# session.commit()
