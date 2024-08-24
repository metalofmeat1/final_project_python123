from flask import Flask, render_template, jsonify, request
import sqlite3

app = Flask(__name__)

def fetch_events(period_id=None, search_term=None):
    """Fetches historical events from the database with optional filters."""
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()

    query = '''
        SELECT id, period_id, year, start_year, end_year, location_lat, location_lng, title, description, image, video
        FROM historical_events
    '''
    conditions = []
    params = []

    if period_id:
        conditions.append("period_id = ?")
        params.append(period_id)

    if search_term:
        conditions.append("title LIKE ?")
        params.append(f"%{search_term}%")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    events = []
    for row in rows:
        event = {
            "period_id": row[1],
            "year": row[2] if row[2] is not None else None,
            "startYear": row[3] if row[3] is not None else None,
            "endYear": row[4] if row[4] is not None else None,
            "location": [row[5], row[6]],
            "title": row[7],
            "description": row[8],
            "media": {
                "image": row[9],
                "video": row[10]
            }
        }
        events.append(event)

    return {"events": events}

def fetch_periods():
    """Fetches historical periods from the database."""
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, name FROM historical_periods')
    periods = cursor.fetchall()

    conn.close()

    return [{"id": row[0], "name": row[1]} for row in periods]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    period_id = request.args.get('period_id')
    search_term = request.args.get('search')
    data = fetch_events(period_id=period_id, search_term=search_term)
    return jsonify(data)

@app.route('/api/periods')
def get_periods():
    periods = fetch_periods()
    return jsonify({"periods": periods})

if __name__ == '__main__':
    app.run(debug=True)
