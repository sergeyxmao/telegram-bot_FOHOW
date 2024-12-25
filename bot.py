import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

API_TOKEN = "7780696135:AAH2rBcDXs79KFW3PmnNnImrAI4t0vz6GL0"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Зарегистрироваться в базе")],
        [KeyboardButton(text="Найти")]
    ],
    resize_keyboard=True
)

register_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Как представительство")],
        [KeyboardButton(text="Как партнёр")],
        [KeyboardButton(text="Назад"), KeyboardButton(text="Главная")]
    ],
    resize_keyboard=True
)

search_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Представительство")],
        [KeyboardButton(text="Партнёр")],
        [KeyboardButton(text="Назад"), KeyboardButton(text="Главная")]
    ],
    resize_keyboard=True
)

class RepresentativeRegistration(StatesGroup):
    country = State()
    city = State()
    address = State()
    phone = State()
    contact_person = State()

def connect_db():
    return sqlite3.connect("fohow.db")

def execute_query(query, params=None):
    with connect_db() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()

def fetch_query(query, params=None):
    with connect_db() as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()

def create_tables():
    execute_query("""
        CREATE TABLE IF NOT EXISTS representatives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT NOT NULL,
            city TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT NOT NULL,
            contact_person TEXT NOT NULL
        )
    """)
    execute_query("""
        CREATE TABLE IF NOT EXISTS partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT NOT NULL,
            city TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            telegram TEXT
        )
    """)

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(
        "Добро пожаловать в Базу FOHOW!\nВыберите действие из меню ниже.",
        reply_markup=main_menu
    )

@dp.message(lambda message: message.text == "Зарегистрироваться в базе")
async def register_handler(message: Message):
    await message.answer(
        "Выберите, кого вы хотите зарегистрировать:",
        reply_markup=register_menu
    )

@dp.message(lambda message: message.text == "Как представительство")
async def register_representative(message: Message, state: FSMContext):
    await message.answer("Введите страну:")
    await state.set_state(RepresentativeRegistration.country)

@dp.message(RepresentativeRegistration.country)
async def ask_city(message: Message, state: FSMContext):
    await state.update_data(country=message.text)
    await message.answer("Введите город:")
    await state.set_state(RepresentativeRegistration.city)

@dp.message(RepresentativeRegistration.city)
async def ask_address(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("Введите адрес:")
    await state.set_state(RepresentativeRegistration.address)

@dp.message(RepresentativeRegistration.address)
async def ask_phone(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("Введите телефон:")
    await state.set_state(RepresentativeRegistration.phone)

@dp.message(RepresentativeRegistration.phone)
async def ask_contact_person(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Введите имя контактного лица:")
    await state.set_state(RepresentativeRegistration.contact_person)

@dp.message(RepresentativeRegistration.contact_person)
async def finish_registration(message: Message, state: FSMContext):
    user_data = await state.get_data()
    execute_query("""
        INSERT INTO representatives (country, city, address, phone, contact_person)
        VALUES (?, ?, ?, ?, ?)
    """, (user_data['country'], user_data['city'], user_data['address'], user_data['phone'], message.text))
    await message.answer("Регистрация завершена!")
    await state.clear()

@dp.message(lambda message: message.text == "Найти")
async def search_handler(message: Message):
    await message.answer(
        "Что вы хотите найти?",
        reply_markup=search_menu
    )

@dp.message(lambda message: message.text == "Представительство")
async def search_representative(message: Message):
    await message.answer("Введите страну для поиска представительств:")

@dp.message(lambda message: message.text == "Партнёр")
async def search_partner(message: Message):
    await message.answer("Введите страну для поиска партнёров:")

@dp.message()
async def process_search_query(message: Message):
    query = message.text.strip()
    results_rep = fetch_query("""
        SELECT country, city, address, phone, contact_person
        FROM representatives
        WHERE country LIKE ?
    """, (f"%{query}%",))

    results_part = fetch_query("""
        SELECT country, city, name, phone, telegram
        FROM partners
        WHERE country LIKE ?
    """, (f"%{query}%",))

    response = "Результаты поиска:\n\n"
    
    if results_rep:
        response += "Представительства:\n"
        for rep in results_rep:
            response += (
                f"Страна: {rep[0]}\n"
                f"Город: {rep[1]}\n"
                f"Адрес: {rep[2]}\n"
                f"Телефон: {rep[3]}\n"
                f"Контактное лицо: {rep[4]}\n\n"
            )
    else:
        response += "Представительства не найдены.\n\n"

    if results_part:
        response += "Партнёры:\n"
        for part in results_part:
            response += (
                f"Страна: {part[0]}\n"
                f"Город: {part[1]}\n"
                f"Имя: {part[2]}\n"
                f"Телефон: {part[3]}\n"
                f"Telegram: {part[4] or 'Не указано'}\n\n"
            )
    else:
        response += "Партнёры не найдены.\n\n"

    await message.answer(response)

async def main():
    create_tables()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
