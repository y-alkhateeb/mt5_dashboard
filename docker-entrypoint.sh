#!/bin/bash
# Docker entrypoint script for Trading Robot Admin - Pure Docker Deployment

set -e

echo "🐳 TRADING ROBOT ADMIN - DOCKER DEPLOYMENT"
echo "=========================================="
echo "🚀 Starting Trading Robot Admin on Render.com"
echo ""

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

try:
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
except Exception as e:
    print(f'⚠️  Database connection check failed: {e}')
    print('🔄 Continuing anyway...')
"
}

# Function to run Django setup
setup_django() {
    echo "🔧 Setting up Django application..."
    
    # Run database migrations
    echo "📊 Running database migrations..."
    python manage.py migrate --noinput
    
    # Reset and setup admin user with correct credentials
    echo "👤 Setting up admin user..."
    python manage.py reset_and_setup \
        --username yousef \
        --password admin123123 \
        --email yousef@tradingadmin.com \
        --skip-migrations \
        --force
    
    # Collect static files if not already done
    echo "📁 Collecting static files..."
    python manage.py collectstatic --noinput --clear
    
    # Create sample data if database is empty
    echo "📊 Setting up sample data..."
    python -c "
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
django.setup()

from licenses.models import License
from configurations.models import TradingConfiguration

try:
    if License.objects.count() == 0 and TradingConfiguration.objects.count() == 0:
        print('📊 Creating sample data...')
        from django.core.management import call_command
        call_command('create_sample_data', '--clients', '3')
        print('✅ Sample data created')
    else:
        print('✅ Data already exists, skipping sample data creation')
except Exception as e:
    print(f'⚠️  Sample data setup skipped: {e}')
" 2>/dev/null || echo "⚠️  Sample data setup skipped"
    
    echo "✅ Django setup completed"
}

# Function to start the application
start_app() {
    echo "🚀 Starting application server..."
    echo "📍 Port: ${PORT:-10000}"
    echo "🌐 Workers: ${WEB_CONCURRENCY:-3}"
    echo "⚙️  Timeout: 120 seconds"
    echo "🔧 Settings: ${DJANGO_SETTINGS_MODULE}"
    echo ""
    
    exec gunicorn trading_admin.wsgi:application \
        --bind 0.0.0.0:${PORT:-10000} \
        --workers ${WEB_CONCURRENCY:-3} \
        --timeout 120 \
        --max-requests 1000 \
        --max-requests-jitter 50 \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        --preload \
        --worker-class sync
}

# Function to show startup summary
show_summary() {
    echo "📋 STARTUP SUMMARY"
    echo "=================="
    echo "🌐 Environment: ${DJANGO_SETTINGS_MODULE}"
    echo "🔐 Debug Mode: ${DEBUG:-false}"
    echo "💾 Database: ${DATABASE_URL:+Connected}" 
    echo "📁 Static Root: ${STATIC_ROOT:-/app/staticfiles}"
    echo "👤 Admin User: yousef"
    echo "🔑 Admin Password: admin123123"
    echo "📧 Admin Email: yousef@tradingadmin.com"
    echo "🌐 URLs:"
    echo "   📱 Admin: https://your-app.onrender.com/admin/"
    echo "   🏠 Dashboard: https://your-app.onrender.com/dashboard/"
    echo "   🤖 API: https://your-app.onrender.com/api/validate/"
    echo "=================="
}

# Main execution function
main() {
    # Wait for database if DATABASE_URL is provided
    if [ ! -z "$DATABASE_URL" ]; then
        wait_for_db
        setup_django
    else
        echo "⚠️  No DATABASE_URL found, skipping database setup"
        echo "🔧 Collecting static files only..."
        python manage.py collectstatic --noinput --clear
    fi
    
    # Show summary
    show_summary
    
    # Start the application
    start_app
}

# Run main function with all arguments
main "$@"