#!/bin/sh

# Optional: Wait for the database to be ready (e.g., for PostgreSQL)
# You might need to install 'netcat' in your Dockerfile: RUN apt-get update && apt-get install -y netcat-traditional
# while ! nc -z db 5432; do
#   echo "Waiting for database..."
#   sleep 1
# done
# echo "Database is up!"

echo "Running database migrations..."
# For Django:
python manage.py migrate --noinput

# For Flask (with Flask-Migrate/Alembic):
# flask db upgrade

# For Node.js (assuming a migration script):
# npm run migrate

echo "Starting application..."
exec "$@" # This executes the command passed as CMD in the Dockerfile