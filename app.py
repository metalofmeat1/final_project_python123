import functools
import json
import logging
from flask import Flask, render_template, jsonify, request, send_from_directory, redirect, url_for, session, flash, \
    abort
from flask import Flask, render_template, jsonify, request, send_from_directory, redirect, url_for, Response, abort
from werkzeug.utils import secure_filename
import sqlite3
import os
import subprocess

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
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config["SECRET_KEY"] = "my_key"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/uploads'


def role_required(required_role):
    def decorator(f):
        @functools.wraps(f)
        def wrapped_function(*args, **kwargs):
            user_role = session.get('role')
            if user_role != required_role:
                abort(403)
            return f(*args, **kwargs)
        return wrapped_function
    return decorator


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)

    flash('Ви успішно вийшли з системи.', 'success')
    return redirect(url_for('login'))


def get_db_connection():
    conn = sqlite3.connect('./database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/register', methods=['GET', 'POST'])
@role_required('super_admin')
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO admins (email, username, password, role) VALUES (?, ?, ?, ?)",
                       (email, username, password, role))
        conn.commit()
        conn.close()

        flash('You have successfully registered!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE username = ? AND password = ?",
                       (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('index') + "?success_login=true")
        else:
            flash('Incorrect username or password.', 'danger')

    return render_template('login.html')


@app.route('/change_password', methods=['GET', 'POST'])
@role_required('admin')
@role_required('super_admin')
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT password FROM users WHERE id = ?", (session['user_id'],))
        user = cursor.fetchone()

        if user and user['password'] == current_password:
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, session['user_id']))
            conn.commit()
            flash('Password successfully changed!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Incorrect current password.', 'danger')

        conn.close()

    return render_template('change_password.html')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        year = request.args.get('year')
        conn = sqlite3.connect('history2.db')
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
                'image': f'/uploads/{event[6]}' if event[6] else None
            })

        return jsonify(events_list)
    except Exception as e:
        logging.error(f'Error fetching event: {e}')
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    try:
        conn = sqlite3.connect('history2.db')
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
        if 'image' not in request.files or request.files['image'].filename == '':
            return jsonify({"status": "error", "message": "No image file"}), 400

        file = request.files['image']
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        data = request.form
        conn = sqlite3.connect('history2.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO events (name, description, date, latitude, longitude, image) VALUES (?, ?, ?, ?, ?, ?)",
            (data['name'], data['description'], data['date'], data['latitude'], data['longitude'], filename))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"}), 201
    except Exception as e:
        logging.error(f'Error adding event: {e}')
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/api/search', methods=['GET'])
def search_events():
    try:
        query = request.args.get('query', '')

        conn = sqlite3.connect('history2.db')
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
        logging.error(f'Error searching events: {e}')
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/events')
def events_page():
    try:
        conn = sqlite3.connect('history2.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events")
        events = cursor.fetchall()
        conn.close()
        return render_template('events.html', events=events)
    except Exception as e:
        logging.error(f'Error fetching events: {e}')
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/event/<int:event_id>')
def event_page(event_id):
    try:
        conn = sqlite3.connect('history2.db')
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


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def get_figures():
    conn = sqlite3.connect('historical_figures.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, birth_year, death_year, biography, notable_for, image FROM figures')
    figures = cursor.fetchall()
    conn.close()
    return figures


def get_figure_detail(figure_id):
    conn = sqlite3.connect('historical_figures.db')
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


@app.route('/figure_image/<int:figure_id>')
def figure_image(figure_id):
    figure = get_figure_detail(figure_id)
    if figure and figure[6]:
        return Response(figure[6], mimetype='image/jpeg')
    else:
        abort(404)


@app.route('/figure_detail/<int:figure_id>')
def figure_detail(figure_id):
    figure = get_figure_detail(figure_id)
    if not figure:
        abort(404)
    return render_template('figure_detail.html', figure=figure)


def add_figure_to_db(name, birth_year, death_year, biography, notable_for, image, detail):
    conn = sqlite3.connect('historical_figures.db')
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


@app.route('/add_figure', methods=['GET', 'POST'])
@role_required('admin')
@role_required('super_admin')
def add_figure():
    if request.method == 'POST':
        name = request.form['name']
        birth_year = request.form.get('birth_year')
        death_year = request.form.get('death_year')
        biography = request.form.get('biography')
        notable_for = request.form.get('notable_for')
        detail = request.form.get('detail')
        image = request.files['image'].read()

        add_figure_to_db(name, birth_year, death_year, biography, notable_for, image, detail)
        return redirect(url_for('gallery'))

    return render_template('add_figure.html')


@app.route('/edit_figure/<int:figure_id>', methods=['GET', 'POST'])
@role_required('super_admin')
def edit_figure(figure_id):
    if request.method == 'POST':
        name = request.form['name']
        birth_year = request.form.get('birth_year')
        death_year = request.form.get('death_year')
        biography = request.form.get('biography')
        notable_for = request.form.get('notable_for')
        detail = request.form.get('detail')
        image = request.files['image'].read() if 'image' in request.files else None

        update_figure_in_db(figure_id, name, birth_year, death_year, biography, notable_for, image, detail)
        return redirect(url_for('gallery'))

    figure = get_figure_detail(figure_id)
    if not figure:
        abort(404)
    return render_template('edit_figure.html', figure=figure)


def update_figure_in_db(figure_id, name, birth_year, death_year, biography, notable_for, image, detail):
    conn = sqlite3.connect('historical_figures.db')
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


@app.route('/delete_figure/<int:figure_id>', methods=['POST'])
@role_required('admin')
@role_required('super_admin')
def delete_figure(figure_id):
    try:
        conn = sqlite3.connect('historical_figures.db')
        cursor = conn.cursor()

        cursor.execute('DELETE FROM figure_detail WHERE figure_id = ?', (figure_id,))
        cursor.execute('DELETE FROM figures WHERE id = ?', (figure_id,))

        conn.commit()
        conn.close()

        return redirect(url_for('gallery'))
    except Exception as e:
        app.logger.error(f'Error deleting figure: {e}')
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/gallery')
def gallery():
    figures = get_figures()
    return render_template('gallery.html', figures=figures)


@app.route('/figure/<int:figure_id>')
@role_required('admin')
@role_required('super_admin')
def figure_detail_view(figure_id):
    try:
        figure = get_figure_detail(figure_id)
        if figure:
            return render_template('figure_detail.html', figure=figure)
        else:
            return "Figure not found", 404
    except Exception as e:
        app.logger.error(f'Error fetching figure: {e}')
        return jsonify({"error": "Internal Server Error"}), 500



@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        username = request.form.get('username')
        score = 0
        for question, correct_answer in correct_answers.items():
            user_answer = request.form.get(question)
            if user_answer == correct_answer:
                score += 1
        insert_to_db(username, score)
        return redirect(url_for('test_leaders'))
    return render_template('test.html')


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
    return render_template('test_leaders.html', champs=champs)


if __name__ == '__main__':
    subprocess.run(['python', 'init_db.py'])
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
