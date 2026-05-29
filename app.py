from flask import Flask, render_template, request, jsonify
import os

from version import __version__

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-for-development')

MAX_CLIP_CHARS = 1000
MAX_LINKS = 20

def parse_trainers():
    result = {}
    for entry in os.environ.get('TRAINERS', 'qa:paste-dev').split(','):
        entry = entry.strip()
        if ':' in entry:
            initials, secret = entry.split(':', 1)
            result[initials.strip()] = {
                'clip': {'text': '', 'links': []},
                'visitors': set(),
                'secret': secret.strip(),
            }
    return result

trainers = parse_trainers()

@app.route('/')
def home():
    return render_template('home.html', version=__version__)

@app.route('/health')
def health():
    return jsonify({'service': 'kopisha', 'status': 'healthy', 'version': __version__})

@app.route('/clip/<initials>')
def get_clip(initials):
    if initials not in trainers:
        return jsonify({'text': '', 'links': []}), 404
    t = trainers[initials]
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip:
        t['visitors'].add(ip.split(',')[0].strip())
    return jsonify(t['clip'])

@app.route('/visitors/<initials>')
def get_visitors(initials):
    if initials not in trainers:
        return jsonify({'count': 0}), 404
    return jsonify({'count': len(trainers[initials]['visitors'])})

@app.route('/<path:path>', methods=['GET', 'POST'])
def handle_path(path):
    # Learner view: path matches a trainer's initials
    if path in trainers:
        return render_template('learner.html', clip=trainers[path]['clip'], initials=path)

    # Tutor view: path matches a trainer's secret
    for initials, t in trainers.items():
        if path == t['secret']:
            if request.method == 'POST':
                t['visitors'] = set()
                data = request.get_json()
                raw_links = data.get('links', [])
                t['clip'] = {
                    'text': data.get('text', '').strip()[:MAX_CLIP_CHARS],
                    'links': [l.strip() for l in raw_links if l.strip()][:MAX_LINKS],
                }
                return jsonify({'success': True})
            return render_template('tutor.html', clip=t['clip'], initials=initials)

    return "Not found", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
