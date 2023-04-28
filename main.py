# -*- coding: utf-8 -*-
import config
from logging.handlers import RotatingFileHandler
import logging
from utils import TestStates

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from classes import *
from text import *
from urls import *

kb = Keyboard()
db = Dbase()

bot = Bot(token=config.token)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


# Пишем лог в одноименный файл (пути в конфиге для кроссплатформенной настройки)
logging.basicConfig(
        handlers=[RotatingFileHandler(config.bot_log, maxBytes=1000000, backupCount=1, encoding='utf-8')],
        level=logging.DEBUG,
        format="%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s",
        datefmt='%Y-%m-%dT%H:%M:%S')


def create_table():
    # Создать таблицу для пользователей
    conn = sqlite3.connect('/usr/onperspektiva24.com_infobot/main.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS some_info(
       id INT PRIMARY KEY,
       text TEXT);
    """)
    conn.commit()
    conn.close()


def update_promo(promo_text):
    conn = sqlite3.connect('/usr/onperspektiva24.com_infobot/main.db')
    c = conn.cursor()
    c.execute(f"UPDATE some_info SET text = '{promo_text}' WHERE id = 1")
    conn.commit()
    conn.close()


def get_promo():
    conn = sqlite3.connect('/usr/onperspektiva24.com_infobot/main.db')
    c = conn.cursor()
    promo = c.execute(
        f"SELECT text FROM some_info WHERE id = 1").fetchone()
    conn.close()
    print(promo)
    return promo[0]

# Начало взаимодействия с ботом командой start или s
@dp.message_handler(commands=['start', 's'])
async def start_handler(message):
    state = dp.current_state(user=message.from_user.id)
    #await bot.send_message(message.from_user.id, 'Чтобы воспользоваться ботом введите код-доступа')
    #await state.set_state(TestStates.all()[1])
    # если пользователя нет в базе, запрашиваем контакт, если есть - отправляем в главное меню
    if db.check_user(message.from_user.id):
        del_link = await bot.send_message(message.from_user.id, f"{messages_text['start']}", reply_markup=kb.inlinekey(option='start'))
    else:
        del_link = await bot.send_message(message.from_user.id, f"Пришлите свой контакт", reply_markup=markup_request)
    # храним переменные ссылки (для удаления) и родителя (для кнопки назад)
    await state.update_data(del_link=del_link, parent_back='start')


@dp.message_handler(lambda message: message.text and get_promo() in message.text, state=TestStates.TEST_STATE_1)
async def text_handler(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    # Если user еще не использовал этого бота
    if db.check_user(message.from_user.id):
        del_link = await bot.send_message(message.from_user.id, f"{messages_text['start']}",
                                          reply_markup=kb.inlinekey(option='start'))
    else:
        del_link = await bot.send_message(message.from_user.id, f"Пришлите свой контакт", reply_markup=markup_request)
        # храним переменные ссылки (для удаления) и родителя (для кнопки назад)
    await state.reset_state()
    await state.update_data(del_link=del_link, parent_back='start')


@dp.message_handler(commands=['promo'], state='*')
async def promo_handler(message):
    state = dp.current_state(user=message.from_user.id)
    promo = get_promo()
    await bot.send_message(message.from_user.id, f'Введите новый промокод\n\nТекущий промокод - {promo}')
    await state.set_state(TestStates.all()[0])


@dp.message_handler(state=TestStates.TEST_STATE_1)
async def promo_handler(message):
    await bot.send_message(message.from_user.id, f'🚫 Введите промокод для доступа к функционалу')



@dp.message_handler(state=TestStates.TEST_STATE_0)
async def promo_handler(message):
    state = dp.current_state(user=message.from_user.id)
    update_promo(message.text)
    promo = get_promo()
    await bot.send_message(message.from_user.id, f'Промокод обновлен: {promo}')
    await state.reset_state()

# Обработка кнопок клавиатуры
@dp.callback_query_handler(lambda call: call.data)
async def process_callback_button1(call):
    # в state храним переменные
    state = dp.current_state(user=call['from']['id'])
    user_data = await state.get_data()
    # получить список элементов меню из базы
    menulist = db.read_sqlite_table(call.data)
    # удаление сообщений, картинок (TODO: добавить поддержку других форматов)
    try:
        for i in range(len(user_data['del_img'])):
            await bot.delete_message(call.message.chat.id, user_data['del_img'][i]["message_id"])
    except Exception as e:
        pass
    try:
        await bot.delete_message(call.message.chat.id, user_data['del_link']["message_id"])
    except Exception as e:
        pass
    # Распаковка меню из SQLlite
        # прислать видео если есть
    if call.data == 'Наши регалии':
        media = types.MediaGroup()
        media.attach_photo('AgACAgIAAxkBAAIEP2KCZ8XZ08ORGDbFzyWm1mCkc__bAAIqwDEbJdkZSCOYkCzkeu7tAQADAgADcwADJAQ', 'Превосходная фотография')
        media.attach_photo('AgACAgIAAxkBAAIEPGKCZ8RgXj_cZ7Eeq30RtY_NeY01AAIpwDEbJdkZSPbN8oMZ-JDCAQADAgADcwADJAQ', 'Превосходная фотография 1')
        media.attach_photo('AgACAgIAAxkBAAIEOWKCZ8Ov50a-hHfGbrsuoz5yl-QKAAIowDEbJdkZSA12umlTEI5aAQADAgADcwADJAQ', 'Превосходная фотография 2')
        media.attach_photo('AgACAgIAAxkBAAIENmKCZ8KL7d8e3i8_AAG5_4HgtyMmMAACJ8AxGyXZGUh4haFwb_lhKwEAAwIAA3MAAyQE', 'Превосходная фотография 3')
        media.attach_photo('AgACAgIAAxkBAAIEM2KCZ8HxbqqVUz4Niu1fqk6fKb3QAAImwDEbJdkZSMvnpAOMD4pkAQADAgADcwADJAQ',
                           'Превосходная фотография 4')
        media.attach_photo('AgACAgIAAxkBAAIEMGKCZ8HIU96-zmAIY4LCUFMkRrMDAAIlwDEbJdkZSKwq_-qGTmEmAQADAgADcwADJAQ',
                           'Превосходная фотография 5')
        del_img = await bot.send_media_group(call.message.chat.id, media=media)
        await state.update_data(del_img=del_img)
    # прислать документ если есть
    if call.data in documents:
        for x in documents[call.data]:
            await bot.send_document(call.from_user.id, x)
    if call.data in youtube:
        for x in youtube[call.data]:
            # await bot.send_document(call.from_user.id, x)
            await bot.send_message(call.from_user.id, x)
            time.sleep(0.5)
    if call.data in menulist[0]:
            await bot.answer_callback_query(call.id)
            del_link = await bot.send_message(call.from_user.id, messages_text[call.data], reply_markup=kb.inlinekey(option=call.data, parent=menulist[1]))
            await state.update_data(del_link=del_link)



#-----------------------------------Работа с базой----------------------------------------------------------------------


# добавить себя в базу
@dp.message_handler(commands=['add'])
async def start_handler(message):
    try:
        await bot.send_message(message.from_user.id, f"Пришлите свой контакт", reply_markup=markup_request)
    except Exception as e:
        print(e)


# обработка присланного контакта от пользователя
@dp.message_handler(content_types=['contact'])
async def contact(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    # если его нет в базе - записываем
    if not db.check_user(message.from_user.id):
        contact = message.contact
        try:
            db.add_user(contact["user_id"], contact["phone_number"][1:], contact["first_name"], message.from_user.username)
            await bot.send_message(message.from_user.id, f"Контакт получен спасибо", reply_markup=markup_del)
            del_link = await bot.send_message(message.from_user.id, f"{messages_text['start']}",
                                              reply_markup=kb.inlinekey(option='start'))
            await state.update_data(del_link=del_link)
        except Exception as e: print(e)


# удалить себя из базы
@dp.message_handler(commands=['delete'])
async def start_handler(message):
    try:
        db.del_user(message.from_user.id)
        await bot.send_message(message.from_user.id, f"Вы удалены из базы")
    except Exception as e:
        print(e)


# проверить себя в базе, прислать в ответ запись или оповестить об отсутствии
@dp.message_handler(commands=['check'])
async def start_handler(message):
    try:
        text = db.check_user(message.from_user.id)
        if len(text) > 0:
            await bot.send_message(message.from_user.id, f"{text}")
        else:
            await bot.send_message(message.from_user.id, f"Вас нет в базе")
    except Exception as e:
        print(e)



#-----------------пишем ID файлов в базу с именами----------------------------------------------------------------------



@dp.message_handler(content_types= ['photo', 'video', 'document'])
async def start_handler(message):
    #state = dp.current_state(user=message.from_user.id)
    if 'document' in message:
        print(message['caption'])
        file_id = message.document
        file_id = file_id["file_id"]
        await bot.send_document(message.from_user.id, f'{file_id}')
        await bot.send_message(message.from_user.id, f'{file_id}')
        db.add_ID(message['message_id'], file_id, f'{message["caption"]}')
    elif 'video' in message:
        file_id = message.video
        file_id = file_id["file_id"]
        await bot.send_video(message.from_user.id, f'{file_id}')
        await bot.send_message(message.from_user.id, f'{file_id}')
        db.add_ID(message['message_id'], file_id, f'{message["caption"]}')
    elif 'photo' in message:
        file_id = message.photo
        file_id = file_id[0]["file_id"]
        await bot.send_photo(message.from_user.id, f'{file_id}')
        await bot.send_message(message.from_user.id, f'{file_id}')
        db.add_ID(message['message_id'], file_id, f'{message["caption"]}')


'''@dp.message_handler(state='*')
async def start_handler(message):
    await bot.send_message(message.from_user.id, '/add\n/delete\n/check\n/s /start\nИли отправьте мне контакт или файл')'''


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp)