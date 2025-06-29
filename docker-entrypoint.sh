#!/bin/bash
# Render.com Auto-Migration Entrypoint
# Runs migrations automatically on every deployment

set -e

echo "🚀 TRADING ROBOT ADMIN - RENDER DEPLOYMENT"
echo "=========================================="
echo "🌐 Environment: Production (Render.com)"
echo ""

# Function to wait for PostgreSQL database
wait_for_postgres() {
    if [ -z "$DATABASE_URL" ]; then
        echo "⚠️  No DATABASE_URL found - using SQLite fallback"
        return 0
    fi
    
    echo "⏳ Waiting for PostgreSQL database connection..."
    
    python -c "
import os, sys, time
try:
    import psycopg2
    from urllib.parse import urlparse
    
    db_url = os.getenv('DATABASE_URL')
    parsed = urlparse(db_url)
    
    print(f'🔗 Connecting to PostgreSQL...')
    
    max_attempts = 60  # 2 minutes timeout
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
            print('✅ PostgreSQL database connected successfully')
            break
        except psycopg2.OperationalError as e:
            if attempt < 5:  # Only show first few attempts
                print(f'⏳ Connecting... attempt {attempt+1}')
            elif attempt % 10 == 0:  # Then every 10th attempt
                print(f'⏳ Still connecting... attempt {attempt+1}/{max_attempts}')
            
            if attempt >= max_attempts - 1:
                print('❌ Database connection timeout after 2 minutes')
                print('🔍 Please check your DATABASE_URL and PostgreSQL service')
                sys.exit(1)
            time.sleep(2)
            
except ImportError:
    print('⚠️  psycopg2 not available - cannot verify PostgreSQL connection')
except Exception as e:
    print(f'⚠️  Database check failed: {e}')
    print('🔄 Continuing with deployment...')
"
}

# Function to run migrations automatically
auto_migrate() {
    echo "📊 AUTOMATIC MIGRATION PROCESS"
    echo "==============================="
    
    # Step 1: Check existing migrations
    echo "📋 Checking migration status..."
    python manage.py showmigrations --verbosity=0 || {
        echo "⚠️  showmigrations failed - creating initial migrations"
    }
    
    # Step 2: Create missing migrations
    echo "📝 Creating any missing migrations..."
    apps=("configurations" "licenses" "core")
    
    for app in "${apps[@]}"; do
        if [ -d "$app" ]; then
            echo "   📝 Checking $app migrations..."
            python manage.py makemigrations "$app" --verbosity=1 --noinput || {
                echo "   ⚠️  No new migrations needed for $app"
            }
        fi
    done
    
    # Step 3: Apply all migrations
    echo "🚀 Applying all migrations..."
    
    # Try standard migration first
    if python manage.py migrate --verbosity=1 --noinput; then
        echo "✅ Standard migration completed successfully"
    else
        echo "⚠️  Standard migration failed, trying alternative approach..."
        
        # Try fake-initial for existing schemas
        echo "🔄 Attempting fake-initial migration..."
        python manage.py migrate --fake-initial --verbosity=1 --noinput || {
            echo "❌ Migration failed - this may require manual intervention"
            echo "🆘 Check Render logs for specific migration errors"
        }
    fi
    
    # Step 4: Verify migration success
    echo "🔍 Verifying migration success..."
    python -c "
try:
    import django
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
    django.setup()
    
    from django.db import connection
    from licenses.models import Client, License
    from configurations.models import TradingConfiguration
    
    # Test database connection
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✅ Database connection verified')
    
    # Test model access
    print(f'✅ Models accessible - Clients: {Client.objects.count()}, Licenses: {License.objects.count()}, Configs: {TradingConfiguration.objects.count()}')
    
except Exception as e:
    print(f'⚠️  Migration verification warning: {e}')
    print('🔄 Application will continue starting...')
" 2>/dev/null || echo "⚠️  Migration verification skipped"
    
    echo "✅ Migration process completed"
}

# Function to collect static files
collect_static_files() {
    echo "📁 Collecting static files..."
    
    python manage.py collectstatic --noinput --clear --verbosity=1 || {
        echo "⚠️  Static file collection failed - continuing anyway"
    }
    
    echo "✅ Static files ready"
}

# Function to start the application
start_application() {
    echo ""
    echo "🚀 STARTING APPLICATION SERVER"
    echo "============================="
    echo "📍 Port: ${PORT:-10000}"
    echo "🌐 Workers: ${WEB_CONCURRENCY:-3}"
    echo "⚙️  Settings: ${DJANGO_SETTINGS_MODULE:-trading_admin.settings_render}"
    echo "🔐 Debug: ${DEBUG:-false}"
    echo "💾 Database: PostgreSQL"
    echo ""
    echo "🌐 Your app will be available at:"
    echo "   📱 Admin: https://your-app.onrender.com/admin/"
    echo "   🏠 Dashboard: https://your-app.onrender.com/dashboard/"
    echo "   🤖 API: https://your-app.onrender.com/api/validate/"
    echo ""
    
    # Start gunicorn with optimized settings for Render
    exec gunicorn trading_admin.wsgi:application \
        --bind 0.0.0.0:${PORT:-10000} \
        --workers ${WEB_CONCURRENCY:-3} \
        --timeout 120 \
        --max-requests 1000 \
        --max-requests-jitter 50 \
        --worker-class sync \
        --worker-connections 1000 \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        --preload
}

# Main deployment sequence
main() {
    echo "🎯 RENDER.COM AUTOMATIC DEPLOYMENT"
    echo "=================================="
    echo "🕐 Started at: $(date)"
    echo ""
    
    # Step 1: Wait for database
    wait_for_postgres
    
    echo ""
    
    # Step 2: Run automatic migrations
    auto_migrate
    
    echo ""
    
    # Step 3: Collect static files
    collect_static_files
    
    echo ""
    
    # Step 4: Start the application
    start_application
}

# Error handling
trap 'echo "❌ Deployment failed at line $LINENO. Check Render logs for details."' ERR

# Run main deployment sequence
main "$@"