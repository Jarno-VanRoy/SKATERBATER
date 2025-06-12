# Use a small, supported Python runtime
FROM python:3.13-slim

# Set a working directory
WORKDIR /app

# Copy only requirements first (for better layer caching)
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# If you need FLASK_APP/FLASK_ENV set, you can uncomment these:
# ENV FLASK_APP=run.py
# ENV FLASK_ENV=production

# Expose the port Gunicorn will serve on
EXPOSE 8000

# On container start:
# 1. upgrade the database to the latest migration
# 2. seed the tricks table (won't duplicate existing rows)
# 3. exec gunicorn to run your Flask app
ENTRYPOINT ["sh", "-c", "\
    flask db upgrade && \
    python seed_tricks.py && \
    exec gunicorn --workers 4 --threads 4 --bind 0.0.0.0:8000 run:app\
"]
