import sqlite3


def init_admin_db():
    conn = sqlite3.connect('./database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

    print("База даних admins.db створена.")


def init_super_admin():
    conn = sqlite3.connect('./database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO admins (email, username, password, role) VALUES ('admin_email@gmail.com', 'admin', 'admin', 'super_admin')")
    conn.commit()
    conn.close()
    print('Супер адміна додано')


init_admin_db()
init_super_admin()
