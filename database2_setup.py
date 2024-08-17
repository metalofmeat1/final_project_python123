import sqlite3

conn = sqlite3.connect('history.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        date TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL
    )
''')

conn.commit()
conn.close()

print("База даних history.db створена.")
