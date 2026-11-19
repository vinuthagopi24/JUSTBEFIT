# syntax=docker/dockerfile:1
FROM python:3.10-slim

# Prevent Python from writing .pyc and buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Initialize DB and seed baseline if not present
RUN python seed_data.py

EXPOSE 5000

# Run production server using Waitress or Gunicorn
CMD ["python", "serve.py"]
