from flask import Flask
import os

app = Flask(__name__, template_folder='./templates', static_folder='./static')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
app.config["SECRET_KEY"] = "my_key"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
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