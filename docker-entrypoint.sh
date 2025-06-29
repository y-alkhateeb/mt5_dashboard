#!/bin/bash
# Docker entrypoint script for Trading Robot Admin

set -e

echo "🚀 Starting Trading Robot Admin on Render.com"
echo "=============================================="

# Function to wait for database
wait_for_db() {
    echo "⏳ Waiting for database connection..."
    
    if [ -z "$DATABASE_URL" ]; then
        echo "⚠️  DATABASE_URL not set, skipping database wait"
        return 0
    fi
    
    python -c "
import os, sys, time, psycopg2
from urllib.parse import urlparse

db_url = os.getenv('DATABASE_URL')
parsed = urlparse(db_url)
db_config = {
    'host': parsed.hostname,
    'port': parsed.port or 5432,
    'user': parsed.username,
    'password': parsed.password,
    'dbname': parsed.path[1:]
}

max_attempts = 30
for attempt in range(max_attempts):
    try:
        conn = psycopg2.connect(**db_config)
        conn.close()
        print('✅ Database connection successful')
        break
    except psycopg2.OperationalError:
        print(f'⏳ Database not ready, attempt {attempt+1}/{max_attempts}')
        if attempt >= max_attempts - 1:
            print('❌ Database connection failed')
            sys.exit(1)
        time.sleep(2)
"
}

# Function to run Django setup
setup_django() {
    echo "🔧 Setting up Django application..."
    
    echo "📊 Running database migrations..."
    python manage.py migrate --noinput
    
    echo "👤 Setting up admin user..."
    python manage.py reset_and_setup \
        --username yousef \
        --password admin123123 \
        --email admin@example.com \
        --force 2>/dev/null || true
    
    echo "📋 Setting up sample data..."
    python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
django.setup()

from licenses.models import License
from configurations.models import TradingConfiguration

if License.objects.count() == 0 and TradingConfiguration.objects.count() == 0:
    print('📊 Creating sample data...')
    try:
        from django.core.management import call_command
        call_command('create_sample_data', '--clients', '3')
        print('✅ Sample data created')
    except Exception as e:
        print(f'⚠️  Sample data creation skipped: {e}')
else:
    print('✅ Data exists, skipping sample data creation')
" 2>/dev/null || echo "⚠️  Sample data setup skipped"
}

# Function to start the application
start_app() {
    echo "🚀 Starting application server..."
    echo "📍 Port: ${PORT:-10000}"
    echo "🌐 Workers: ${WEB_CONCURRENCY:-3}"
    
    exec gunicorn trading_admin.wsgi:application \
        --bind 0.0.0.0:${PORT:-10000} \
        --workers ${WEB_CONCURRENCY:-3} \
        --timeout 120 \
        --max-requests 1000 \
        --max-requests-jitter 50 \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        --preload
}

# Main execution
main() {
    if [ ! -z "$DATABASE_URL" ]; then
        wait_for_db
        setup_django
    else
        echo "⚠️  No DATABASE_URL found, skipping database setup"
    fi
    
    start_app
}

# Run main function
main "$@"
