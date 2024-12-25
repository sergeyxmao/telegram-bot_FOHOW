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
        [KeyboardButton(text="Найти")],
        [KeyboardButton(text="Редактировать данные")]
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

edit_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Редактировать представительство")],
        [KeyboardButton(text="Редактировать партнёра")],
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

class PartnerRegistration(StatesGroup):
    country = State()
    city = State()
    name = State()
    phone = State()
    telegram = State()

class EditStates(StatesGroup):
    representative_search = State()
    partner_search = State()
    edit_country = State()
    edit_city = State()
    edit_address = State()
    edit_phone = State()
    edit_contact_person = State()

# Ensure SSL is available for secure connections
def verify_ssl_support():
    try:
        import ssl
        logger.info("SSL module is available.")
    except ImportError:
        logger.error("SSL module is not available. Please ensure it is installed.")
        raise


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
        conn.commit()

@dp.message(Command("start"))
async def send_welcome(message: Message):
    logger.info("Обработчик /start вызван.")
    await message.answer(
        "Добро пожаловать в Базу FOHOW!\nВыберите действие из меню ниже.",
        reply_markup=main_menu
    )

@dp.message(lambda message: message.text == "Редактировать данные")
async def edit_handler(message: Message):
    await message.answer(
        "Выберите, что вы хотите редактировать:",
        reply_markup=edit_menu
    )

@dp.message(lambda message: message.text == "Редактировать представительство")
async def edit_representative(message: Message, state: FSMContext):
    await message.answer("Введите ID представительства, которое хотите отредактировать:")
    await state.set_state(EditStates.representative_search)

@dp.message(EditStates.representative_search)
async def update_representative(message: Message, state: FSMContext):
    rep_id = message.text.strip()
    with sqlite3.connect("fohow.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, country, city, address, phone, contact_person
            FROM representatives
            WHERE id = ?
        """, (rep_id,))
        result = cursor.fetchone()

    if result:
        data = {
            "id": result[0],
            "country": result[1],
            "city": result[2],
            "address": result[3],
            "phone": result[4],
            "contact_person": result[5]
        }
        await state.update_data(rep_id=rep_id)
        await message.answer(
            f"Текущие данные:\n"
            f"Страна: {data['country']}\nГород: {data['city']}\n"
            f"Адрес: {data['address']}\nТелефон: {data['phone']}\n"
            f"Контактное лицо: {data['contact_person']}\n\n"
            f"Введите новое значение для страны или напишите 'Пропустить':"
        )
        await state.set_state(EditStates.edit_country)
    else:
        await message.answer("Представительство с указанным ID не найдено.")
        await state.clear()

@dp.message(EditStates.edit_country)
async def process_edit_country(message: Message, state: FSMContext):
    new_value = message.text.strip()
    if new_value.lower() != "пропустить":
        user_data = await state.get_data()
        with sqlite3.connect("fohow.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE representatives
                SET country = ?
                WHERE id = ?
            """, (new_value, user_data['rep_id']))
    await message.answer("Введите новое значение для города или напишите 'Пропустить':")
    await state.set_state(EditStates.edit_city)

@dp.message(EditStates.edit_city)
async def process_edit_city(message: Message, state: FSMContext):
    new_value = message.text.strip()
    if new_value.lower() != "пропустить":
        user_data = await state.get_data()
        with sqlite3.connect("fohow.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE representatives
                SET city = ?
                WHERE id = ?
            """, (new_value, user_data['rep_id']))
    await message.answer("Введите новое значение для адреса или напишите 'Пропустить':")
    await state.set_state(EditStates.edit_address)

@dp.message(EditStates.edit_address)
async def process_edit_address(message: Message, state: FSMContext):
    new_value = message.text.strip()
    if new_value.lower() != "пропустить":
        user_data = await state.get_data()
        with sqlite3.connect("fohow.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE representatives
                SET address = ?
                WHERE id = ?
            """, (new_value, user_data['rep_id']))
    await message.answer("Редактирование завершено.", reply_markup=main_menu)
    await state.clear()

async def main():
    verify_ssl_support()
    create_tables()
    logger.info("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
