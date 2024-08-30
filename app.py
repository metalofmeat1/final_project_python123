# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, request, flash, redirect, url_for, session
import sqlite3
import json
app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key'


def init_db():
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        date TEXT,
                        latitude REAL,
                        longitude REAL
                      )''')
    conn.commit()
    conn.close()


def db():
    conn = sqlite3.connect('history_guys.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS history_guys (
                        id INTEGER PRIMARY KEY,
                        full_name TEXT NOT NULL,
                        picture TEXT,
                        bio TEXT
                      )''')
    conn.commit()
    return conn


def json_into_db():
    conn = db()
    cursor = conn.cursor()
    with open('historical_guys.json', 'r') as json_file:
        data = json.load(json_file)
        for guy in data:
            cursor.execute("INSERT INTO history_guys (full_name, picture, bio) VALUES (?, ?, ?)",
                           (guy['full_name'], guy['picture'], guy['bio']))
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    search_query = request.form.get('query')
    return render_template('index.html', query=search_query)


@app.route('/')
@app.route('/api/events', methods=['GET'])
def get_events():
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE date BETWEEN ? AND ?", (start_date, end_date))
    events = cursor.fetchall()
    conn.close()
    return jsonify(events)


@app.route('/api/add_event', methods=['POST'])
def add_event():
    data = request.json
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO events (name, description, date, latitude, longitude) VALUES (?, ?, ?, ?, ?)",
                   (data['name'], data['description'], data['date'], data['latitude'], data['longitude']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 201


@app.route('/historical_man', methods=['GET', 'POST'])
def historical_man():
    if request.method == 'POST':
        guy_id = request.form.get('id')
        session['data'] = guy_id
        return redirect(url_for('historical_man_details', guy_id=guy_id))
    return render_template('historical_man.html')


@app.route('/historical_man_details/')
def historical_man_details():
    guy_id = session['data']
    conn = db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history_guys WHERE full_name=?", (guy_id,))
    guy = cursor.fetchone()
    conn.close()
    guy_info = {
        "guy_id": guy[0],
        "full_name": guy[1],
        "picture": guy[2],
        "bio": guy[3]
    }
    if guy is not None:
        return render_template('historical_man_details.html', guy_info=guy_info)
    else:
        return f"На жаль ми нічого не знаємо про людину на ім'я {guy_id}"


if __name__ == '__main__':
    app.run(debug=True)
