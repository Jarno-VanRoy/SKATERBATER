#!/usr/bin/env sh
set -e

# Make sure Flask knows where to find your app
export FLASK_APP=run.py

# 1️⃣ Apply any new Alembic migrations
echo "⏳ Running database migrations…"
flask db upgrade

# 2️⃣ Seed the tricks table (seed_tricks.py skips duplicates)
echo "⏳ Seeding tricks…"
python seed_tricks.py

# 3️⃣ Finally, hand off to Gunicorn
echo "🚀 Starting Gunicorn…"
exec gunicorn \
  --workers 4 \
  --threads 4 \
  --bind 0.0.0.0:8000 \
  run:app
