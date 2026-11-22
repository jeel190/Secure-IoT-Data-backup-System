# Dockerfile for Cloud VM / Container Deployment
FROM python:3.11-slim

LABEL maintainer="Vasani Jeel <24UG00241>"
LABEL assignment="18 - Secure IoT Data Backup System"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose HTTP port
EXPOSE 5000

ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/stats || exit 1

# Launch with Gunicorn for production or python for development
CMD ["python", "app.py"]
