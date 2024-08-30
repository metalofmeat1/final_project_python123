import sqlite3
import os

def init_db():
    db_file = 'historical_figures.db'


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

if __name__ == '__main__':
    init_db()
