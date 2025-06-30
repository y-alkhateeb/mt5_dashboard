#!/bin/bash
# Robust entrypoint.sh that handles partial table existence
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

# Advanced table analysis and repair
echo "🔍 Analyzing database state and fixing inconsistencies..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
django.setup()

from django.db import connection

print('🔍 Checking all required tables...')

# Define all required tables with their dependencies
required_tables = {
    'configurations_tradingconfiguration': None,  # No dependencies
    'licenses_client': None,  # No dependencies  
    'licenses_license': ['configurations_tradingconfiguration', 'licenses_client']  # Depends on both
}

existing_tables = []
missing_tables = []

with connection.cursor() as cursor:
    # Check which tables exist
    for table in required_tables.keys():
        cursor.execute(f\"\"\"
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{table}'
            );
        \"\"\")
        if cursor.fetchone()[0]:
            existing_tables.append(table)
        else:
            missing_tables.append(table)
    
    print(f'✅ Existing tables: {existing_tables}')
    print(f'❌ Missing tables: {missing_tables}')
    
    # Strategy: If we have partial tables, it's safer to recreate all
    if existing_tables and missing_tables:
        print('⚠️  Partial table existence detected - cleaning up for consistency')
        print('🗑️  Dropping all application tables to ensure clean state...')
        
        # Drop all our tables in reverse dependency order
        tables_to_drop = [
            'licenses_license',  # Drop dependent table first
            'licenses_client',
            'configurations_tradingconfiguration'
        ]
        
        for table in tables_to_drop:
            cursor.execute(f'DROP TABLE IF EXISTS {table} CASCADE;')
            print(f'   Dropped: {table}')
        
        # Clear all migration history for our apps
        cursor.execute(\"DELETE FROM django_migrations WHERE app IN ('configurations', 'licenses');\")
        print('🧹 Cleared all migration history')
        print('✅ Database cleaned - ready for fresh migration')
        
    elif existing_tables and not missing_tables:
        print('✅ All tables exist - will use fake migration')
        # Clear migration history to allow fake migration
        cursor.execute(\"DELETE FROM django_migrations WHERE app IN ('configurations', 'licenses');\")
        print('🧹 Cleared migration history for fake migration')
        
    elif not existing_tables:
        print('✅ No existing tables - fresh installation')
    
    else:
        print('✅ Database state is consistent')
"

# Create migrations
echo "📝 Creating migrations..."
python manage.py makemigrations configurations --noinput || {
    echo "❌ Failed to create configurations migrations"
    exit 1
}

python manage.py makemigrations licenses --noinput || {
    echo "❌ Failed to create licenses migrations"
    exit 1
}

# Apply migrations with smart strategy
echo "🚀 Applying migrations with smart strategy..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
django.setup()

from django.db import connection
from django.core.management import call_command

# Check current table state
existing_tables = []
with connection.cursor() as cursor:
    required_tables = [
        'configurations_tradingconfiguration',
        'licenses_client',
        'licenses_license'
    ]
    
    for table in required_tables:
        cursor.execute(f\"\"\"
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{table}'
            );
        \"\"\")
        if cursor.fetchone()[0]:
            existing_tables.append(table)

print(f'📊 Current existing tables: {existing_tables}')

if len(existing_tables) == 3:
    print('✅ All tables exist - using fake migration')
    try:
        call_command('migrate', '--fake-initial', verbosity=1)
        print('✅ Fake migration completed successfully')
    except Exception as e:
        print(f'⚠️  Fake migration failed: {e}')
        call_command('migrate', '--fake', verbosity=1)
        print('✅ Forced fake migration completed')
        
elif len(existing_tables) == 0:
    print('✅ No tables exist - running normal migration')
    call_command('migrate', verbosity=1)
    print('✅ Normal migration completed successfully')
    
else:
    print(f'⚠️  Partial tables detected: {existing_tables}')
    print('🔧 Running migration - should create missing tables')
    try:
        call_command('migrate', verbosity=1)
        print('✅ Migration completed - missing tables created')
    except Exception as e:
        print(f'❌ Migration failed: {e}')
        raise
" || {
    echo "❌ Migration strategy failed"
    exit 1
}

# Verify all tables exist
echo "🔍 Final table verification..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
django.setup()

from django.db import connection

required_tables = [
    'configurations_tradingconfiguration',
    'licenses_client',
    'licenses_license'
]

missing_tables = []
with connection.cursor() as cursor:
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
    print(f'❌ Still missing tables: {missing_tables}')
    exit(1)
else:
    print('✅ All required tables verified')
"

# Setup admin user and sample data
echo "👤 Setting up admin user and sample data..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
django.setup()

from django.contrib.auth.models import User
from configurations.models import TradingConfiguration
from licenses.models import Client, License
from django.utils import timezone
from datetime import timedelta
import uuid

try:
    # Create/update admin user
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
        admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print('✅ Created admin user: admin/admin123')
    
    admin_user = User.objects.get(username='admin')
    
    # Create sample configuration if none exist
    if not TradingConfiguration.objects.exists():
        config = TradingConfiguration.objects.create(
            name='US30 Standard Configuration',
            description='Standard US30 trading configuration - PostgreSQL compatible',
            allowed_symbol='US30',
            strict_symbol_check=True,
            session_start='08:45',
            session_end='10:00',
            is_active=True
        )
        print('✅ Created sample configuration')
    else:
        config = TradingConfiguration.objects.first()
        print('✅ Using existing configuration')
    
    # Create sample client and license if none exist
    if not Client.objects.exists():
        client = Client.objects.create(
            first_name='Sample',
            last_name='Client',
            country='United States',
            email='sample@example.com',
            created_by=admin_user
        )
        print('✅ Created sample client')
    else:
        client = Client.objects.first()
        print('✅ Using existing client')
    
    if not License.objects.exists():
        license_obj = License.objects.create(
            license_key=str(uuid.uuid4()).replace('-', ''),
            client=client,
            trading_configuration=config,
            account_trade_mode=0,  # Demo
            expires_at=timezone.now() + timedelta(days=365),
            is_active=True,
            created_by=admin_user
        )
        print('✅ Created sample license')
    else:
        print('✅ Using existing license')
    
    # Verify everything
    client_count = Client.objects.count()
    license_count = License.objects.count()
    config_count = TradingConfiguration.objects.count()
    admin_count = User.objects.filter(is_superuser=True).count()
    
    print(f'📊 Final database state:')
    print(f'   👤 Admin users: {admin_count}')
    print(f'   👥 Clients: {client_count}')
    print(f'   🔑 Licenses: {license_count}')
    print(f'   ⚙️  Configurations: {config_count}')
    
    if all([admin_count > 0, client_count > 0, license_count > 0, config_count > 0]):
        print('✅ All data verified - application ready')
    else:
        print('⚠️  Some data may be incomplete')
        
except Exception as e:
    print(f'❌ Setup failed: {e}')
    raise
" || {
    echo "❌ Admin user and sample data setup failed"
    exit 1
}

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear || echo "⚠️  Static collection failed"

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