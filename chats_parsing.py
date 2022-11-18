from typing import List, Tuple
from telethon.sync import TelegramClient, events
from telethon.tl.custom.dialog import Dialog
from telethon.tl.types import User
from progress.bar import ChargingBar
from colorama import init, Fore, deinit
from collections import namedtuple
import sqlite3


class Database:
    """Класс описывающий работу приложения с базой данных"""
    def __init__(self, path_db):
        self.database = sqlite3.connect(path_db)
        self.cursor = self.database.cursor()

    def create_table(self) -> None:
        with self.database:
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                                    user_id INTEGER PRIMARY KEY NOT NULL,
                                    name TEXT,
                                    username TEXT,
                                    phone TEXT)""")
            self.database.commit()

    def select_user(self, user_id: int | None = None) -> Tuple | int | None:
        with self.database:
            if user_id:
                self.cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
                data = self.cursor.fetchone()
            else:
                self.cursor.execute("SELECT user_id FROM users")
                data = len(self.cursor.fetchall())
            return data

    def insert_user(self, user_id: int, name: str, username: str, phone: str) -> str:
        with self.database:
            self.cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            if not self.cursor.fetchone():
                self.cursor.execute("INSERT INTO users(user_id, name, username, phone) VALUES"
                                    "(?, ?, ?, ?)", (user_id, name, username, phone))
                self.database.commit()
                res = 'ok'
            else:
                res = 'bad'
            return res


def dialog_parsing(client):
    chats = list()
    dialogs = client.get_dialogs()
    bar = ChargingBar(f'{Fore.GREEN}Парсинг диалогов:', suffix=f'%(percent)d%%', max=len(dialogs))
    for dialog in dialogs:
        bar.next()
        if dialog.is_group and dialog.is_channel:
            chats.append(dialog)

    print(f'  {Fore.CYAN}Найдено: {len(chats)} чатов{Fore.RESET}\n')
    bar.finish()

    return chats


def chat_parsing(client, chat):
    result = list()
    Tg_User = namedtuple('Tg_User', ('user_id', 'name', 'username', 'phone'))

    print(f'{Fore.GREEN}Загрузка чата: "{Fore.MAGENTA}{chat.name}{Fore.GREEN}"')
    users = client.get_participants(chat)
    bar = ChargingBar(f'Парсинг:', suffix=f'%(percent)d%%', max=len(users))
    for usr in users:
        if not usr.deleted and not usr.bot:
            result.append(Tg_User(usr.id, (usr.first_name if usr.first_name else "" + ' ' + usr.last_name if usr.last_name else ""),
                          usr.username, usr.phone))
        bar.next()
    print(f'{Fore.CYAN} в чате: {len(users)} пользователей{Fore.RESET}')
    bar.finish()

    return result


def add_users_in_db(chat_users):
    num = []
    bar = ChargingBar(f'{Fore.GREEN}Запись в БД:', suffix=f'%(percent)d%%', max=len(chat_users))
    for usr in chat_users:
        bar.next()
        num.append(db.insert_user(usr.user_id, usr.name, usr.username, usr.phone))
    print(f'{Fore.CYAN} добавлено: {num.count("ok")}, повторов: {num.count("bad")}, '
          f'всего в БД: {db.select_user()} записей{Fore.RESET}\n')
    bar.finish()


init()
db = Database('chats_parsing_base.db')

#Аккаунт Semen Slepakon
api_id = 20088035
api_hash = '6fc88e4abb6958ddc1a557c3c425d267'
phone = '+79163678748'
secret_code = '44492'
db.create_table()

with TelegramClient('name', api_id, api_hash) as client:
    print('Парсер Телеграм чатов!\n')
    client.send_message('me', 'Парсер Телеграм чатов!\n')
    chats = dialog_parsing(client=client)

    chat_name = input('Введите название чата или нажмите ENTER для парсинга всех чатов: ')
    for chat in chats:
        if chat_name:
            if chat.name == chat_name:
                add_users_in_db(chat_parsing(client=client, chat=chat))
                break
        else:
            add_users_in_db(chat_parsing(client=client, chat=chat))

    print('\nПарсинг чатов окончен')
    client.run_until_disconnected()

# Поисковая выдача товара на сайте Wildberries