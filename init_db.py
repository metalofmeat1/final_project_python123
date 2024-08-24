import sqlite3
from datetime import datetime

# Створення бази даних та таблиць
conn = sqlite3.connect('history.db')
cursor = conn.cursor()

# Створення таблиці з урахуванням нормалізації даних та оптимізації
cursor.execute('''
    CREATE TABLE IF NOT EXISTS historical_periods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,  -- Назва історичного періоду
        description TEXT  -- Опис періоду (опціонально)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS historical_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        period_id INTEGER NOT NULL,  -- Зовнішній ключ на таблицю historical_periods
        year TEXT,  -- Рік події
        start_year DATE,  -- Початкова дата
        end_year DATE,  -- Кінцева дата
        location_lat REAL NOT NULL,  -- Широта
        location_lng REAL NOT NULL,  -- Довгота
        title TEXT NOT NULL,  -- Назва події
        description TEXT,  -- Опис події
        image TEXT,  -- Зображення
        video TEXT,  -- Відео
        FOREIGN KEY (period_id) REFERENCES historical_periods(id)
        ON DELETE CASCADE ON UPDATE CASCADE  -- Каскадне оновлення та видалення
    )
''')

# # Додавання історичних періодів
# historical_periods = [
#     ("Січ Запорізька", "Історичний період, що характеризується існуванням Запорізької Січі."),
#     ("Україна у складі Речі Посполитої", "Період, коли українські землі входили до складу Речі Посполитої."),
#     ("Сучасна Україна", "Період, що розпочався після проголошення незалежності України у 1991 році.")
# ]

# cursor.executemany('''
#     INSERT OR IGNORE INTO historical_periods (name, description)
#     VALUES (?, ?)
# ''', historical_periods)

# # Отримання ідентифікаторів періодів
# cursor.execute('SELECT id, name FROM historical_periods')
# period_ids = {name: id for id, name in cursor.fetchall()}

# # Додавання подій до таблиці
# historical_events = [
#     (period_ids["Січ Запорізька"], "1648-01-01", None, None, 48.4501, 35.0509,
#      "Повстання під проводом Богдана Хмельницького",
#      "Національно-визвольна війна під проводом Богдана Хмельницького проти Речі Посполитої.",
#      "khmelnytsky_uprising.jpg", "khmelnytsky_uprising.mp4"),

#     (period_ids["Україна у складі Речі Посполитої"], "1569-07-01", None, None, 50.4501, 30.5234,
#      "Люблінська унія",
#      "Укладення Люблінської унії, що призвела до утворення Речі Посполитої та включення українських земель до її складу.",
#      "lublin_union.jpg", "lublin_union.mp4"),

#     (period_ids["Україна у складі Речі Посполитої"], "1596-10-09", None, None, 50.4501, 30.5234,
#      "Берестейська унія",
#      "Угода між частиною української православної церкви і папським престолом, що утворила греко-католицьку церкву.",
#      "berest_union.jpg", "berest_union.mp4"),

#     (period_ids["Сучасна Україна"], "1991-08-24", None, None, 50.4501, 30.5234,
#      "Проголошення незалежності України",
#      "Україна проголосила свою незалежність від Радянського Союзу.",
#      "independence.jpg", "independence.mp4"),

#     (period_ids["Сучасна Україна"], datetime.now().strftime('%Y-%m-%d'), None, None, 50.4501, 30.5234,
#      "Сьогоднішня подія",
#      "Це опис події, що відбулася сьогодні.",
#      "today_event.jpg", "today_event.mp4")
# ]

# # Додавання подій з тривалим часом
# long_duration_events = [
#     (period_ids["Січ Запорізька"], None, "1648-01-01", "1657-12-31", 48.4501, 35.0509,
#      "Національно-визвольна війна під проводом Богдана Хмельницького",
#      "Війна, яка тривала з 1648 по 1657 рік, була спрямована на здобуття незалежності українських земель.",
#      "khmelnytsky_war.jpg", "khmelnytsky_war.mp4"),

#     (period_ids["Україна у складі Речі Посполитої"], None, "1596-01-01", "1596-12-31", 50.4501, 30.5234,
#      "Берестейська унія",
#      "Процес укладення Берестейської унії, який тривав протягом кількох років.",
#      "berest_union_long.jpg", "berest_union_long.mp4"),

#     (period_ids["Сучасна Україна"], None, "2014-01-01", "2022-12-31", 50.4501, 30.5234,
#      "Революція гідності та війна на сході України",
#      "Події, які охоплюють період від початку Революції гідності до активної фази війни на сході України.",
#      "revolution_war.jpg", "revolution_war.mp4")
# ]

# # Вставлення даних у таблицю
# cursor.executemany('''
#     INSERT INTO historical_events (period_id, year, start_year, end_year, location_lat, location_lng, title, description, image, video)
#     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
# ''', historical_events + long_duration_events)

conn.commit()
conn.close()
