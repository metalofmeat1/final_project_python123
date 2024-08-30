import sqlite3
import os


def init_db():
    db_file = 'historical_figures.db'

    # Видалити існуючий файл бази даних
    if os.path.exists(db_file):
        os.remove(db_file)

    # Створення нової бази даних та таблиць
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Створення таблиці постатей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS figures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        birth_year INTEGER,
        death_year INTEGER,
        biography TEXT,
        notable_for TEXT,
        image_filename TEXT
    )
    ''')

    # Створення таблиці каруселі
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS carousel (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        figure_id INTEGER,
        image_filename TEXT NOT NULL,
        FOREIGN KEY (figure_id) REFERENCES figures (id)
    )
    ''')

    # Створення таблиці деталей постатей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS figure_detail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            figure_id INTEGER NOT NULL,
            detail TEXT,
            FOREIGN KEY (figure_id) REFERENCES figures(id)
        )
        ''')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
