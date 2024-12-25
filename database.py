import sqlite3

# Подключение к базе данных (если файл базы отсутствует, он будет создан)
conn = sqlite3.connect("fohow.db")
cursor = conn.cursor()

# Создание таблицы для представительств
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

# Создание таблицы для партнёров
cursor.execute("""
CREATE TABLE IF NOT EXISTS partners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country TEXT NOT NULL,
    city TEXT NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    telegram TEXT NOT NULL
)
""")

# Закрытие соединения
conn.commit()
conn.close()

print("База данных успешно создана!")
