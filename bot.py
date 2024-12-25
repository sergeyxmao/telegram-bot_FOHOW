import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
import sqlite3

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Константы для состояний
MAIN_MENU, SEARCH_MENU, SEARCH_COUNTRY = range(3)

# Подключение к SQLite
DB_PATH = os.getenv('DB_PATH', 'fohow.db')
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# Создание таблиц в базе данных
cursor.execute('''CREATE TABLE IF NOT EXISTS representations (
    id INTEGER PRIMARY KEY,
    country TEXT,
    city TEXT,
    address TEXT,
    phone TEXT,
    contact_person TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS partners (
    id INTEGER PRIMARY KEY,
    country TEXT,
    city TEXT,
    name TEXT,
    phone TEXT,
    telegram TEXT
)''')
conn.commit()

def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("\U0001F50E Найти", callback_data='find')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Добро пожаловать в Базу FOHOW! Выберите действие:", reply_markup=reply_markup)
    return MAIN_MENU

def main_menu_handler(update: Update, context):
    query = update.callback_query
    query.answer()
    if query.data == 'find':
        keyboard = [
            [InlineKeyboardButton("\U0001F3E2 Представительство", callback_data='representation')],
            [InlineKeyboardButton("\U0001F464 Партнёра", callback_data='partner')],
            [InlineKeyboardButton("\U0001F519 Назад", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text("Что вы хотите найти?", reply_markup=reply_markup)
        return SEARCH_MENU

def search_menu_handler(update: Update, context):
    query = update.callback_query
    query.answer()
    if query.data == 'representation' or query.data == 'partner':
        context.user_data['search_type'] = query.data
        query.edit_message_text("Введите страну для поиска:")
        return SEARCH_COUNTRY
    elif query.data == 'back':
        return start(update, context)

def search_country_handler(update: Update, context):
    search_type = context.user_data.get('search_type')
    country = update.message.text

    if search_type == 'representation':
        cursor.execute("SELECT city, address, phone, contact_person FROM representations WHERE country = ?", (country,))
    else:
        cursor.execute("SELECT city, name, phone, telegram FROM partners WHERE country = ?", (country,))

    results = cursor.fetchall()

    if results:
        response = "\U0001F4C4 Найдены результаты:\n"
        for row in results:
            response += f"Город: {row[0]}\n"
            if search_type == 'representation':
                response += f"Адрес: {row[1]}\nТелефон: {row[2]}\nКонтактное лицо: {row[3]}\n\n"
            else:
                response += f"Имя: {row[1]}\nТелефон: {row[2]}\nTelegram: {row[3]}\n\n"
        update.message.reply_text(response)
    else:
        update.message.reply_text("\U0001F6AB Ничего не найдено. Попробуйте другую страну.")

    return MAIN_MENU

def cancel(update: Update, context):
    update.message.reply_text("\U0001F44B До свидания! Вы можете начать заново, отправив /start.")
    return ConversationHandler.END

def main():
    # Чтение токена из переменных окружения
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN не установлен в переменных окружения.")
        return

    application = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [CallbackQueryHandler(main_menu_handler)],
            SEARCH_MENU: [CallbackQueryHandler(search_menu_handler)],
            SEARCH_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_country_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    logger.info("Бот запущен и ожидает сообщения.")
    application.run_polling()

if __name__ == '__main__':
    main()
