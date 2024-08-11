from flask import Flask, render_template, jsonify, request
import sqlite3

app = Flask(__name__)


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


@app.route('/')
def index():
    return render_template('index.html')


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


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
