FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY backend/ ./backend/

# Set working directory to backend
WORKDIR /app/backend

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose port
EXPOSE 8080

# Remove local dev database so Cloud Run starts fresh
RUN rm -f db.sqlite3

# Collect static files and create fresh database
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate --noinput

# Create media directory
RUN mkdir -p media/generated_content

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "--timeout", "0", "--error-logfile", "-", "--access-logfile", "-", "odyssey_web.wsgi:application"]
