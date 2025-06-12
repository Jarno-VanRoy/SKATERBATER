# Dockerfile
FROM python:3.13-slim

# 1. Set working dir
WORKDIR /app

# 2. Copy only requirements to leverage layer cache
COPY requirements.txt .

# 3. Install deps
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of your code, including entrypoint.sh
COPY . .

# 5. Make entrypoint.sh executable (done inside the container, no host chmod needed)
RUN chmod +x ./entrypoint.sh

# 6. Ensure flask CLI knows where to find your app
ENV FLASK_APP=run.py

# 7. Expose your port
EXPOSE 8000

# 8. Kick off your script (which runs migrations, seeds, then launches Gunicorn)
ENTRYPOINT ["./entrypoint.sh"]
