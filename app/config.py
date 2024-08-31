from flask import Flask
import os

app = Flask(__name__, template_folder='./templates', static_folder='./static')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
app.config["SECRET_KEY"] = "my_key"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
