# Use a small, supported Python runtime
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy only requirements first (for better layer caching)
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application
COPY . .

# Copy and make our entrypoint runnable
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Expose the port Gunicorn will serve on
EXPOSE 8000

# Use our script to migrate, seed, then launch Gunicorn
ENTRYPOINT ["./entrypoint.sh"]
