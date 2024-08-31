import sqlite3


def init_historical_figures_db():
    db_file = 'databases/historical_figures.db'

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS figures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        birth_year INTEGER,
        death_year INTEGER,
        biography TEXT,
        notable_for TEXT,
        image BLOB
    )
    ''')

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


def init_admin_db():
    conn = sqlite3.connect('databases/admins.db')
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
    conn = sqlite3.connect('databases/admins.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO admins (email, username, password, role) VALUES ('admin_email@gmail.com', 'admin', 'admin', 'super_admin')")
    conn.commit()
    conn.close()
    print('Супер адміна додано')


def init_history_db():
    conn = sqlite3.connect('databases/history.db')
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
    print('База даних history.db створена.')


def init_score():
    conn = sqlite3.connect('databases/users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS leaders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        result INTEGER NOT NULL
                      )''')
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_score()
    init_history_db()
    init_historical_figures_db()
    init_admin_db()
    init_super_admin()


