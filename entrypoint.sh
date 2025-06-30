#!/bin/sh
set -e

echo "🚀 Starting Trading Admin deployment..."
echo "🌐 Port configuration: ${PORT:-10000}"

# ... existing migration code ...



echo "Running database migrations..."
exec rm -rf licenses/migrations/ configurations/migrations/ 2>/dev/null
# For Django:
echo "Running database migrations..."
python manage.py makemigrations licenses
python manage.py makemigrations configurations
python manage.py migrate --noinput


echo "🎯 Starting application server on port ${PORT:-10000}..."
exec gunicorn trading_admin.wsgi:application \
    --bind "0.0.0.0:${PORT:-10000}" \
    --workers 3 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --log-level info

echo "Starting application..."
exec "$@" # This executes the command passed as CMD in the Dockerfile