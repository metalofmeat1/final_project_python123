from flask import Flask

app = Flask(__name__, template_folder='./templates', static_folder='./static')
app.config['UPLOAD_FOLDER'] = 'app/uploads'
app.config["SECRET_KEY"] = "my_key"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
