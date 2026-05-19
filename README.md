# kopisha ~ Copy & Paste

*Python Flask App*

A simple clipboard relay for use during online training sessions.
The tutor pastes text (URLs, commands, code snippets) and learners
can retrieve it on demand - avoiding copy/paste issues with VM environments.

## Usage

### Tutor
- Visit `paste.qaalabs.com/{TUTOR_PATH}`
- Paste your text and click Publish
- Click Clear to blank the learner screen

### Learner
- Visit `paste.qaalabs.com`
- Click Refresh to get the latest text
- Select all and copy into your VM

## Routes

| Route | Who | What |
|---|---|---|
| `/` | Learner | Shows current clip |
| `/clip` | Learner JS | Returns current clip as JSON |
| `/{TUTOR_PATH}` | Tutor | Paste and publish |
| `/health` | Anyone | Service health and version |

## Local Development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_DEBUG=true
python app.py
```

## Environment Variables

| Variable | Purpose | Default |
|---|---|---|
| `SECRET_KEY` | Flask session key | `fallback-for-development` |
| `TUTOR_PATH` | Secret tutor URL path | `paste-dev` |

## Deployment

```bash
./bin/deploy.sh
```

Deploys to Google Cloud Run. Requires:
- `~/.flask_secret_key` - Flask secret key
- `~/.kopisha_tutor_path` - Tutor URL path
- GCP service account key at `~/.gcp-keys/{PROJECT_ID}-key.json`

## Health Check

`/health` returns service name, status, and version.

## Notes

- No database - current clip stored in memory only
- Scales to zero when idle - free tier friendly
- Text only - max 1000 characters per clip
- Single instance deployment - no state sync issues

