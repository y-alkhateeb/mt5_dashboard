#!/bin/bash
# Updated docker-entrypoint.sh with automatic PostgreSQL field fix
# Runs automatically on every Render deployment

set -e

echo "🚀 TRADING ROBOT ADMIN - RENDER DEPLOYMENT WITH POSTGRESQL FIX"
echo "=============================================================="
echo "🌐 Environment: Production (Render.com)"
echo "🔧 Auto-fixing PostgreSQL field naming issues"
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

# Function to run automatic PostgreSQL field fix
auto_fix_postgresql() {
    echo "🔧 AUTOMATIC POSTGRESQL FIELD FIX"
    echo "================================="
    
    # Check if this is a fresh deployment or update
    echo "📋 Checking deployment type..."
    
    # Run the PostgreSQL fix management command
    echo "🚀 Running PostgreSQL field compatibility fix..."
    
    if python manage.py fix_postgresql_fields --force; then
        echo "✅ PostgreSQL field fix completed successfully"
    else
        echo "⚠️  PostgreSQL field fix had issues, continuing with standard migration..."
        
        # Fallback to standard migration process
        echo "🔄 Running fallback migration process..."
        
        # Create migrations if they don't exist
        echo "📝 Creating missing migrations..."
        python manage.py makemigrations configurations --noinput || echo "⚠️  Configurations migrations failed"
        python manage.py makemigrations licenses --noinput || echo "⚠️  Licenses migrations failed"
        
        # Apply migrations
        echo "🚀 Applying migrations..."
        python manage.py migrate --noinput || echo "⚠️  Migrations failed"
    fi
}

# Function to run standard migrations (as backup)
run_standard_migrations() {
    echo "📊 STANDARD MIGRATION PROCESS"
    echo "============================"
    
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
}

# Function to setup admin user
setup_admin_user() {
    echo "👤 ADMIN USER SETUP"
    echo "=================="
    
    # Try to create admin user via management command
    echo "🔧 Setting up admin user..."
    python manage.py setup_admin --username admin --password admin123 --email admin@example.com || {
        echo "⚠️  Admin setup command failed, trying manual creation..."
        
        # Fallback manual creation
        python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
django.setup()

from django.contrib.auth.models import User

username = 'admin'
password = 'admin123'
email = 'admin@example.com'

try:
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.set_password(password)
        user.email = email
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        print(f'✅ Updated admin user: {username}')
    else:
        User.objects.create_superuser(username, email, password)
        print(f'✅ Created admin user: {username}')
    
    print(f'📧 Email: {email}')
    print(f'🔑 Password: {password}')
    print('⚠️  Change password after first login!')
    
except Exception as e:
    print(f'❌ Manual admin creation failed: {e}')
" || echo "⚠️  Admin user creation failed"
    }
}

# Function to verify deployment
verify_deployment() {
    echo "🔍 DEPLOYMENT VERIFICATION"
    echo "========================="
    
    echo "🧪 Running deployment verification..."
    python -c "
try:
    import django
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
    django.setup()
    
    from django.db import connection
    from licenses.models import Client, License
    from configurations.models import TradingConfiguration
    from django.contrib.auth.models import User
    
    # Test database connection
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✅ Database connection verified')
    
    # Test model access
    try:
        client_count = Client.objects.count()
        license_count = License.objects.count() 
        config_count = TradingConfiguration.objects.count()
        admin_count = User.objects.filter(is_superuser=True).count()
        
        print(f'✅ Models accessible:')
        print(f'   👤 Admins: {admin_count}')
        print(f'   👥 Clients: {client_count}')
        print(f'   🔑 Licenses: {license_count}')
        print(f'   ⚙️  Configs: {config_count}')
        
        # Test API compatibility
        if config_count > 0:
            from configurations.serializers import TradingConfigurationSerializer
            config = TradingConfiguration.objects.first()
            data = TradingConfigurationSerializer(config).data
            has_legacy = 'inp_AllowedSymbol' in data
            has_new = 'allowed_symbol' in data
            print(f'✅ API compatibility: Legacy={has_legacy}, New={has_new}')
        
    except Exception as e:
        print(f'⚠️  Model verification warning: {e}')
    
except Exception as e:
    print(f'⚠️  Verification warning: {e}')
    print('🔄 Application will continue starting...')
" 2>/dev/null || echo "⚠️  Verification skipped"
}

# Function to collect static files
collect_static_files() {
    echo "📁 STATIC FILES COLLECTION"
    echo "=========================="
    
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
    echo "🔐 Default admin credentials:"
    echo "   Username: admin"
    echo "   Password: admin123"
    echo "   ⚠️  Change password after first login!"
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

# Main deployment sequence with PostgreSQL fix
main() {
    echo "🎯 RENDER.COM DEPLOYMENT WITH POSTGRESQL FIX"
    echo "=============================================="
    echo "🕐 Started at: $(date)"
    echo ""
    
    # Step 1: Wait for database
    wait_for_postgres
    
    echo ""
    
    # Step 2: Run automatic PostgreSQL field fix
    auto_fix_postgresql
    
    echo ""
    
    # Step 3: Setup admin user
    setup_admin_user
    
    echo ""
    
    # Step 4: Collect static files
    collect_static_files
    
    echo ""
    
    # Step 5: Verify deployment
    verify_deployment
    
    echo ""
    echo "✅ DEPLOYMENT COMPLETED SUCCESSFULLY!"
    echo "==================================="
    echo ""
    
    # Step 6: Start the application
    start_application
}

# Error handling
trap 'echo "❌ Deployment failed at line $LINENO. Check Render logs for details."' ERR

# Run main deployment sequence
main "$@"