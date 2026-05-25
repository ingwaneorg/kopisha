from flask import Flask, render_template, request, jsonify
import os

# Import the version number
from version import __version__

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-for-development')

# The entire "database"
current_clip = {'text': '', 'links': []}
visitor_ips = set()

# Tutor path from environment variable
TUTOR_PATH = os.environ.get('TUTOR_PATH', 'paste-dev')

@app.route('/')
def home():
    return render_template('home.html', version=__version__)

@app.route('/qa')
def learner():
    return render_template('learner.html', clip=current_clip)

@app.route('/health')
def health():
    return jsonify({
        'service': 'kopisha',
        'status' : 'healthy',
        'version': __version__,
    })

@app.route('/clip')
def get_clip():
    global visitor_ips
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip:
        visitor_ips.add(ip.split(',')[0].strip())
    return jsonify(current_clip)

@app.route('/visitors')
def get_visitors():
    return jsonify({'count': len(visitor_ips)})

@app.route('/<path:tutor_path>', methods=['GET'])
def tutor(tutor_path):
    if tutor_path != TUTOR_PATH:
        return "Not found", 404
    return render_template('tutor.html', clip=current_clip)

@app.route('/<path:tutor_path>', methods=['POST'])
def publish(tutor_path):
    if tutor_path != TUTOR_PATH:
        return "Not found", 404
    global current_clip, visitor_ips
    visitor_ips = set()
    data = request.get_json()
    raw_links = data.get('links', [])
    current_clip = {
        'text': data.get('text', '').strip()[:1000],
        'links': [l.strip() for l in raw_links if l.strip()][:20],
    }
    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
 
