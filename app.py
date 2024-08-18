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
                        longitude REAL,
                        category TEXT  
                      )''')
    conn.commit()
    conn.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/events', methods=['GET'])
def get_events():
    year = request.args.get('year')
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE date LIKE ?", (f'{year}%',))
    events = cursor.fetchall()
    conn.close()
    return jsonify(events)

@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    event = cursor.fetchone()
    conn.close()
    return jsonify(event)


@app.route('/api/add_event', methods=['POST'])
def add_event():
    data = request.json
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO events (name, description, date, latitude, longitude, category) VALUES (?, ?, ?, ?, ?, ?)",
        (data['name'], data['description'], data['date'], data['latitude'], data['longitude'], data['category']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 201


@app.route('/api/search', methods=['GET'])
def search_events():
    query = request.args.get('query', '')
    filter = request.args.get('filter', '')

    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()

    sql_query = "SELECT * FROM events WHERE name LIKE ?"
    params = [f'%{query}%']

    if filter:
        sql_query += " AND category = ?"
        params.append(filter)

    cursor.execute(sql_query, params)
    events = cursor.fetchall()
    conn.close()

    return jsonify(events)


@app.route('/events')
def events():
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()
    conn.close()
    return render_template('events.html', events=events)


@app.route('/events/<int:event_id>')
def event_detail(event_id):
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    event = cursor.fetchone()
    conn.close()
    return render_template('event_details.html', event=event)



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
