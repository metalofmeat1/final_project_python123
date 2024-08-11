print("Hello, PYTHON_1y_21_16_09_23_3")
print("Вова тут :)")
from flask import Flask, render_template, request, flash, redirect, url_for
app = Flask(__name__)
app.secret_key = 'secret_key'


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    search_query = request.form.get('query')
    return render_template('search.html', query=search_query)


if __name__ == '__main__':
    app.run(debug=True)
