# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pip requirements
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the project
COPY . /app/

# Set Django settings module for Railway
ENV DJANGO_SETTINGS_MODULE=trading_admin.settings_railway

# Expose port (Railway sets $PORT)
EXPOSE 8000

# Run migrations, collect static files, then start Gunicorn
CMD bash -c "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn trading_admin.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120"
