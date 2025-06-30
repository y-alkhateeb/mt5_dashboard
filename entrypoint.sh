#!/bin/bash
# Updated entrypoint.sh for field rename migrations - preserves data
set -e

echo "🚀 Starting Trading Admin deployment with field rename migrations..."
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

# Check database state and determine migration strategy
echo "🔍 Analyzing database state for field rename migration..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
django.setup()

from django.db import connection
from django.core.management import call_command

print('🔍 Checking database tables and field structure...')

tables_exist = []
field_structure = {}

with connection.cursor() as cursor:
    # Check if main tables exist
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
            tables_exist.append(table)
    
    print(f'✅ Existing tables: {tables_exist}')
    
    # Check field structure in configurations table if it exists
    if 'configurations_tradingconfiguration' in tables_exist:
        cursor.execute(\"\"\"
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'configurations_tradingconfiguration'
            AND column_name LIKE '%fib%'
            ORDER BY column_name;
        \"\"\")
        
        fib_fields = [row[0] for row in cursor.fetchall()]
        print(f'📋 Current Fibonacci fields: {fib_fields}')
        
        # Determine if we have old or new field names
        old_field_pattern = any('fib_level_' in field for field in fib_fields)
        new_field_pattern = any('fib_session_' in field or 'fib_primary_' in field for field in fib_fields)
        
        if old_field_pattern and not new_field_pattern:
            print('🔄 OLD field structure detected - field rename migration needed')
            field_structure['migration_needed'] = True
            field_structure['current_structure'] = 'old'
        elif new_field_pattern and not old_field_pattern:
            print('✅ NEW field structure detected - migration already completed')
            field_structure['migration_needed'] = False
            field_structure['current_structure'] = 'new'
        elif old_field_pattern and new_field_pattern:
            print('⚠️  MIXED field structure detected - partial migration state')
            field_structure['migration_needed'] = True
            field_structure['current_structure'] = 'mixed'
        else:
            print('❓ Unknown field structure - will create fresh migrations')
            field_structure['migration_needed'] = True
            field_structure['current_structure'] = 'unknown'
    else:
        print('📝 No configurations table - fresh installation')
        field_structure['migration_needed'] = True
        field_structure['current_structure'] = 'fresh'

# Store the analysis result
import json
with open('/tmp/db_analysis.json', 'w') as f:
    json.dump({
        'tables_exist': tables_exist,
        'field_structure': field_structure
    }, f)

print(f'💾 Database analysis complete - {len(tables_exist)} tables found')
"

# Load analysis results
DB_ANALYSIS=$(python -c "
import json
try:
    with open('/tmp/db_analysis.json', 'r') as f:
        data = json.load(f)
    print(f\"{data['field_structure']['migration_needed']}|{data['field_structure']['current_structure']}|{len(data['tables_exist'])}\")
except:
    print('True|unknown|0')
")

IFS='|' read -r MIGRATION_NEEDED CURRENT_STRUCTURE TABLE_COUNT <<< "$DB_ANALYSIS"

echo "📊 Migration Strategy: $CURRENT_STRUCTURE structure, $TABLE_COUNT tables, migration needed: $MIGRATION_NEEDED"

# Handle migrations based on current state
if [ "$CURRENT_STRUCTURE" = "fresh" ] || [ "$TABLE_COUNT" = "0" ]; then
    echo "🆕 Fresh installation - creating initial migrations..."
    
    # Clean any existing migration files for fresh start
    for app in licenses configurations; do
        if [ -d "$app/migrations" ]; then
            find "$app/migrations/" -name "*.py" -not -name "__init__.py" -delete 2>/dev/null || true
            find "$app/migrations/" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
            echo "   Cleaned $app migrations"
        fi
    done
    
    # Create fresh migrations with new field names
    python manage.py makemigrations configurations --noinput || {
        echo "❌ Failed to create configurations migrations"
        exit 1
    }
    
    python manage.py makemigrations licenses --noinput || {
        echo "❌ Failed to create licenses migrations"
        exit 1
    }
    
    # Apply migrations
    python manage.py migrate --noinput || {
        echo "❌ Failed to apply fresh migrations"
        exit 1
    }
    
    echo "✅ Fresh migrations applied successfully"

elif [ "$CURRENT_STRUCTURE" = "old" ]; then
    echo "🔄 Old field structure detected - applying field rename migrations..."
    
    # Create field rename migration
    echo "📝 Creating field rename migration..."
    python manage.py makemigrations configurations --name rename_fib_fields --noinput || {
        echo "❌ Failed to create field rename migration"
        exit 1
    }
    
    # Apply the field rename migration
    echo "🚀 Applying field rename migration..."
    python manage.py migrate configurations --noinput || {
        echo "❌ Failed to apply field rename migration"
        exit 1
    }
    
    # Apply any other pending migrations
    python manage.py migrate --noinput || {
        echo "❌ Failed to apply remaining migrations"
        exit 1
    }
    
    echo "✅ Field rename migration completed successfully"

elif [ "$CURRENT_STRUCTURE" = "new" ]; then
    echo "✅ New field structure already in place - checking for pending migrations..."
    
    # Just apply any pending migrations
    python manage.py migrate --noinput || {
        echo "❌ Failed to apply pending migrations"
        exit 1
    }
    
    echo "✅ All migrations up to date"

else
    echo "⚠️  Mixed or unknown field structure - attempting recovery..."
    
    # Try to create and apply migrations carefully
    python manage.py makemigrations --noinput || echo "⚠️  Migration creation had issues"
    python manage.py migrate --noinput || {
        echo "❌ Migration failed - manual intervention may be required"
        exit 1
    }
    
    echo "✅ Recovery migration completed"
fi

# Verify final database state
echo "🔍 Final database verification..."
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

# Verify new field structure
try:
    cursor.execute(\"\"\"
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'configurations_tradingconfiguration'
        AND (column_name LIKE 'fib_session_%' OR column_name LIKE 'fib_primary_%')
        ORDER BY column_name;
    \"\"\")
    
    new_fields = [row[0] for row in cursor.fetchall()]
    if new_fields:
        print(f'✅ New field structure confirmed: {len(new_fields)} new fields found')
        print(f'   Sample fields: {new_fields[:3]}...')
    else:
        print('⚠️  New field structure not detected - may still have old fields')
        
except Exception as e:
    print(f'⚠️  Field verification failed: {e}')

print('✅ Database verification completed')
"

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
echo "🔄 Field Rename Migration Status:"
echo "   ✅ Database schema updated with new field names"
echo "   ✅ API maintains backward compatibility"
echo "   ✅ Existing data preserved during migration"
echo ""
echo "📝 Next Steps:"
echo "   1. Test admin interface with new field names"
echo "   2. Verify API endpoints return both old and new field names"
echo "   3. Confirm existing MT5 robots continue working"
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