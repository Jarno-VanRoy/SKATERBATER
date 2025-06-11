import os
from flask import Flask, session
from werkzeug.middleware.proxy_fix import ProxyFix
from app import create_app

# ─── Create the Flask application ────────────────────────────────
app = create_app()

# ─── Trust X-Forwarded headers when behind a proxy ───────────────
# (Render, Heroku, NGROK, etc.)
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,    # trust X-Forwarded-For
    x_proto=1,  # trust X-Forwarded-Proto
    x_host=1    # trust X-Forwarded-Host
)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=(os.getenv('FLASK_ENV') != 'production'),
        use_reloader=True
    )
