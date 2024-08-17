import sqlite3

conn = sqlite3.connect('events.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER,
        start_year INTEGER,
        end_year INTEGER,
        location_lat REAL,
        location_lng REAL,
        title TEXT,
        description TEXT,
        image TEXT,
        video TEXT
    )
''')

events = [
    
]

cursor.executemany('''
    INSERT INTO events (year, start_year, end_year, location_lat, location_lng, title, description, image, video)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', events)

conn.commit()
conn.close()
