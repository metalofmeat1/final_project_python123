import sqlite3


def get_db_connection():
    conn = sqlite3.connect('databases/admins.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_history_db_connection():
    conn = sqlite3.connect('databases/history.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_figures():
    conn = sqlite3.connect('databases/historical_figures.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, birth_year, death_year, biography, notable_for, image FROM figures')
    figures = cursor.fetchall()
    conn.close()
    return figures


def get_figure_detail(figure_id):
    conn = sqlite3.connect('databases/historical_figures.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT f.id, f.name, f.birth_year, f.death_year, f.biography, f.notable_for, f.image, d.detail
    FROM figures f
    JOIN figure_detail d ON f.id = d.figure_id
    WHERE f.id = ?
    ''', (figure_id,))
    figure = cursor.fetchone()
    conn.close()
    return figure


def add_figure_to_db(name, birth_year, death_year, biography, notable_for, image, detail):
    conn = sqlite3.connect('databases/historical_figures.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO figures (name, birth_year, death_year, biography, notable_for, image)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, birth_year, death_year, biography, notable_for, image))
    figure_id = cursor.lastrowid
    cursor.execute('''
    INSERT INTO figure_detail (figure_id, detail)
    VALUES (?, ?)
    ''', (figure_id, detail))

    conn.commit()
    conn.close()


def update_figure_in_db(figure_id, name, birth_year, death_year, biography, notable_for, image, detail):
    conn = sqlite3.connect('databases/historical_figures.db')
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE figures
    SET name = ?, birth_year = ?, death_year = ?, biography = ?, notable_for = ?, image = ?
    WHERE id = ?
    ''', (name, birth_year, death_year, biography, notable_for, image, figure_id))

    cursor.execute('''
    UPDATE figure_detail
    SET detail = ?
    WHERE figure_id = ?
    ''', (detail, figure_id))

    conn.commit()
    conn.close()
