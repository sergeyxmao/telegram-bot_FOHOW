import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Укажите токен вашего бота
API_TOKEN = "7780696135:AAEyN2imxZU4U99MwyQHw0P8zlInoZPbGqk"

# Укажите URL вашего бота на сервере (например, Railway)
WEBHOOK_URL = "https://<your-deployed-app-url>"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Зарегистрироваться в базе")],
        [KeyboardButton(text="Найти")]
    ],
    resize_keyboard=True
)

# Подменю регистрации
register_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Как представительство")],
        [KeyboardButton(text="Как партнёр")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)

# Классы для состояний
class RepresentativeRegistration(StatesGroup):
    country = State()
    city = State()
    address = State()
    phone = State()
    contact_person = State()

class PartnerRegistration(StatesGroup):
    country = State()
    city = State()
    name = State()
    phone = State()
    telegram = State()

# Создание таблиц в базе данных
def create_tables():
    conn = sqlite3.connect("fohow.db")
    cursor = conn.cursor()

    # Таблица для представительств
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS representatives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT NOT NULL,
            city TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT NOT NULL,
            contact_person TEXT NOT NULL
        )
    """)

    # Таблица для партнёров
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT NOT NULL,
            city TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            telegram TEXT
        )
    """)

    conn.commit()
    conn.close()

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(
        "Добро пожаловать в Базу FOHOW!\nВыберите действие из меню ниже.",
        reply_markup=main_menu
    )

# Обработчики для регистрации представительств
@dp.message(lambda message: message.text == "Как представительство")
async def register_representative(message: Message, state: FSMContext):
    await message.answer("Введите страну:")
    await state.set_state(RepresentativeRegistration.country)

@dp.message(RepresentativeRegistration.country)
async def ask_city_for_representative(message: Message, state: FSMContext):
    await state.update_data(country=message.text)
    await message.answer("Введите город:")
    await state.set_state(RepresentativeRegistration.city)

@dp.message(RepresentativeRegistration.city)
async def ask_address_for_representative(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("Введите адрес:")
    await state.set_state(RepresentativeRegistration.address)

@dp.message(RepresentativeRegistration.address)
async def ask_phone_for_representative(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("Введите телефон:")
    await state.set_state(RepresentativeRegistration.phone)

@dp.message(RepresentativeRegistration.phone)
async def ask_contact_person_for_representative(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Введите имя контактного лица:")
    await state.set_state(RepresentativeRegistration.contact_person)

@dp.message(RepresentativeRegistration.contact_person)
async def finish_representative_registration(message: Message, state: FSMContext):
    user_data = await state.get_data()
    conn = sqlite3.connect("fohow.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO representatives (country, city, address, phone, contact_person)
        VALUES (?, ?, ?, ?, ?)
    """, (user_data['country'], user_data['city'], user_data['address'], user_data['phone'], message.text))
    conn.commit()
    conn.close()

    await message.answer(
        f"Регистрация завершена:\n"
        f"Страна: {user_data['country']}\n"
        f"Город: {user_data['city']}\n"
        f"Адрес: {user_data['address']}\n"
        f"Телефон: {user_data['phone']}\n"
        f"Контактное лицо: {message.text}"
    )
    await state.clear()

# Установка webhook
async def set_webhook():
    await bot.set_webhook(WEBHOOK_URL)

# Удаление webhook (при необходимости)
async def delete_webhook():
    await bot.delete_webhook()

# Основная функция
async def main():
    create_tables()
    logger.info("Настройка webhook...")
    await set_webhook()
    logger.info("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
