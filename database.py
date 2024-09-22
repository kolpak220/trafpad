import sqlite3
import math
import random
import shutil
import os
import time
import string
from datetime import datetime

def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits  # Строка с буквами и цифрами
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

# Преобразование полученного списка в словарь
def dict_factory(cursor, row):
    save_dict = {}

    for idx, col in enumerate(cursor.description):
        save_dict[col[0]] = row[idx]

    return save_dict


# Форматирование запроса без аргументов
def query(sql, parameters: dict):
    if "XXX" not in sql: sql += " XXX "
    values = ", ".join([
        f"{item} = ?" for item in parameters
    ])
    sql = sql.replace("XXX", values)

    return sql, list(parameters.values())


# Форматирование запроса с аргументами
def query_args(sql, parameters: dict):
    sql = f"{sql} WHERE "

    sql += " AND ".join([
        f"{item} = ?" for item in parameters
    ])

    return sql, list(parameters.values())


def get_ref(bot_link: str):
    with sqlite3.connect(path_db) as con:
        con.row_factory = sqlite3.Row  # Позволяет обращаться к колонкам через названия
        cur = con.cursor()

        # Запрос на выборку пользователя по его bot_link
        cur.execute("SELECT ref_link FROM users WHERE bot_link = ?", (bot_link,))
        user = cur.fetchone()  # Получаем данные пользователя
        
        return user['ref_link'] if user else None

# Функция для проверки пользователя в базе данных
def get_user_data(user_id: int):
    with sqlite3.connect(path_db) as con:
        con.row_factory = sqlite3.Row  # Позволяет обращаться к колонкам через названия
        cur = con.cursor()

        # Запрос на выборку пользователя по его id
        cur.execute("SELECT ref_link, bot_link FROM users WHERE id = ?", (user_id,))
        user = cur.fetchone()  # Получаем данные пользователя
        
        return dict(user) if user else None
# Добавление пользователя в базу данных
def add_user(user_id: int, ref_link: str):
    with sqlite3.connect(path_db) as con:
        bot_link = generate_random_string(20)
        con.row_factory = dict_factory
        cur = con.cursor()
        
        # Время регистрации пользователя
        reg_date = datetime.today().replace(microsecond=0)
        
        cur.execute(
            "INSERT INTO users (id, ref_link, bot_link, reg_date) VALUES (?, ?, ?, ?)",
            (user_id, ref_link, bot_link, reg_date)
        )
        con.commit()
        print(f"User {user_id} added to the database.")


# Удаление пользователя по id
def delete_user(user_id: int):
    with sqlite3.connect(path_db) as con:
        con.row_factory = dict_factory
        cur = con.cursor()
        
        cur.execute(
            "DELETE FROM users WHERE id = ?",
            (user_id,)
        )
        con.commit()
        print(f"User {user_id} deleted from the database.")

# Изменение данных пользователя по id (например, обновление ref_link или bot_link)
def update_user(user_id: int, new_data: dict):
    with sqlite3.connect(path_db) as con:
        con.row_factory = dict_factory
        cur = con.cursor()
        
        # Формирование запроса на изменение данных
        sql, params = query("UPDATE users SET XXX", new_data)
        sql += " WHERE id = ?"
        params.append(user_id)
        
        cur.execute(sql, params)
        con.commit()
        print(f"User {user_id} updated.")

#         # Пример использования этих функций
# if __name__ == "__main__":
#     # Добавить пользователя
#     add_user(12345, "https://example.com/ref123", "https://t.me/example_bot")

#     # Обновить пользователя
#     update_user(12345, {"ref_link": "https://newref.com", "bot_link": "https://t.me/new_bot"})

#     # Удалить пользователя
#     delete_user(12345)


def create_backup(file_path, backup_dir):
    try:
        timestamp = int(time.time())
        file_name = os.path.basename(file_path)
        backup_filename = f"{timestamp}_{file_name}"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        shutil.copy(file_path, backup_path)
        return backup_path
    except Exception as e:
        print(f"Failed to create backup: {e}")

def delete_oldest_backup(backup_dir, max_backups=3):
    try:
        if not os.path.exists(backup_dir):
            print(f"Backup directory '{backup_dir}' does not exist.")
            return
        
        backups = os.listdir(backup_dir)
        
        if len(backups) <= max_backups:
            return
        
        backups = [os.path.join(backup_dir, backup) for backup in backups]
        backups.sort(key=os.path.getctime)
        
        # Удаляем старейшую версию (первый элемент в списке)
        os.remove(backups[0])
    except Exception as e:
        print(f"Failed to delete oldest backup: {e}")

def db_backup(file_path, backup_dir):
    try:
        # Создаем новую резервную копию
        backup_path = create_backup(file_path, backup_dir)

        # Удаляем старейшую версию (если есть)
        delete_oldest_backup(backup_dir)
        
        print('Backup was saved')
        
        return backup_path
    except Exception as e:
        print(f"Backup failed: {e}")

path_dbBackup = 'data/DBbackups'
path_db = 'database.db'

# Создание Базы Данных
def create_db():
    with sqlite3.connect(path_db) as con:
        con.row_factory = dict_factory

        # Пользователи
        if len(con.execute("PRAGMA table_info(users)").fetchall()) == 5:
            print("database was found (users | 1/1)")
        else:
            con.execute("CREATE TABLE users("
                        "increment INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "id INTEGER,"
                        "ref_link TEXT,"
                        "bot_link TEXT,"
                        "reg_date TIMESTAMP)")
            

            print("database was not found (users | 1/11), creating...")


            con.commit()
                # Закрываем соединение с оригинальной базой данных
        



        db_backup(path_db, path_dbBackup)