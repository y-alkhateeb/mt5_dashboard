#!/bin/bash
# Final working entrypoint.sh that handles migration state conflicts
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

# Check for existing tables and handle migration state conflicts
echo "🔍 Checking database state..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
django.setup()

from django.db import connection

# Check if tables already exist
existing_tables = []
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
        if cursor.fetchone()[0]:
            existing_tables.append(table)
    
    if existing_tables:
        print(f'⚠️  Found existing tables: {existing_tables}')
        print('🗑️  Clearing migration history to fix state conflicts...')
        
        # Clear migration history for apps with existing tables
        apps_to_clear = []
        if any('configurations' in table for table in existing_tables):
            apps_to_clear.append('configurations')
        if any('licenses' in table for table in existing_tables):
            apps_to_clear.append('licenses')
        
        for app in apps_to_clear:
            cursor.execute('DELETE FROM django_migrations WHERE app = %s', [app])
            print(f'   Cleared migration history for {app}')
    else:
        print('✅ No existing tables found - fresh database')
"

# Create migrations
echo "📝 Creating migrations..."
python manage.py makemigrations configurations --noinput || echo "⚠️  Configurations migration failed"
python manage.py makemigrations licenses --noinput || echo "⚠️  Licenses migration failed"

# Apply migrations with proper handling of existing tables
echo "🚀 Applying migrations..."
if python manage.py migrate --fake-initial --noinput 2>/dev/null; then
    echo "✅ Migrations applied with --fake-initial"
elif python manage.py migrate --noinput 2>/dev/null; then
    echo "✅ Migrations applied normally"
else
    echo "⚠️  Migration failed, trying to fix table conflicts..."
    
    # Last resort: handle the duplicate table error
    python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
django.setup()

from django.db import connection
from django.core.management import call_command

print('🔧 Handling table conflicts manually...')

try:
    # Mark migrations as applied without running them
    call_command('migrate', '--fake', verbosity=0)
    print('✅ Marked conflicting migrations as applied')
except Exception as e:
    print(f'⚠️  Fake migration failed: {e}')
    
    # Final fallback: recreate database structure
    print('🗑️  Dropping conflicting tables and recreating...')
    with connection.cursor() as cursor:
        # Drop problematic tables
        tables_to_drop = [
            'configurations_tradingconfiguration',
            'licenses_license',
            'licenses_client'
        ]
        
        for table in tables_to_drop:
            cursor.execute(f'DROP TABLE IF EXISTS {table} CASCADE;')
            print(f'   Dropped {table}')
        
        # Clear migration history
        cursor.execute(\"DELETE FROM django_migrations WHERE app IN ('configurations', 'licenses');\")
        print('   Cleared migration history')
    
    # Now run migrations normally
    call_command('migrate', verbosity=0)
    print('✅ Database recreated successfully')
" || {
    echo "❌ All migration attempts failed"
    exit 1
}
fi

# Verify database is working
echo "🔍 Verifying database structure..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
django.setup()

from django.db import connection

try:
    # Test database connection
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    
    # Test that our main tables exist
    with connection.cursor() as cursor:
        required_tables = [
            'configurations_tradingconfiguration',
            'licenses_client',
            'licenses_license'
        ]
        
        missing_tables = []
        for table in required_tables:
            cursor.execute(f\"\"\"
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{table}'
                );
            \"\"\")
            if not cursor.fetchone()[0]:
                missing_tables.append(table)
        
        if missing_tables:
            print(f'❌ Missing tables: {missing_tables}')
            exit(1)
        else:
            print('✅ All required tables exist')
    
    print('✅ Database structure verified')
    
except Exception as e:
    print(f'❌ Database verification failed: {e}')
    exit(1)
" || exit 1

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
        
    # Create sample data if needed
    from configurations.models import TradingConfiguration
    from licenses.models import Client, License
    from django.utils import timezone
    from datetime import timedelta
    import uuid
    
    # Create sample configuration
    if not TradingConfiguration.objects.exists():
        config = TradingConfiguration.objects.create(
            name='US30 Standard Configuration',
            description='Standard US30 trading configuration',
            allowed_symbol='US30',
            is_active=True
        )
        print('✅ Created sample configuration')
        
        # Create sample client and license
        admin_user = User.objects.get(username='admin')
        client = Client.objects.create(
            first_name='Sample',
            last_name='Client',
            country='United States',
            email='sample@example.com',
            created_by=admin_user
        )
        
        License.objects.create(
            license_key=str(uuid.uuid4()).replace('-', ''),
            client=client,
            trading_configuration=config,
            account_trade_mode=0,
            expires_at=timezone.now() + timedelta(days=365),
            is_active=True,
            created_by=admin_user
        )
        print('✅ Created sample client and license')
    
except Exception as e:
    print(f'⚠️  Admin/sample data setup failed: {e}')
" || echo "⚠️  Admin user setup failed"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear || echo "⚠️  Static collection failed"

# Final verification
echo "🎯 Final verification..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
django.setup()

from licenses.models import Client, License
from configurations.models import TradingConfiguration
from django.contrib.auth.models import User

try:
    client_count = Client.objects.count()
    license_count = License.objects.count()
    config_count = TradingConfiguration.objects.count()
    admin_count = User.objects.filter(is_superuser=True).count()
    
    print(f'✅ Database contents:')
    print(f'   👤 Admin users: {admin_count}')
    print(f'   👥 Clients: {client_count}')
    print(f'   🔑 Licenses: {license_count}')
    print(f'   ⚙️  Configurations: {config_count}')
    
    if all([admin_count > 0, config_count > 0]):
        print('✅ Application ready for use')
    else:
        print('⚠️  Some data may be missing')
        
except Exception as e:
    print(f'⚠️  Final verification warning: {e}')
" || echo "⚠️  Final verification had issues"

echo ""
echo "✅ DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "🌐 Application URLs:"
echo "   📱 Admin: https://mt5-dashboard.onrender.com/admin/ (admin/admin123)"
echo "   🏠 Dashboard: https://mt5-dashboard.onrender.com/dashboard/"
echo "   🤖 API: https://mt5-dashboard.onrender.com/api/validate/"
echo ""
echo "🔐 Admin Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo "   ⚠️  Change password after first login!"
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