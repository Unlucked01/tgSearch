from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
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
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=True)
    password = Column(String, nullable=True)
    telegram_account_id = Column(Integer, ForeignKey('telegram_accounts.id'), nullable=True)
    telegram_account = relationship("TelegramAccounts", back_populates="user")
    amocrm_account_id = Column(Integer, ForeignKey('amocrm_accounts.id'), nullable=True)
    amocrm_account = relationship("AmocrmAccounts", back_populates="user")
    settings = relationship("Setting", back_populates="user")
    telegram_session_id = Column(Integer, nullable=True)


class TelegramAccounts(Base):
    __tablename__ = "telegram_accounts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    api_id = Column(Integer)
    api_hash = Column(String)
    phone = Column(String)
    account_id = Column(String)
    user = relationship("Users", back_populates="telegram_account")


class AmocrmAccounts(Base):
    __tablename__ = 'amocrm_accounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String)
    password = Column(String)
    host = Column(String)
    user = relationship("Users", back_populates="amocrm_account")


class Setting(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    group = Column(String)
    key = Column(String)
    chat_id = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("Users", back_populates="settings", foreign_keys="Setting.user_id")


def add_telegram(login, api_id, api_hash, phone, account_id):
    print(login)
    account = dbSession.query(Users).filter_by(email=login).first()
    if account:
        print(account.id)
        telegram_account = TelegramAccounts(api_id=api_id, api_hash=api_hash, phone=phone, account_id=account_id)
        account.telegram_account = telegram_account
        dbSession.add(telegram_account)
        dbSession.commit()
        print("Telegram account added successfully.")
    else:
        print("User not found.")


def add_amo(login, amo_login, amo_password):
    print(login)
    account = dbSession.query(Users).filter_by(email=login).first()
    if account:
        print(account.id)
        amocrm_account = AmocrmAccounts(email=amo_login, password=amo_password)
        account.amocrm_account = amocrm_account
        dbSession.add(amocrm_account)
        dbSession.commit()
        print("Amocrm account added successfully.")
    else:
        print("User not found.")


def add_settings(login, groups, keys, chat_id):
    account = dbSession.query(Users).filter_by(email=login).first()
    if account:
        print(account.id)
        delete_settings_for_user(dbSession, account.id)
        group_value = ', '.join(groups)
        key_value = ', '.join(keys)
        if group_value or key_value:
            settings = Setting(group=group_value, key=key_value, chat_id=chat_id, user=account)
            dbSession.add(settings)
        dbSession.commit()
        print("Settings added successfully.")
    else:
        print("User not found.")


def delete_settings_for_user(session: Session, user_id: int):
    user = session.query(Users).get(user_id)

    if user:
        session.query(Setting).filter_by(user_id=user.id).delete()
        session.commit()
        print(f"Settings for user with id {user_id} deleted successfully.")
    else:
        print(f"User with id {user_id} not found.")


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
dbSession = Session()
