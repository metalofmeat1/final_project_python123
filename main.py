from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_history_db_connection():
    conn = sqlite3.connect('history.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)",
                       (email, username, password))
        conn.commit()
        conn.close()

        flash('Вы успешно зарегистрировались!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?",
                       (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index') + "?success_login=true")
        else:
            flash('Неправильное имя пользователя или пароль.', 'danger')

    return render_template('login.html')


@app.route('/change_password', methods=['GET', 'POST'])
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
            flash('Пароль успешно изменен!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Неправильный текущий пароль.', 'danger')

        conn.close()

    return render_template('change_password.html')


@app.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в аккаунт.', 'warning')
        return redirect(url_for('login'))

    if 'avatar' not in request.files:
        flash('Файл не выбран.', 'danger')
        return redirect(url_for('index'))

    file = request.files['avatar']

    if file.filename == '':
        flash('Файл не выбран.', 'danger')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET avatar = ? WHERE id = ?", (filename, session['user_id']))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))
    else:
        flash('Недопустимый формат файла. Разрешены только png, jpg, jpeg, gif.', 'danger')
        return redirect(url_for('index'))


@app.route('/set_theme', methods=['POST'])
def set_theme():
    theme = request.form['theme']
    session['theme'] = theme
    return redirect(url_for('index'))


@app.route('/index')
def index():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в аккаунт.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute("SELECT id, username, avatar FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()

    success_login = request.args.get('success_login')

    return render_template('index.html', username=user['username'], user_avatar=user['avatar'], success_login=success_login)


@app.route('/api/events')
def get_events():
    year = request.args.get('year')
    conn = get_history_db_connection()
    events = conn.execute('SELECT * FROM events WHERE strftime("%Y", date) = ?', (year,)).fetchall()
    conn.close()

    events_list = []
    for event in events:
        events_list.append([event['id'], event['name'], event['description'], event['date'], event['latitude'], event['longitude']])

    return jsonify(events_list)


@app.route('/')
def main():
    return redirect(url_for('register'))


if __name__ == '__main__':
    app.run(debug=True)



