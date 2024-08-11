from flask import Flask, render_template, jsonify


app = Flask(__name__)

test_data = {
  "events": [
    {
      "year": 1000,
    #   Координати мітки.
      "location": [50.4501, 30.5234], 
      "title": "Тест",
      "description": "Опис",
    #   Можна буде прикріпити картинки або відео, якщо в майбутньому це буде потрібно 
      "media": {
        "image": "battle_kyiv.jpg",
        "video": "battle_kyiv.mp4"

      }
    }
  ]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    return jsonify(test_data)

if __name__ == '__main__':
    app.run(debug=True)