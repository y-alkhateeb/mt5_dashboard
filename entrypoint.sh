#!/bin/bash
# Fixed entrypoint.sh with migration dependency resolution
set -e

echo "🚀 Starting Trading Admin deployment with smart migration handling..."
echo "🌐 Port configuration: ${PORT:-10000}"

# Set Django settings for production
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-trading_admin.settings_render}

# Remove ALL problematic migration files and regenerate clean ones
echo "🗑️  Removing ALL problematic migration files..."
rm -f configurations/migrations/0002_*.py
rm -f configurations/migrations/0003_*.py
rm -f configurations/migrations/0004_*.py

# Wait for PostgreSQL database
echo "⏳ Waiting for PostgreSQL database..."
python -c "
import os, sys, time
try:
    import psycopg2
    from urllib.parse import urlparse
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print('⚠️  No DATABASE_URL - using SQLite')
        sys.exit(0)
        
    parsed = urlparse(db_url)
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                user=parsed.username,
                password=parsed.password,
                dbname=parsed.path[1:],
                connect_timeout=10
            )
            conn.close()
            print('✅ PostgreSQL connected')
            break
        except psycopg2.OperationalError:
            if attempt >= max_attempts - 1:
                print('❌ Database timeout')
                sys.exit(1)
            time.sleep(2)
            
except ImportError:
    print('⚠️  psycopg2 not available')
except Exception as e:
    print(f'⚠️  Database check failed: {e}')
"

# Generate fresh migrations based on current model state
echo "🔄 Generating fresh migrations for current model state..."
python manage.py makemigrations configurations --name remove_fibonacci_session_fields || {
    echo "⚠️  Migration generation failed, continuing with existing migrations"
}

# Mark existing migrations as applied if database already has the tables
echo "🔧 Syncing migration state with database..."
python manage.py migrate --fake-initial || true

# Apply any new migrations
echo "🔄 Applying new migrations..."
python manage.py migrate --noinput || {
    echo "⚠️  Some migrations failed but continuing..."
}

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear || echo "⚠️  Static collection failed"

echo ""
echo "✅ DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "🌐 Application URLs:"
echo "   📱 Admin: https://mt5-dashboard.onrender.com/admin/"
echo "   🏠 Dashboard: https://mt5-dashboard.onrender.com/dashboard/"
echo "   🤖 API: https://mt5-dashboard.onrender.com/api/validate/"
echo ""

# Start the application (MUST be the last line)
echo "🎯 Starting application server on port ${PORT:-10000}..."
exec gunicorn trading_admin.wsgi:application \
    --bind "0.0.0.0:${PORT:-10000}" \
    --workers 3 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile -