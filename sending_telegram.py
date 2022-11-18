import datetime
import os
import random
import time
from collections import namedtuple
from typing import List, Tuple

# https://docs.telethon.dev/en/stable/ - документация
from telethon.errors import PeerFloodError, SessionPasswordNeededError
from telethon.sync import TelegramClient, events
from telethon.tl.custom.dialog import Dialog
from telethon.tl.types import User
from colorama import init, Fore, deinit

import sqlite3


class Database:
    """Класс описывающий работу приложения с базой данных"""
    def __init__(self, path_db):
        self.database = sqlite3.connect(path_db)
        self.cursor = self.database.cursor()

    def select_user(self, user_id: int | None = None, rand: bool = False) -> Tuple | int | None:
        with self.database:
            if rand:
                Contact = namedtuple('Contact', ('user_id_', 'username_'))
                self.cursor.execute("SELECT user_id, username FROM users ORDER BY RANDOM() LIMIT 1")
                data = Contact(*self.cursor.fetchone())
            elif user_id:
                self.cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
                data = self.cursor.fetchone()
            else:
                self.cursor.execute("SELECT username FROM users")
                data = tuple(user[0] for user in self.cursor.fetchall())
            return data

    def delete_user(self, user_id: int) -> None:
        with self.database:
            self.cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            self.database.commit()


# https://my.telegram.org/auth - для регистрации приложения
api_id = 20088035
my_phone = '+79163678748'
api_hash = '6fc88e4abb6958ddc1a557c3c425d267'

accounts = ({'name': 'Andrei_Ivanov', 'phone': '+79774847409', 'ban': False},
            {'name': 'Semen_Slepakov', 'phone': '+79163678748', 'ban': False},
            {'name': 'User_Userov', 'phone': '+79627543061', 'ban': False},)

db = Database('free_marpla.db') #192145

message = '@WBbisnesBot - удобный телеграмм бот для экономии рекламного бюджета в личном кабинете WB. ' \
          'Показывает РЕАЛЬНЫЕ рекламные ставки в поиске и в карточке товара'

num_sending = 0
non_username = 0
while not any(acct.get('ban') for acct in accounts):
    for account in accounts:
        if account.get('ban'):
            print(f'{Fore.RED}Аккаунт {Fore.YELLOW}{account.get("name")}{Fore.RED} - забанен!!!{Fore.RESET}')
            time.sleep(1)
            continue
        # with TelegramClient(account.get('name'), api_id, api_hash) as client:
        client = TelegramClient(account.get('name'), api_id, api_hash)
        client.connect()
        if not client.is_user_authorized():

            # запрашиваем однаразовый код
            client.send_code_request(account.get('phone'))

            try:
                client.sign_in(account.get('phone'), input(f'{account.get("name")} Введите секретный код: '))

            # дополнительный пароль двухфакторной авторизации если необходимо
            except SessionPasswordNeededError:
                 client.sign_in(password=input("Enter password: "))

        client.send_message('me', f'Старт {datetime.datetime.now()}')
        for _ in range(5):
            contact = db.select_user(rand=True)

            if not contact.username_:
                db.delete_user(user_id=contact.user_id_)
                non_username += 1
                continue
            print("Отправляю сообщение: ", contact.username_)
            try:
                # отправляем сообщение
                client.send_message(contact.username_, message)

            # Возможно словить Flood Error, поэтому лучше сразу прекратить спам и разорвать связь
            except PeerFloodError:
                print(f"{Fore.RED}Ошибка PeerFloodError ->"
                      f" аккаунт {Fore.YELLOW}{account.get('name')}{Fore.RED} в карантин{Fore.RESET}")
                account['ban'] = True
                break
            except Exception as exc:
                print("Ошибка:", exc, "\n Ещё попытка...")
                continue
            else:
                num_sending += 1
                db.delete_user(user_id=contact.user_id_)
                delay = random.randint(15, 25)
                print(f"Задержка {delay} сек")  # со ссылкой получиться отправить 10 сообщ, без 40
                time.sleep(delay)

        client.disconnect()
        os.remove(f'{account.get("name")}.session')


input(f'Отправлено: {num_sending}, удалено: {num_sending+non_username}, из них без username: {non_username}'
      '\nВсе аккаунты в карантине, для завершения программы нажмите Enter')
exit()

# 1) Andrei Ivanov, +7 (977) 484-7409 = (17.11 - 10)
# 2) Semen Slepakov, +7 (916) 367-8748 = (17.11 - 2)


    # client.send_message('tech_business_support', 'Любой текст11111') #id без кавычек, ссылка и юзернаме в кавычках

    # chats: List[Dialog] = [dialog for dialog in client.get_dialogs() if dialog.is_group and dialog.is_channel]
    # print([cht.entity.participants_count for cht in chats])
    # users = [user for user in client.get_participants(chats[19])]

    # @client.on(events.NewMessage(pattern='(?i).*'))
    # async def handler(event):
    #     await event.reply('Hey!')

# User(id=5709028719,
#      is_self=True,
#      contact=False,
#      mutual_contact=False,
#      deleted=False, bot=False,
#      bot_chat_history=False,
#      bot_nochats=False,
#      verified=False,
#      restricted=False,
#      min=False,
#      bot_inline_geo=False,
#      support=False,
#      scam=False,
#      apply_min_photo=True,
#      fake=False,
#      bot_attach_menu=False,
#      premium=False,
#      attach_menu_enabled=False,
#      access_hash=-6434398034508119334,
#      first_name='Semen',
#      last_name='Slepakov',
#      username='semen_slp',
#      phone='79163678748',
#      photo=None,
#      status=UserStatusOnline(expires=datetime.datetime(2022, 11, 17, 10, 7, 36, tzinfo=datetime.timezone.utc)),
#      bot_info_version=None, restriction_reason=[], bot_inline_placeholder=None, lang_code=None)