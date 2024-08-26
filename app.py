import logging
from flask import Flask, render_template, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3
import os
from db_starter import init_db

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        year = request.args.get('year')
        conn = sqlite3.connect('history.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE date LIKE ?", (f'{year}%',))
        events = cursor.fetchall()
        conn.close()

        events_list = []

        for event in events:
            events_list.append({
                'id': event[0],
                'name': event[1],
                'description': event[2],
                'date': event[3],
                'latitude': event[4],
                'longitude': event[5],
                'image': f'/uploads/{event[6]}'
            })

        return jsonify(events_list)
    except Exception as e:
        logging.error(f'Error fetching event: {e}')
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    try:
        conn = sqlite3.connect('history.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        event = cursor.fetchone()
        conn.close()

        if event:
            event_data = {
                'id': event[0],
                'name': event[1],
                'description': event[2],
                'date': event[3],
                'latitude': event[4],
                'longitude': event[5],
                'image': event[6] if event[6] else None
            }
            return jsonify(event_data)
        else:
            return jsonify({"error": "Event not found"}), 404
    except Exception as e:
        logging.error(f'Error fetching event: {e}')
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/api/add_event', methods=['POST'])
def add_event():
    try:
        # За сенсом коду, нам треба обов'язково додавати картинку у форму, чи воно нам треба? (Якщо не треба, то приберіть)
        if 'image' not in request.files:
            return jsonify({"status": "error", "message": "No image file"}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({"status": "error", "message": "No selected image"}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        data = request.form
        conn = sqlite3.connect('history.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO events (name, description, date, latitude, longitude, image) VALUES (?, ?, ?, ?, ?, ?)",
            (data['name'], data['description'], data['date'], data['latitude'], data['longitude'], filename))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"}), 201
    except Exception as e:
        logging.error(f'Error fetching event: {e}')
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/api/search', methods=['GET'])
def search_events():
    try:
        query = request.args.get('query', '')

        conn = sqlite3.connect('history.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE name LIKE ?", (f'%{query}%',))
        events = cursor.fetchall()
        conn.close()

        events_list = []
        for event in events:
            events_list.append({
                'id': event[0],
                'name': event[1],
                'description': event[2],
                'date': event[3],
                'latitude': event[4],
                'longitude': event[5],
                'image': event[6] if event[6] else None
            })

        return jsonify(events_list)
    except Exception as e:
        logging.error(f'Error fetching event: {e}')
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/events')
def events_page():
    try:
        conn = sqlite3.connect('history.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events")
        events = cursor.fetchall()
        conn.close()
        return render_template('events.html', events=events)
    except Exception as e:
        logging.error(f'Error fetching event: {e}')
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/event/<int:event_id>')
def event_page(event_id):
    try:
        conn = sqlite3.connect('history.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        event = cursor.fetchone()
        conn.close()

        if event:
            event_data = {
                'id': event[0],
                'name': event[1],
                'description': event[2],
                'date': event[3],
                'latitude': event[4],
                'longitude': event[5],
                'image': event[6] if event[6] else None
            }
            return render_template('event_detail.html', event=event_data)
        else:
            return "Event not found", 404
    except Exception as e:
        logging.error(f'Error fetching event: {e}')
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/submit_test', methods=['POST'])
def submit_test():
    data = request.json
    name = data['name']
    answer = data['answer']

    # Определение баллов на основе ответа #TODO: Прибрати коментарі 😒😒😒
    score = 0
    correct_answer = "Правильный ответ"
    if answer.strip().lower() == correct_answer.lower():
        score = 10

    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO test_results (name, answer, score) VALUES (?, ?, ?)",
        (name, answer, score)
    )
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/leaderboard')
def leaderboard():
    try:
        conn = sqlite3.connect('history.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, score FROM test_results ORDER BY score DESC")
        results = cursor.fetchall()
        conn.close()

        leaderboard = [{'name': row[0], 'score': row[1]} for row in results]
        return jsonify(leaderboard)
    except Exception as e:
        logging.error(f'Error fetching event: {e}')
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == '__main__':
    init_db()
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
