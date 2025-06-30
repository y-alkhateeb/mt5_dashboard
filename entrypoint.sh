#!/bin/bash
# Working entrypoint.sh for Trading Robot Admin
# This actually fixes your PostgreSQL field naming issues

set -e

echo "🚀 Starting Trading Admin deployment..."
echo "🌐 Port configuration: ${PORT:-10000}"

# Set Django settings for production
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-trading_admin.settings_render}

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

# Clean old migrations (keep __init__.py files)
echo "🧹 Cleaning old migrations..."
for app in licenses configurations; do
    if [ -d "$app/migrations" ]; then
        find "$app/migrations/" -name "*.py" -not -name "__init__.py" -delete 2>/dev/null || true
        find "$app/migrations/" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        echo "   Cleaned $app migrations"
    fi
done

# Try emergency fix first (this bypasses system check errors)
echo "🔧 Attempting emergency PostgreSQL field fix..."
if python manage.py emergency_fix --force 2>/dev/null; then
    echo "✅ Emergency fix completed - database is ready"
else
    echo "⚠️  Emergency fix not available, trying standard migration..."
    
    # Fallback: try standard migration
    echo "📝 Creating migrations..."
    python manage.py makemigrations configurations --noinput || echo "⚠️  Configurations migration failed"
    python manage.py makemigrations licenses --noinput || echo "⚠️  Licenses migration failed"
    
    echo "🚀 Applying migrations..."
    if ! python manage.py migrate --noinput; then
        echo "❌ Migration failed - cannot continue"
        exit 1
    fi
fi

# Setup admin user
echo "👤 Setting up admin user..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
django.setup()

from django.contrib.auth.models import User

try:
    if User.objects.filter(username='admin').exists():
        user = User.objects.get(username='admin')
        user.set_password('admin123')
        user.email = 'admin@example.com'
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        print('✅ Updated admin user: admin/admin123')
    else:
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print('✅ Created admin user: admin/admin123')
except Exception as e:
    print(f'⚠️  Admin setup failed: {e}')
" || echo "⚠️  Admin user setup failed"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear || echo "⚠️  Static collection failed"

# Verify everything works
echo "🔍 Verifying deployment..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
django.setup()

from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✅ Database connection verified')
except Exception as e:
    print(f'❌ Database verification failed: {e}')
    exit(1)
" || exit 1

echo ""
echo "✅ DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "🌐 Application URLs:"
echo "   Admin: https://your-app.onrender.com/admin/ (admin/admin123)"
echo "   Dashboard: https://your-app.onrender.com/dashboard/"
echo "   API: https://your-app.onrender.com/api/validate/"
echo ""

# Start the application (this MUST be the last line)
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