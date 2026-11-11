# Hosting Guide — The Intern's Token

The challenge is a small Flask app with no external dependencies (no
database, no outbound network calls), so it can be hosted almost anywhere.
Verified instructions below.

## Option A — Docker (recommended, ~1 minute)

```bash
cd advanced-challenge/app
docker build -t gdg-ctf-jwt .
docker run -d -p 5000:5000 --name gdg-ctf-jwt gdg-ctf-jwt
```

Visit `http://<your-host>:5000/`. To stop/remove:

```bash
docker stop gdg-ctf-jwt && docker rm gdg-ctf-jwt
```

### Docker Compose (if you're hosting multiple challenges)

```yaml
services:
  jwt-challenge:
    build: ./advanced-challenge/app
    ports:
      - "5000:5000"
    restart: unless-stopped
```

## Option B — Bare metal / VM

```bash
cd advanced-challenge/app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Use a production WSGI server instead of the Flask dev server:
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

## Option C — PaaS (Render / Railway / Fly.io / Replit, etc.)

All of these can build directly from the included `Dockerfile`:

1. Push this repo (or just the `advanced-challenge/app` folder) to a Git
   repo.
2. Create a new "Web Service" / "App" on the platform, point it at the
   repo, and let it auto-detect the `Dockerfile` (or set the start command
   to `python app.py` / `gunicorn -w 2 -b 0.0.0.0:$PORT app:app` if the
   platform injects a `$PORT` env var — see note below).
3. Expose port 5000 (or whatever the platform requires).

**Port note:** some PaaS providers require binding to `$PORT` instead of a
hardcoded `5000`. If so, change the last line of `app.py` to:

```python
import os
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
```

## Firewall / isolation recommendations for event day

- Run one container per team/participant if you want isolated flags per
  team (trivial here since the app is stateless and fast to spin up).
- Rate-limit or put a reverse proxy (e.g. nginx/Caddy) in front if hosting
  publicly, to avoid accidental abuse from automated scanners.
- The app has no filesystem writes, no database, and no shell-out calls —
  there is no path to remote code execution even if someone probes beyond
  the intended `/admin` vulnerability, but standard container hygiene
  (non-root user — already set in the Dockerfile, read-only root FS,
  resource limits) is still good practice:

```bash
docker run -d -p 5000:5000 --read-only --tmpfs /tmp \
  --memory=128m --cpus=0.5 --name gdg-ctf-jwt gdg-ctf-jwt
```

## Resetting between teams/rounds

The app is fully stateless — nothing persists between requests except
what's inside each issued JWT. Restarting the container is all that's
needed to "reset" it; there's no database to wipe.
