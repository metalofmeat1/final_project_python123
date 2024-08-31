import sqlite3


def init_db():
    conn = sqlite3.connect('./history2.db')
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

init_db()