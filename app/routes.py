import logging
import sqlite3

from flask import render_template, jsonify, request, redirect, url_for, session, flash, abort, Response, \
    send_from_directory
from werkzeug.utils import secure_filename
import os
from final_project_python123.app.config import app
from final_project_python123.app.utilities import role_required
from final_project_python123.app.work_with_db import get_db_connection, get_history_db_connection, get_figure_detail, \
    get_figures, update_figure_in_db, add_figure_to_db

from final_project_python123.app.config import correct_answers
from final_project_python123.app.work_with_db import insert_to_db


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE username = ? AND password = ?", (username, password))
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


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    flash('Ви успішно вийшли з системи.', 'success')
    return redirect(url_for('login'))


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


@app.route('/change_password', methods=['GET', 'POST'])
@role_required('admin', 'super_admin')
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


@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        year = request.args.get('year')
        conn = get_history_db_connection()
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
                'image': f'/{event[6]}' if event[6] else None
            })

        return jsonify(events_list)
    except Exception as e:
        logging.error(f'Error fetching event: {e}')
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    try:
        conn = get_history_db_connection()
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


@app.route('/event/<int:event_id>')
def event_page(event_id):
    try:
        conn = sqlite3.connect('databases/history.db')
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
        conn = get_history_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO events (name, description, date, latitude, longitude, image) VALUES (?, ?, ?, ?, ?, ?)",
            (data['name'], data['description'], data['date'], data['latitude'], data['longitude'], filename))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"}), 201
    except Exception as e:
        logging.error(f'Error adding event: {e}')
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500


@app.route('/api/search', methods=['GET'])
def search_events():
    try:
        query = request.args.get('query', '')
        if not query:
            return jsonify({"error": "Search query cannot be empty"}), 400

        conn = get_history_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE name LIKE ?", ('%' + query + '%',))
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
                'image': url_for('uploaded_file', filename=event[6]) if event[6] else None
            })

        return jsonify(events_list)
    except Exception as e:
        logging.error(f'Error searching events: {e}')
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


@app.route('/test_leaders', methods=['GET'])
def test_leaders():
    with sqlite3.connect('databases/users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leaders")
        champs = cursor.fetchall()
    return render_template('test_leaders.html', champs=champs)


@app.route('/figure_image/<int:figure_id>')
def figure_image(figure_id):
    figure = get_figure_detail(figure_id)
    if figure and figure[6]:
        return Response(figure[6], mimetype='image/jpeg')
    else:
        abort(404)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/edit_figure/<int:figure_id>', methods=['GET', 'POST'])
@role_required('admin', 'super_admin')
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


@app.route('/delete_figure/<int:figure_id>', methods=['POST'])
@role_required('admin', 'super_admin')
def delete_figure(figure_id):
    try:
        conn = sqlite3.connect('databases/historical_figures.db')
        cursor = conn.cursor()

        cursor.execute('DELETE FROM figure_detail WHERE figure_id = ?', (figure_id,))
        cursor.execute('DELETE FROM figures WHERE id = ?', (figure_id,))

        conn.commit()
        conn.close()

        return redirect(url_for('gallery'))
    except Exception as e:
        app.logger.error(f'Error deleting figure: {e}')
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/add_figure', methods=['GET', 'POST'])
@role_required('admin', 'super_admin')
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


@app.route('/gallery')
def gallery():
    figures = get_figures()
    return render_template('gallery.html', figures=figures)


@app.route('/figure/<int:figure_id>')
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