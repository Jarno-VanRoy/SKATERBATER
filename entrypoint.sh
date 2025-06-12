#!/usr/bin/env sh
set -e

# ensure the Flask CLI can find your app
export FLASK_APP=run.py

# 1. Migrate the DB
flask db upgrade

# 2. Seed the DB (seed_tricks.py already skips existing tricks)
python seed_tricks.py

# 3. Start the app
exec gunicorn --workers 4 --threads 4 --bind 0.0.0.0:8000 run:app
