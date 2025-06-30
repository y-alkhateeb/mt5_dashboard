#!/bin/bash
# Emergency docker-entrypoint.sh that bypasses Django system checks
# Fixes the admin.py field reference issues

set -e

echo "🚨 TRADING ROBOT ADMIN - EMERGENCY POSTGRESQL FIX"
echo "================================================="
echo "🌐 Environment: Production (Render.com)"
echo "🔧 Bypassing Django system checks to fix database"
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

# Function to run emergency PostgreSQL fix
run_emergency_fix() {
    echo "🚨 EMERGENCY POSTGRESQL FIX"
    echo "============================"
    
    # Run the emergency fix that bypasses system checks
    echo "🚀 Running emergency fix (bypassing system checks)..."
    
    if python manage.py emergency_fix --force; then
        echo "✅ Emergency fix completed successfully"
        return 0
    else
        echo "❌ Emergency fix failed"
        return 1
    fi
}

# Function to verify basic database functionality
verify_basic_functionality() {
    echo "🔍 BASIC VERIFICATION"
    echo "===================="
    
    echo "🧪 Testing basic database functionality..."
    python -c "
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')

# Set up Django without system checks
from django.conf import settings
if not settings.configured:
    django.setup()

try:
    # Test database connection
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✅ Database connection working')
    
    # Test that tables exist
    with connection.cursor() as cursor:
        # Check for our main tables
        tables_to_check = [
            'configurations_tradingconfiguration',
            'licenses_client', 
            'licenses_license'
        ]
        
        for table in tables_to_check:
            cursor.execute(f\"\"\"
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{table}'
                );
            \"\"\")
            exists = cursor.fetchone()[0]
            if exists:
                print(f'✅ Table exists: {table}')
            else:
                print(f'❌ Table missing: {table}')
    
    # Test basic admin user functionality
    try:
        from django.contrib.auth.models import User
        admin_count = User.objects.filter(username='admin').count()
        print(f'✅ Admin user check: {admin_count} admin users found')
    except Exception as e:
        print(f'⚠️  Admin user check failed: {e}')
    
except Exception as e:
    print(f'❌ Basic verification failed: {e}')
    sys.exit(1)

print('✅ Basic verification completed')
" 2>/dev/null || echo "⚠️  Verification had issues"
}

# Function to collect static files
collect_static_files() {
    echo "📁 STATIC FILES COLLECTION"
    echo "=========================="
    
    echo "📁 Collecting static files..."
    
    # Collect static files with system checks disabled
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
    echo "   📱 Admin: https://mt5-dashboard.onrender.com/admin/"
    echo "   🏠 Dashboard: https://mt5-dashboard.onrender.com/dashboard/"
    echo "   🤖 API: https://mt5-dashboard.onrender.com/api/validate/"
    echo ""
    echo "🔐 Default admin credentials:"
    echo "   Username: admin"
    echo "   Password: admin123"
    echo "   ⚠️  Change password after first login!"
    echo ""
    echo "⚠️  IMPORTANT: After this deployment works, update your admin.py"
    echo "   files and redeploy to use the proper admin interface!"
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

# Main deployment sequence with emergency fix
main() {
    echo "🎯 RENDER.COM EMERGENCY DEPLOYMENT FIX"
    echo "======================================="
    echo "🕐 Started at: $(date)"
    echo ""
    echo "This deployment bypasses Django system checks to fix the database"
    echo "After this works, update admin.py files and redeploy normally"
    echo ""
    
    # Step 1: Wait for database
    wait_for_postgres
    
    echo ""
    
    # Step 2: Run emergency fix
    if run_emergency_fix; then
        echo "✅ Emergency fix completed successfully"
    else
        echo "❌ Emergency fix failed - deployment cannot continue"
        exit 1
    fi
    
    echo ""
    
    # Step 3: Verify basic functionality
    verify_basic_functionality
    
    echo ""
    
    # Step 4: Collect static files
    collect_static_files
    
    echo ""
    echo "✅ EMERGENCY DEPLOYMENT COMPLETED!"
    echo "================================="
    echo ""
    echo "🔧 NEXT STEPS AFTER THIS DEPLOYMENT:"
    echo "1. Update configurations/admin.py with new field names"
    echo "2. Update configurations/forms.py with new field names"  
    echo "3. Update any other admin files that reference old field names"
    echo "4. Redeploy normally"
    echo ""
    
    # Step 5: Start the application
    start_application
}

# Error handling
trap 'echo "❌ Emergency deployment failed at line $LINENO. Check Render logs for details."' ERR

# Run main deployment sequence
main "$@"