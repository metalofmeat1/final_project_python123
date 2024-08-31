# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, request, flash, redirect, url_for, session
import sqlite3
import json
app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key'

correct_answers = {
    'q1': 'c',
    'q2': 'a',
    'q3': 'c',
    'q4': 'c',
    'q5': 'c',
    'q6': 'd',
    'q7': 'a',
    'q8': 'a',
    'q9': 'b',
    'q10': 'd',
    'q11': 'b',
    'q12': 'b',
    'q13': 'b',
    'q14': 'c',
    'q15': 'a'
}

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


@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        username = request.form.get('username')
        score = 0
        for question, correct_answer in correct_answers.items():
            user_answer = request.form.get(question)
            print(user_answer)
            if user_answer == correct_answer:
                score += 1
        insert_to_db(username, score)
        return render_template('test_leaders.html')
    return render_template('test.html')


# users = {}

def init_score():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS leaders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        result INTEGER NOT NULL
                      )''')
    conn.commit()
    conn.close()



def insert_to_db(username, score):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute(''' INSERT INTO leaders (name, result) VALUES(?, ?) ''', (username, score))
    connection.commit()
    connection.close()


@app.route('/test_leaders', methods=['GET'])
def test_leaders():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leaders")
        champs = cursor.fetchall()
    print(champs)
    return render_template('test_leaders.html', champs=champs)


if __name__ == '__main__':
    app.run(debug=True)
