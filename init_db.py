import sqlite3
import os


def init_db_historical_figures():
    db_file = 'historical_figures.db'

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


def init_db_history():
    print('OK')
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        date TEXT,
                        latitude REAL,
                        longitude REAL,
                        image BLOB
                      )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS test_results (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        answer TEXT,
                        score INTEGER
                      )''')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db_historical_figures()
    init_db_history()
