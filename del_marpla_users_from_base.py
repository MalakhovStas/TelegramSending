from typing import Tuple
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
                data = tuple(user[0] for user in self.cursor.fetchall())
            return data

    def delete_user(self, user_id: int) -> None:
        with self.database:
            self.cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            self.database.commit()


db_chat_parsing = Database('chats_parsing_base.db')
marpla_db = Database('marpla_db.db')

urs = marpla_db.select_user()
num_del = 0

for i_id in urs:
    if db_chat_parsing.select_user(i_id):
        db_chat_parsing.delete_user(i_id)
        num_del += 1
print('Удалённых пользователей:', num_del)
print('В базе осталось:', len(db_chat_parsing.select_user()))


