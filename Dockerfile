# Use a small, supported Python runtime
FROM python:3.13-slim

# Set a working directory
WORKDIR /app

# Copy only requirements first (for better layer caching)
COPY requirements.txt .

# Install Python dependencies (we assume psycopg2-binary is in requirements)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port Gunicorn will serve on
EXPOSE 8000

# Launch with Gunicorn, pointing at the Flask app defined in run.py
CMD ["gunicorn", \
     "--workers", "4", \
     "--threads", "4", \
     "--bind", "0.0.0.0:8000", \
     "run:app"]
