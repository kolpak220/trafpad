import logging
from database import create_db, add_user, update_user, delete_user, get_user_data, get_ref

from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from datetime import datetime
import os
import random

admins_id = [1634257885, 5747705509]

# Токен вашего бота
API_TOKEN = '7269688779:AAFIhOQ4EfkJIvaASiAWb_td0-CFWtYDZmM'

storage = MemoryStorage()


# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


class AddUserForm(StatesGroup):
    user_id = State()  # Запрос user_id
    ref_link = State()  # Запрос реферальной ссылки
    bot_link = State()  # Запрос ссылки на бота
class EditUserForm(StatesGroup):
    user_id = State()  # Запрос user_id
    ref_link = State()  # Запрос реферальной ссылки
class DeleteUserForm(StatesGroup):
    user_id = State()
class ReferToLink(StatesGroup):
    ref_link = State()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    args = message.get_args()

    ref_link = get_ref(args)
    
    user_id = message.from_user.id  # Получаем ID пользователя из сообщения

    # Проверяем, есть ли пользователь в базе данных
    user_data = get_user_data(user_id)
    # Проверка, является ли пользователь администратором

    if user_data:
        # Если пользователь найден, отправляем данные о его ссылках
        ref_link = user_data['ref_link']
        bot_link = user_data['bot_link']
        await bot.send_message(message.chat.id, f"Добро пожаловать трафер!\n"
                             f"Ваша реферальная ссылка: {ref_link}\n"
                             f"Ссылка на бота: https://t.me/hack777jet_bot?start={bot_link}")
    if user_id in admins_id:
        # Если это администратор, то создаём кнопки
        admin_welcome_text = "Привет, админ!\nВы можете управлять ботом с помощью кнопок ниже."
        
        # Создаем кнопки для администратора
        inline_kb = InlineKeyboardMarkup()  # Создаем inline-клавиатуру
        button1 = InlineKeyboardButton("Добавить", callback_data='add_user')
        button2 = InlineKeyboardButton("Изменить", callback_data='edit_user')
        button3 = InlineKeyboardButton("Удалить", callback_data='remove_user') 
        inline_kb.add(button1, button2, button3)

        
        # Отправка сообщения с кнопками
        await bot.send_message(message.chat.id, admin_welcome_text, reply_markup=inline_kb)
    elif ref_link:
        # Текст приветствия для обычных пользователей
        welcome_text = "Добро пожаловать!\n\nВ данном боте рассказывается, как обойти скрипт казино и забрать профит."
        
        # Путь к изображению
        image_path = "welcome_image.jpg"
        
        # Создаём клавиатуру с кнопкой-ссылкой
        keyboard = InlineKeyboardMarkup()
        
        # Добавляем кнопку-ссылку с ref_link
        button1 = InlineKeyboardButton("🚀 Lucky Jet (способ №1)", callback_data='jet_lit')
        button2 = InlineKeyboardButton("🚀 Lucky Jet (способ №2)", callback_data='jet_big')
        button3 = InlineKeyboardButton("💣 Mines СИГНАЛ", callback_data='mines_lit')
        # button4 = InlineKeyboardButton("🧨 Mines (способ №2)", callback_data='mines_big')
        button5 = InlineKeyboardButton("💰 1win 💰", url=ref_link)
        keyboard.add(button1).add(button2).add(button3).add(button5)
        
        # Отправка сообщения с текстом, изображением и кнопкой
        with open(image_path, 'rb') as image_file:
            await bot.send_photo(
                message.chat.id, 
                photo=InputFile(image_file), 
                caption=welcome_text, 
                reply_markup=keyboard  # Добавляем клавиатуру с кнопкой
            )
        await ReferToLink.ref_link.set()
        state = dp.current_state(user=user_id)
        await state.update_data(ref_link=ref_link)
    else:
        # Текст приветствия для обычных пользователей
        welcome_text = "Добро пожаловать!\n\nВ данном боте рассказывается, как обойти скрипт казино и забрать профит."
        
        # Путь к изображению
        image_path = "welcome_image.jpg"
        
        # Отправка сообщения с текстом и изображением
        with open(image_path, 'rb') as image_file:
            await bot.send_photo(message.chat.id, photo=InputFile(image_file), caption=welcome_text)


@dp.callback_query_handler(lambda c: c.data == 'jet_lit', state=ReferToLink.ref_link)
async def process_callback(callback_query: CallbackQuery, state=FSMContext):
    data = await state.get_data()
    ref_link = data.get('ref_link')

    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton("💰 1win 💰", url=ref_link)
    button2 = InlineKeyboardButton("◀️ Назад", callback_data="back")
    keyboard.add(button1).add(button2)

    with open('jet1.png', 'rb') as image_file:
        await bot.send_photo(
            callback_query.message.chat.id, 
            photo=InputFile(image_file), 
            caption="Играем только с нового аккаунта! ( Первый депозит +500% ) \n\n*схема только для маленьких ставок (500-2000)*\nВыбираем ракетку, ставим минималку 1 раз и проигрываем, после ставим всё и забираем от 2Х до 3Х", 
            reply_markup=keyboard  # Добавляем клавиатуру с кнопкой
        )
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    
    # Устанавливаем состояние ожидания ID пользователя
@dp.callback_query_handler(lambda c: c.data == 'jet_big', state=ReferToLink.ref_link)
async def process_callback(callback_query: CallbackQuery, state=FSMContext):
    data = await state.get_data()
    ref_link = data.get('ref_link')

    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton("💰 1win 💰", url=ref_link)
    button2 = InlineKeyboardButton("◀️ Назад", callback_data="back")
    keyboard.add(button1).add(button2)

    with open('jet2.jpg', 'rb') as image_file:
        await bot.send_photo(
            callback_query.message.chat.id, 
            photo=InputFile(image_file), 
            caption="Играем только с нового аккаунта! ( Первый депозит +500% )\n\n*схема только для БОЛЬШИХ ставок (2000+)*\nВыбираем ракетку, ставим минималку 3 раза и проигрываем, после ставим половину от суммы депа и забираем СТРОГО на 4.35Х", 
            reply_markup=keyboard  # Добавляем клавиатуру с кнопкой
        )
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    
@dp.callback_query_handler(lambda c: c.data == 'mines_lit', state=ReferToLink.ref_link)
async def process_callback(callback_query: CallbackQuery, state=FSMContext):
    data = await state.get_data()
    ref_link = data.get('ref_link')

    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton("💰 1win 💰", url=ref_link)
    button2 = InlineKeyboardButton("◀️ Назад", callback_data="back")
    keyboard.add(button1).add(button2)
    files = os.listdir('mines')
    
    
    
    # Полный путь к изображению
    
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

    # Фильтруем только изображения (например, файлы с расширениями .jpg, .png)
    random_image_file = random.choice(image_files)

    image_path = os.path.join('mines', random_image_file)
    with open(image_path, 'rb') as image_file:
        await bot.send_photo(
            callback_query.message.chat.id, 
            photo=InputFile(image_file), 
            caption="Сигнал на следующий раунд!!!\n\nИграем только с нового аккаунта! ( Первый депозит +500% )\n\nВыбираем МИНЫ, ставим сколько хотите, повторяем все действия как на картинке, выводим, регистрируем новый аккаунт, повторяем круг", 
            reply_markup=keyboard  # Добавляем клавиатуру с кнопкой
        )
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    
@dp.callback_query_handler(lambda c: c.data == 'mines_big', state=ReferToLink.ref_link)
async def process_callback(callback_query: CallbackQuery, state=FSMContext):
    data = await state.get_data()
    ref_link = data.get('ref_link')

    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton("💰 1win 💰", url=ref_link)
    button2 = InlineKeyboardButton("◀️ Назад", callback_data="back")
    keyboard.add(button1).add(button2)

    await bot.send_message(callback_query.from_user.id, "Мины 2", reply_markup=keyboard)
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)



@dp.callback_query_handler(lambda c: c.data == 'back', state=ReferToLink.ref_link)
async def process_callback(callback_query: CallbackQuery, state=FSMContext):
    data = await state.get_data()
    ref_link = data.get('ref_link')

    welcome_text = "Добро пожаловать!\n\nВ данном боте рассказывается, как обойти скрипт казино и забрать профит."
        
        # Путь к изображению
    image_path = "welcome_image.jpg"
        
        # Создаём клавиатуру с кнопкой-ссылкой
    keyboard = InlineKeyboardMarkup()
        
        # Добавляем кнопку-ссылку с ref_link
    button1 = InlineKeyboardButton("🚀 Lucky Jet (способ №1)", callback_data='jet_lit')
    button2 = InlineKeyboardButton("🚀 Lucky Jet (способ №2)", callback_data='jet_big')
    button3 = InlineKeyboardButton("💣 Mines (СИГНАЛ)", callback_data='mines_lit')
    # button4 = InlineKeyboardButton("🧨 Mines (способ №2)", callback_data='mines_big')
    button5 = InlineKeyboardButton("💰 1win 💰", url=ref_link)
    keyboard.add(button1).add(button2).add(button3).add(button5)
        
        # Отправка сообщения с текстом, изображением и кнопкой
    with open(image_path, 'rb') as image_file:
        await bot.send_photo(
            callback_query.message.chat.id, 
            photo=InputFile(image_file), 
            caption=welcome_text, 
            reply_markup=keyboard  # Добавляем клавиатуру с кнопкой
        )


    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)














@dp.callback_query_handler(lambda c: c.data == 'remove_user')
async def process_callback(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Удаление\n\nВведите ID пользователя:")
    
    # Устанавливаем состояние ожидания ID пользователя
    await DeleteUserForm.user_id.set()
@dp.message_handler(state=DeleteUserForm.user_id)
async def process_ref_link(message: types.Message, state: FSMContext):
    user_id = message.text
    
    try:
        delete_user(int(user_id))
        await bot.send_message(message.from_user.id,f"Пользователь с ID {user_id} успешно удалён.")
    except Exception as e:
        await bot.send_message(message.from_user.id,f"Ошибка: {e}")

    await state.finish()






@dp.callback_query_handler(lambda c: c.data == 'edit_user')
async def process_callback(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Изменение\n\nВведите ID пользователя:")
    
    # Устанавливаем состояние ожидания ID пользователя
    await EditUserForm.user_id.set()

@dp.message_handler(state=EditUserForm.user_id)
async def process_user_id(message: types.Message, state: FSMContext):
    user_id = message.text
    
    # Сохраняем user_id в хранилище FSM
    await state.update_data(user_id=user_id)
    
    # Переход к следующему состоянию — запрос реферальной ссылки
    await EditUserForm.next()
    await bot.send_message(message.from_user.id,"Введите реферальную ссылку:")



# Получение реферальной ссылки
@dp.message_handler(state=EditUserForm.ref_link)
async def process_ref_link(message: types.Message, state: FSMContext):
    ref_link = message.text
    
    # Сохраняем ref_link в хранилище FSM
    data = await state.get_data()
    user_id = data.get('user_id')
    
    # Переход к следующему состоянию — запрос ссылки на бота
    try:
        update_user(int(user_id), {"ref_link":str(ref_link)})
        await bot.send_message(message.from_user.id,f"Пользователь с ID {user_id} успешно изменён.")
    except Exception as e:
        await bot.send_message(message.from_user.id,f"Ошибка при изменении пользователя: {e}")

    await state.finish()










@dp.callback_query_handler(lambda c: c.data == 'add_user')
async def process_callback(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Добавление\n\nВведите ID пользователя:")
    
    # Устанавливаем состояние ожидания ID пользователя
    await AddUserForm.user_id.set()

@dp.message_handler(state=AddUserForm.user_id)
async def process_user_id(message: types.Message, state: FSMContext):
    user_id = message.text
    
    # Сохраняем user_id в хранилище FSM
    await state.update_data(user_id=user_id)
    
    # Переход к следующему состоянию — запрос реферальной ссылки
    await AddUserForm.next()
    await bot.send_message(message.from_user.id,"Введите реферальную ссылку:")

# Получение реферальной ссылки
@dp.message_handler(state=AddUserForm.ref_link)
async def process_ref_link(message: types.Message, state: FSMContext):
    ref_link = message.text
    
    # Сохраняем ref_link в хранилище FSM
    data = await state.get_data()
    user_id = data.get('user_id')
    
    # Переход к следующему состоянию — запрос ссылки на бота
    try:
        add_user(int(user_id), ref_link)
        await bot.send_message(message.from_user.id,f"Пользователь с ID {user_id} успешно добавлен в базу данных.")
    except Exception as e:
        await bot.send_message(message.from_user.id,f"Ошибка при добавлении пользователя: {e}")

    await state.finish()






    
async def main():
    try:
        await dp.start_polling(bot)
        create_db()
    except Exception as e:
        logging.error(f"Ошибка токена: {e}")
    finally:
        await bot.session.close()

# Запуск основного цикла
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    create_db()