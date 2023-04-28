import sqlite3
import calendar
import time
from config import *
from urls import *

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


# функция обработки БД
class Dbase():
    # проверка в базе
    def check_user(self, telegram_id):
        if telegram_id != None:
            conn = sqlite3.connect(dbpath)
            c = conn.cursor()
            text = c.execute(f"SELECT * FROM users WHERE telegram_id = '{telegram_id}'").fetchall()
            conn.commit()
            conn.close()
            return text
        #print('Вас нет в базе')

    # добавить пользователя в базу
    def add_user(self, telegram_id, telegram_phone, telegram_name, telegram_nick, more_info=None):
        # Current GMT time in a tuple format
        current_GMT = time.gmtime()
        # ts stores timestamp
        ts = calendar.timegm(current_GMT)
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute(f"INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", (telegram_id, telegram_phone, telegram_name, telegram_nick, ts, more_info))
        conn.commit()
        conn.close()
        #print('Записано в базу')

    # удалить из базы
    def del_user(self, telegram_id):
        if telegram_id != None:
            conn = sqlite3.connect(dbpath)
            c = conn.cursor()
            c.execute(f"DELETE FROM users WHERE telegram_id = '{telegram_id}'")
            conn.commit()
            conn.close()
            #print('Вы удалены из базы')

    # добавить ID файла в базу
    def add_ID(self, message_id, file_id, file_name):
        # Current GMT time in a tuple format
        current_GMT = time.gmtime()
        # ts stores timestamp
        ts = calendar.timegm(current_GMT)
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute(f"INSERT INTO idfile VALUES (?, ?, ?, ?)", (message_id, file_id, file_name, ts))
        conn.commit()
        conn.close()
        #print('Записано в базу')

    # получить список файлов из базы
    def get_files(self):
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        text = c.execute(f"SELECT * FROM idfile").fetchall()
        conn.commit()
        conn.close()
        return text

    # работа с родителем для организации работы кнопки "назад"
    def read_sqlite_table(self, option, parent='start'):
        try:
            #print(option)
            menulist = []
            sqlite_connection = sqlite3.connect(dbpath)
            cursor = sqlite_connection.cursor()
            sqlite_select_query = """SELECT * from menu"""
            cursor.execute(sqlite_select_query)
            records = cursor.fetchall()
            for row in records:
                menulist.append(row[0])
                menu_list = eval(row[1])
                if option in menu_list:
                    parent = row[0]
                    #print(parent)
            cursor.close()
            return [menulist, parent]

        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
        finally:
            if sqlite_connection:
                sqlite_connection.close()
                #print("Соединение с SQLite закрыто")


    def get_menu(self, option):
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        text = c.execute(f"SELECT * FROM menu WHERE callback_button = '{option}'").fetchall()
        conn.commit()
        conn.close()
        return text


db = Dbase()


# построение меню с помощью inlinekeyboard
class Keyboard():
    def inlinekey(self, option=None, parent=None):
        source_inline_menu = InlineKeyboardMarkup(row_width=2)
        menu = db.get_menu(option)[0]
        #print(parent)
        for x in eval(menu[1]):
            categ_1_button = InlineKeyboardButton(f'{x}', callback_data=f'{x}')
            source_inline_menu.add(categ_1_button)
        if option in url:
            categ_1_button = InlineKeyboardButton(f'Ссылка', url=f'{url[option]}')
            source_inline_menu.add(categ_1_button)
        if option not in ['start', 'Посмотрел✊', 'Изучил😉']:
            categ_1_button = InlineKeyboardButton(f'⬅️Назад', callback_data=f'{parent}')
            source_inline_menu.add(categ_1_button)
        return source_inline_menu




markup_request = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Отправить свой контакт ☎️', request_contact=True))
markup_del = ReplyKeyboardRemove()
