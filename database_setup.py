import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        avatar TEXT DEFAULT 'default-avatar.jpg'  
    )
''')


cursor.execute("PRAGMA table_info(users)")
columns = [column[1] for column in cursor.fetchall()]

if 'avatar' not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN avatar TEXT DEFAULT 'default-avatar.jpg'")
    print("Столбец 'avatar' был успешно добавлен в таблицу 'users'.")

conn.commit()
conn.close()

print("База даних history.db створена.")

