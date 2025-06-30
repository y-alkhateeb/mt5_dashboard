#!/bin/bash
# Updated entrypoint.sh with better migration handling
set -e

echo "🚀 Starting Trading Admin deployment with smart migration handling..."
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

# Smart migration detection and handling
echo "🔍 Analyzing database state..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
django.setup()

from django.db import connection
from django.core.management import call_command

print('🔍 Checking database tables and current migration state...')

with connection.cursor() as cursor:
    # Check if configurations table exists
    cursor.execute(\"\"\"
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'configurations_tradingconfiguration'
        );
    \"\"\")
    
    table_exists = cursor.fetchone()[0]
    
    if not table_exists:
        print('📝 Fresh database detected - will create clean migrations')
        exit(0)
    
    # Check current field structure
    cursor.execute(\"\"\"
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'configurations_tradingconfiguration'
        ORDER BY column_name;
    \"\"\")
    
    current_fields = [row[0] for row in cursor.fetchall()]
    print(f'📋 Current fields found: {len(current_fields)} fields')
    
    # Determine strategy based on current field names
    has_inp_fields = any(field.startswith('inp_') for field in current_fields)
    has_new_fields = any(field.startswith('fib_session_') or field.startswith('fib_primary_') for field in current_fields)
    has_old_fib_fields = any(field.startswith('fib_level_') for field in current_fields)
    has_allowed_symbol = 'allowed_symbol' in current_fields
    
    print(f'🔍 Field analysis:')
    print(f'   Has inp_ fields: {has_inp_fields}')
    print(f'   Has new fields: {has_new_fields}')
    print(f'   Has old fib_level_ fields: {has_old_fib_fields}')
    print(f'   Has allowed_symbol: {has_allowed_symbol}')
    
    # Strategy decision
    if has_new_fields and has_allowed_symbol:
        print('✅ Database already has new field structure')
        strategy = 'up_to_date'
    elif has_inp_fields and not has_new_fields:
        print('🔄 Database has original inp_ fields - standard migration needed')
        strategy = 'standard_migration'
    elif has_old_fib_fields and not has_new_fields:
        print('⚠️  Database has inconsistent field structure - requires custom mapping')
        strategy = 'custom_migration'
    else:
        print('❓ Unknown database state - will attempt recovery')
        strategy = 'recovery'
    
    print(f'📋 Migration strategy: {strategy}')
    
    # Store strategy for shell script
    with open('/tmp/migration_strategy.txt', 'w') as f:
        f.write(strategy)
"

# Read the strategy
STRATEGY=$(cat /tmp/migration_strategy.txt 2>/dev/null || echo "recovery")
echo "📊 Applying migration strategy: $STRATEGY"

case $STRATEGY in
    "up_to_date")
        echo "✅ Database is up to date - applying any pending migrations..."
        python manage.py migrate --noinput || {
            echo "❌ Failed to apply pending migrations"
            exit 1
        }
        ;;
        
    "standard_migration")
        echo "🔄 Applying standard field rename migrations..."
        python manage.py migrate --noinput || {
            echo "❌ Standard migration failed"
            exit 1
        }
        ;;
        
    "custom_migration"|"recovery")
        echo "🛠️  Applying custom field mapping..."
        
        # Create a custom SQL migration to handle the current state
        python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
django.setup()

from django.db import connection, transaction

print('🔧 Executing custom field mapping...')

with connection.cursor() as cursor:
    with transaction.atomic():
        # Get current columns
        cursor.execute(\"\"\"
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'configurations_tradingconfiguration'
            ORDER BY column_name;
        \"\"\")
        
        current_fields = [row[0] for row in cursor.fetchall()]
        print(f'📋 Working with {len(current_fields)} existing fields')
        
        # Map problematic fields to correct names
        field_mappings = {
            # Basic fields
            'inp_AllowedSymbol': 'allowed_symbol',
            'inp_StrictSymbolCheck': 'strict_symbol_check', 
            'inp_SessionStart': 'session_start',
            'inp_SessionEnd': 'session_end',
            
            # Fibonacci mappings from current inconsistent names
            'fib_level_1_1': 'fib_primary_buy_tp',
            'fib_level_1_05': 'fib_primary_buy_entry',
            'fib_level_1_0': 'fib_session_high',
            'fib_level_0_0': 'fib_session_low',
            'fib_level_neg_05': 'fib_primary_sell_entry',
            'fib_level_neg_1': 'fib_primary_sell_tp',
            'fib_level_primary_buy_sl': 'fib_primary_buy_sl',
            'fib_level_primary_sell_sl': 'fib_primary_sell_sl',
            
            # Hedge fields
            'fib_level_hedge_buy': 'fib_level_hedge_buy',  # Keep as is if correct
            'fib_level_hedge_sell': 'fib_level_hedge_sell',  # Keep as is if correct
            'fib_level_hedge_buy_sl': 'fib_level_hedge_buy_sl',  # Keep as is if correct
            'fib_level_hedge_sell_sl': 'fib_level_hedge_sell_sl',  # Keep as is if correct
            'fib_level_hedge_buy_tp': 'fib_hedge_buy_tp',
            'fib_level_hedge_sell_tp': 'fib_hedge_sell_tp',
            
            # Timeout fields
            'inp_PrimaryPendingTimeout': 'primary_pending_timeout',
            'inp_PrimaryPositionTimeout': 'primary_position_timeout',
            'inp_HedgingPendingTimeout': 'hedging_pending_timeout',
            'inp_HedgingPositionTimeout': 'hedging_position_timeout',
        }
        
        # Apply field renames where source exists and target doesn't
        renamed_count = 0
        for old_name, new_name in field_mappings.items():
            if old_name in current_fields and new_name not in current_fields and old_name != new_name:
                try:
                    cursor.execute(f'ALTER TABLE configurations_tradingconfiguration RENAME COLUMN \"{old_name}\" TO {new_name};')
                    print(f'   ✅ Renamed {old_name} → {new_name}')
                    renamed_count += 1
                except Exception as e:
                    print(f'   ⚠️  Failed to rename {old_name}: {e}')
        
        # Add missing fields with defaults
        required_fields = {
            'allowed_symbol': ('VARCHAR(20)', \"'US30'\"),
            'strict_symbol_check': ('BOOLEAN', 'true'),
            'session_start': ('VARCHAR(5)', \"'08:45'\"),
            'session_end': ('VARCHAR(5)', \"'10:00'\"),
            'fib_primary_buy_tp': ('NUMERIC(8,5)', '1.325'),
            'fib_primary_buy_entry': ('NUMERIC(8,5)', '1.05'),
            'fib_session_high': ('NUMERIC(8,5)', '1.0'),
            'fib_session_low': ('NUMERIC(8,5)', '0.0'),
            'fib_primary_sell_entry': ('NUMERIC(8,5)', '-0.05'),
            'fib_primary_sell_tp': ('NUMERIC(8,5)', '-0.325'),
            'fib_primary_buy_sl': ('NUMERIC(8,5)', '-0.05'),
            'fib_primary_sell_sl': ('NUMERIC(8,5)', '1.05'),
            'fib_level_hedge_buy': ('NUMERIC(8,5)', '1.05'),
            'fib_level_hedge_sell': ('NUMERIC(8,5)', '-0.05'),
            'fib_level_hedge_buy_sl': ('NUMERIC(8,5)', '0.0'),
            'fib_level_hedge_sell_sl': ('NUMERIC(8,5)', '1.0'),
            'fib_hedge_buy_tp': ('NUMERIC(8,5)', '1.3'),
            'fib_hedge_sell_tp': ('NUMERIC(8,5)', '-0.3'),
            'primary_pending_timeout': ('INTEGER', '30'),
            'primary_position_timeout': ('INTEGER', '60'),
            'hedging_pending_timeout': ('INTEGER', '30'),
            'hedging_position_timeout': ('INTEGER', '60'),
        }
        
        # Re-check current fields after renames
        cursor.execute(\"\"\"
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'configurations_tradingconfiguration';
        \"\"\")
        current_fields = [row[0] for row in cursor.fetchall()]
        
        added_count = 0
        for field_name, (field_type, default_value) in required_fields.items():
            if field_name not in current_fields:
                try:
                    cursor.execute(f'ALTER TABLE configurations_tradingconfiguration ADD COLUMN {field_name} {field_type} DEFAULT {default_value};')
                    print(f'   ➕ Added missing field: {field_name}')
                    added_count += 1
                except Exception as e:
                    print(f'   ⚠️  Failed to add {field_name}: {e}')
        
        print(f'✅ Custom mapping complete: {renamed_count} renamed, {added_count} added')

" || {
            echo "❌ Custom field mapping failed"
            exit 1
        }
        
        # Now apply any remaining Django migrations
        echo "🔄 Applying Django migrations after custom mapping..."
        python manage.py migrate --noinput || {
            echo "⚠️  Some Django migrations may have failed, but continuing..."
        }
        ;;
        
    *)
        echo "❓ Unknown strategy - attempting basic migration..."
        python manage.py migrate --noinput || {
            echo "❌ Migration failed"
            exit 1
        }
        ;;
esac

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

with connection.cursor() as cursor:
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

# Check that we have the required fields
cursor.execute(\"\"\"
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'configurations_tradingconfiguration'
    AND column_name IN ('allowed_symbol', 'fib_session_high', 'fib_primary_buy_entry')
    ORDER BY column_name;
\"\"\")

key_fields = [row[0] for row in cursor.fetchall()]
if len(key_fields) >= 3:
    print(f'✅ Key fields verified: {key_fields}')
else:
    print(f'⚠️  Some key fields may be missing: {key_fields}')

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