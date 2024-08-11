from flask import Flask, render_template, jsonify

app = Flask(__name__)

test_data = {
    "events": [
        {
            "year": 1799,
            "location": [50.4501, 30.5234], 
            "title": "Тест",
            "description": "Опис",
            "media": {
                "image": "battle_kyiv.jpg",
                "video": "battle_kyiv.mp4"
            }
        },
        {
            "startYear": 1900,
            "endYear": 1945,
            "location": [51.9194, 19.1451], 
            "title": "Тест термінів",
            "description": "Нова подія з терміном",
            "media": {
                "image": "ww2.jpg",
                "video": "ww2.mp4"
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
