import sqlite3
from datetime import datetime

# Створення бази даних та таблиці
conn = sqlite3.connect('events.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year TEXT,  -- Використовуємо текстовий формат для року або дати
        start_year TEXT,  -- Текстовий формат для початкової дати
        end_year TEXT,  -- Текстовий формат для кінцевої дати
        location_lat REAL,
        location_lng REAL,
        title TEXT,
        description TEXT,
        image TEXT,
        video TEXT
    )
''')

events = [
    ("1900-01-01", None, None, 50.4501, 30.5234,
     "Перші феміністичні ініціативи в Україні",
     "На початку XX століття в Україні з'явилися перші організації та ініціативи, що боролися за права жінок.",
     "feminism_1900.jpg", "feminism_1900.mp4"),

    (None, "1917-01-01", "1920-12-31", 50.4501, 30.5234,
     "Жіночий рух під час Української революції",
     "У період Української революції жіночі організації активно боролися за рівноправ'я та отримання права голосу.",
     "revolution_feminism.jpg", "revolution_feminism.mp4"),

    ("1965-01-01", None, None, 49.9935, 36.2304,
     "Перші активістки під час радянської епохи",
     "У 1960-70-ті роки в Україні з'явилися активістки, які боролися за права жінок у рамках радянської системи.",
     "soviet_feminism.jpg", "soviet_feminism.mp4"),

    ("2014-01-01", None, None, 50.4501, 30.5234,
     "Сучасний феміністичний рух",
     "З початку 2010-х років в Україні активно розвивається сучасний феміністичний рух, що бореться за гендерну рівність та права жінок.",
     "modern_feminism.jpg", "modern_feminism.mp4"),

    # Додаємо подію з сьогоднішньою датою
    (datetime.now().strftime('%Y-%m-%d'), None, None, 50.4501, 30.5234,
     "Сьогоднішня подія",
     "Це опис події, що відбулася сьогодні.",
     "today_event.jpg", "today_event.mp4")
]

# Вставлення даних у таблицю
cursor.executemany('''
    INSERT INTO events (year, start_year, end_year, location_lat, location_lng, title, description, image, video)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', events)

conn.commit()
conn.close()
