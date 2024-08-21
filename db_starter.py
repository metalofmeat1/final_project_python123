import sqlite3


def init_db():
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS events_new (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        date TEXT,
                        latitude REAL,
                        longitude REAL,
                        image TEXT  -- Нове поле для зберігання зображень
                      )''')

    cursor.execute('''INSERT INTO events_new (id, name, description, date, latitude, longitude)
                      SELECT id, name, description, date, latitude, longitude
                      FROM events''')

    cursor.execute('DROP TABLE IF EXISTS events')

    cursor.execute('ALTER TABLE events_new RENAME TO events')

    conn.commit()
    conn.close()
