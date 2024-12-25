import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

API_TOKEN = "7780696135:AAEyN2imxZU4U99MwyQHw0P8zlInoZPbGqk"

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

def create_table():
    conn = sqlite3.connect("fohow.db")
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
    conn.commit()
    conn.close()

def save_representative_to_db(data):
    try:
        conn = sqlite3.connect("fohow.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO representatives (country, city, address, phone, contact_person)
            VALUES (?, ?, ?, ?, ?)
        """, (data['country'], data['city'], data['address'], data['phone'], data['contact_person']))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Ошибка при работе с базой данных: {e}")
    finally:
        conn.close()

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
    logger.info("Пользователь начал регистрацию представительства.")
    await message.answer("Введите страну:")
    await state.set_state(RepresentativeRegistration.country)

@dp.message(RepresentativeRegistration.country)
async def ask_city(message: Message, state: FSMContext):
    if message.text.strip():
        logger.info(f"Текущее состояние: {await state.get_state()}, Ввод страны: {message.text}")
        await state.update_data(country=message.text)
        await message.answer("Введите город:")
        await state.set_state(RepresentativeRegistration.city)

@dp.message(RepresentativeRegistration.city)
async def ask_address(message: Message, state: FSMContext):
    if message.text.strip():
        logger.info(f"Текущее состояние: {await state.get_state()}, Ввод города: {message.text}")
        await state.update_data(city=message.text)
        await message.answer("Введите адрес:")
        await state.set_state(RepresentativeRegistration.address)

@dp.message(RepresentativeRegistration.address)
async def ask_phone(message: Message, state: FSMContext):
    if message.text.strip():
        logger.info(f"Текущее состояние: {await state.get_state()}, Ввод адреса: {message.text}")
        await state.update_data(address=message.text)
        await message.answer("Введите телефон:")
        await state.set_state(RepresentativeRegistration.phone)

@dp.message(RepresentativeRegistration.phone)
async def ask_contact_person(message: Message, state: FSMContext):
    if message.text.strip():
        logger.info(f"Текущее состояние: {await state.get_state()}, Ввод телефона: {message.text}")
        await state.update_data(phone=message.text)
        await message.answer("Введите имя контактного лица:")
        await state.set_state(RepresentativeRegistration.contact_person)

@dp.message(RepresentativeRegistration.contact_person)
async def finish_registration(message: Message, state: FSMContext):
    if message.text.strip():
        logger.info(f"Текущее состояние: {await state.get_state()}, Ввод контактного лица: {message.text}")
        user_data = await state.get_data()
        await state.update_data(contact_person=message.text)

        save_representative_to_db({
            "country": user_data['country'],
            "city": user_data['city'],
            "address": user_data['address'],
            "phone": user_data['phone'],
            "contact_person": message.text
        })

        await message.answer(
            f"Регистрация завершена и сохранена в базе!\n"
            f"Данные представительства:\n"
            f"Страна: {user_data['country']}\n"
            f"Город: {user_data['city']}\n"
            f"Адрес: {user_data['address']}\n"
            f"Телефон: {user_data['phone']}\n"
            f"Контактное лицо: {message.text}"
        )

        await state.clear()

@dp.message(lambda message: message.text == "Как партнёр")
async def register_partner(message: Message):
    await message.answer("Функция регистрации партнёров пока не реализована.")

@dp.message(lambda message: message.text == "Назад")
async def go_back_to_main_menu(message: Message):
    await message.answer(
        "Вы вернулись в главное меню.",
        reply_markup=main_menu
    )

@dp.message(lambda message: message.text == "Найти")
async def find_handler(message: Message):
    await message.answer("Вы выбрали поиск. Уточните, что хотите найти:\n1. Представительство\n2. Партнёра")

async def main():
    create_table()
    logger.info("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
