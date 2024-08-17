from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)

def get_events_from_db():
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, year, start_year, end_year, location_lat, location_lng, title, description, image, video
        FROM events
    ''')
    rows = cursor.fetchall()
    conn.close()

    events = []
    for row in rows:
        event = {
            "year": row[1] if row[1] is not None else None,
            "startYear": row[2] if row[2] is not None else None,
            "endYear": row[3] if row[3] is not None else None,
            "location": [row[4], row[5]],
            "title": row[6],
            "description": row[7],
            "media": {
                "image": row[8],
                "video": row[9]
            }
        }
        events.append(event)
    
    return {"events": events}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    data = get_events_from_db()
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
