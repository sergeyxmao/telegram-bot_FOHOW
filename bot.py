import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os

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
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)

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

def create_tables():
    with sqlite3.connect("fohow.db") as conn:
        cursor = conn.cursor()
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

@dp.message(Command("start"))
async def send_welcome(message: Message):
    logger.info("Обработчик /start вызван.")
    await message.answer(
        "Добро пожаловать в Базу FOHOW!\nВыберите действие из меню ниже.",
        reply_markup=main_menu
    )

@dp.message(lambda message: message.text == "Зарегистрироваться в базе")
async def register_handler(message: Message):
    logger.info("Меню регистрации открыто.")
    await message.answer(
        "Выберите, кого вы хотите зарегистрировать:",
        reply_markup=register_menu
    )

@dp.message(lambda message: message.text == "Как представительство")
async def register_representative(message: Message, state: FSMContext):
    logger.info("Регистрация представительства начата.")
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
    with sqlite3.connect("fohow.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO representatives (country, city, address, phone, contact_person)
            VALUES (?, ?, ?, ?, ?)
        """, (user_data['country'], user_data['city'], user_data['address'], user_data['phone'], message.text))
    await message.answer("Регистрация завершена!")
    await state.clear()

async def main():
    create_tables()
    logger.info("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
