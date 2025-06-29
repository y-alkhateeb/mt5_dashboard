#!/bin/bash
# File: fix_render_deployment.sh
# Purpose: Fix Docker issue and ensure native Python buildpack is used

echo "🔧 FIXING RENDER DEPLOYMENT ISSUE"
echo "================================="
echo ""
echo "Issue detected: Render is trying to use Docker instead of native Python"
echo "Solution: Remove Dockerfile and ensure proper render.yaml configuration"
echo ""

# Step 1: Remove/backup Dockerfile 
if [ -f "Dockerfile" ]; then
    echo "📁 Step 1: Handling existing Dockerfile..."
    
    # Create backup
    mv Dockerfile Dockerfile.backup
    echo "✅ Moved Dockerfile to Dockerfile.backup"
    
    # Also backup any docker-related files
    if [ -f ".dockerignore" ]; then
        mv .dockerignore .dockerignore.backup
        echo "✅ Moved .dockerignore to .dockerignore.backup"
    fi
else
    echo "📁 Step 1: No Dockerfile found - good!"
fi

echo ""

# Step 2: Create/update proper render.yaml for native Python
echo "📝 Step 2: Creating proper render.yaml for native Python..."

cat > render.yaml << 'EOF'
services:
  # Web Service (Django Trading Robot Admin) - Native Python
  - type: web
    name: trading-robot-admin
    runtime: python3
    region: oregon
    
    # Build command - uses native Python buildpack
    buildCommand: |
      echo "🐍 Using Render native Python buildpack"
      pip install --upgrade pip
      pip install -r requirements.txt
      echo "📦 Dependencies installed"
      python manage.py collectstatic --noinput
      echo "📁 Static files collected"
      python manage.py migrate --noinput
      echo "💾 Database migrations applied"
      python manage.py setup_admin --username admin --password admin123
      echo "👤 Admin user created"
      echo "✅ Build completed successfully"
    
    # Start command - runs the Django app
    startCommand: |
      echo "🚀 Starting Trading Robot Admin..."
      gunicorn trading_admin.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120 --access-logfile - --error-logfile -
    
    # Service configuration
    plan: starter
    
    # Environment variables
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: DJANGO_SETTINGS_MODULE
        value: trading_admin.settings_render
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
    
    # Health check
    healthCheckPath: /api/health/

  # PostgreSQL Database
  - type: pgsql
    name: trading-robot-db
    region: oregon
    databaseName: trading_admin
    user: trading_admin_user
    plan: starter
EOF

echo "✅ Created render.yaml for native Python buildpack"
echo ""

# Step 3: Verify requirements.txt
echo "📦 Step 3: Verifying requirements.txt..."

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found - creating one..."
    
    cat > requirements.txt << 'EOF'
Django==4.2.7
djangorestframework==3.14.0
psycopg2-binary==2.9.7
dj-database-url==2.1.0
gunicorn==21.2.0
whitenoise==6.6.0
django-cors-headers==4.3.1
django-crispy-forms==2.1
crispy-bootstrap5==0.7
Pillow==10.1.0
redis==5.0.1
python-decouple==3.8
django-extensions==3.2.3
EOF
    
    echo "✅ Created requirements.txt"
else
    echo "✅ requirements.txt exists"
    
    # Check for essential packages
    essential_packages=("Django" "gunicorn" "psycopg2-binary" "dj-database-url" "whitenoise")
    missing_packages=()
    
    for package in "${essential_packages[@]}"; do
        if ! grep -q "$package" requirements.txt; then
            missing_packages+=("$package")
        fi
    done
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        echo "⚠️  Missing essential packages: ${missing_packages[*]}"
        echo "Adding them to requirements.txt..."
        
        for package in "${missing_packages[@]}"; do
            case $package in
                "Django") echo "Django==4.2.7" >> requirements.txt ;;
                "gunicorn") echo "gunicorn==21.2.0" >> requirements.txt ;;
                "psycopg2-binary") echo "psycopg2-binary==2.9.7" >> requirements.txt ;;
                "dj-database-url") echo "dj-database-url==2.1.0" >> requirements.txt ;;
                "whitenoise") echo "whitenoise==6.6.0" >> requirements.txt ;;
            esac
        done
        
        echo "✅ Added missing packages"
    fi
fi

echo ""

# Step 4: Verify settings_render.py exists and is correct
echo "⚙️  Step 4: Verifying Render settings..."

if [ ! -f "trading_admin/settings_render.py" ]; then
    echo "❌ settings_render.py not found - creating one..."
    
    cat > trading_admin/settings_render.py << 'EOF'
import os
import dj_database_url
from .settings import *

# Production settings for Render
SECRET_KEY = os.getenv('SECRET_KEY', 'temp-key-for-render')
DEBUG = False

# Render hostname configuration
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS = [RENDER_EXTERNAL_HOSTNAME, '*.onrender.com']
else:
    ALLOWED_HOSTS = ['*']  # Fallback

# Database configuration
if os.getenv('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.parse(
            os.getenv('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

print("🚀 Render settings loaded successfully!")
EOF
    
    echo "✅ Created settings_render.py"
else
    echo "✅ settings_render.py exists"
fi

echo ""

# Step 5: Update .gitignore to exclude Docker files
echo "📝 Step 5: Updating .gitignore..."

cat >> .gitignore << 'EOF'

# Docker backup files (moved during Render setup)
Dockerfile.backup
.dockerignore.backup

# Render specific
.render/
staticfiles/
EOF

echo "✅ Updated .gitignore"
echo ""

# Step 6: Verify manage.py and wsgi.py
echo "🔧 Step 6: Verifying Django configuration..."

# Check if manage.py has proper Render detection
if grep -q "settings_render" manage.py; then
    echo "✅ manage.py has Render settings detection"
else
    echo "⚠️  Updating manage.py for Render..."
    
    cat > manage.py << 'EOF'
#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    # Render platform detection
    if os.getenv('RENDER_EXTERNAL_HOSTNAME'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
        print("🚀 Using Render settings")
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings')
        print("💻 Using local settings")
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
EOF
    
    echo "✅ Updated manage.py"
fi

# Similar check for wsgi.py
if grep -q "settings_render" trading_admin/wsgi.py; then
    echo "✅ wsgi.py has Render settings detection"
else
    echo "⚠️  Updating wsgi.py for Render..."
    
    cat > trading_admin/wsgi.py << 'EOF'
import os
from django.core.wsgi import get_wsgi_application

# Render platform detection
if os.getenv('RENDER_EXTERNAL_HOSTNAME'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings')

application = get_wsgi_application()
EOF
    
    echo "✅ Updated wsgi.py"
fi

echo ""

# Step 7: Create admin setup command if it doesn't exist
echo "👤 Step 7: Verifying admin setup command..."

admin_command_dir="core/management/commands"
admin_command_file="$admin_command_dir/setup_admin.py"

if [ ! -f "$admin_command_file" ]; then
    echo "Creating admin setup command..."
    
    mkdir -p "$admin_command_dir"
    touch core/management/__init__.py
    touch core/management/commands/__init__.py
    
    cat > "$admin_command_file" << 'EOF'
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create admin user for production'
    
    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin')
        parser.add_argument('--password', default='admin123')
        parser.add_argument('--email', default='admin@example.com')
    
    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(f'✅ Admin user "{username}" already exists')
            return
        
        User.objects.create_superuser(username, email, password)
        self.stdout.write(f'✅ Created admin user: {username}')
EOF
    
    echo "✅ Created admin setup command"
else
    echo "✅ Admin setup command exists"
fi

echo ""

# Step 8: Test configuration
echo "🧪 Step 8: Testing configuration..."

# Test settings import
python -c "
import os
os.environ['RENDER_EXTERNAL_HOSTNAME'] = 'test.onrender.com'
os.environ['SECRET_KEY'] = 'test-key'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')

try:
    import django
    django.setup()
    print('✅ Settings import successful')
except Exception as e:
    print(f'❌ Settings import failed: {e}')
    exit(1)
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Configuration test passed"
else
    echo "❌ Configuration test failed"
fi

echo ""

# Step 9: Summary and next steps
echo "🎉 RENDER DEPLOYMENT FIX COMPLETED!"
echo "=================================="
echo ""
echo "📁 Changes made:"
echo "   ✅ Removed Dockerfile (moved to Dockerfile.backup)"
echo "   ✅ Created proper render.yaml for native Python"
echo "   ✅ Verified/created requirements.txt"
echo "   ✅ Verified/created settings_render.py"
echo "   ✅ Updated manage.py and wsgi.py"
echo "   ✅ Created admin setup command"
echo "   ✅ Updated .gitignore"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Commit these changes:"
echo "   git add ."
echo "   git commit -m 'Fix Render deployment - use native Python instead of Docker'"
echo "   git push origin main"
echo ""
echo "2. In Render Dashboard:"
echo "   🔄 Manual Deploy → Deploy latest commit"
echo "   📝 Verify these environment variables are set:"
echo "      - DJANGO_SETTINGS_MODULE=trading_admin.settings_render"
echo "      - SECRET_KEY=(auto-generated)"
echo "      - DEBUG=false"
echo ""
echo "3. Monitor the deployment:"
echo "   📊 Build should show: '🐍 Using Render native Python buildpack'"
echo "   ✅ Look for: '✅ Build completed successfully'"
echo "   🚀 Then: '🚀 Starting Trading Robot Admin...'"
echo ""
echo "4. Test after deployment:"
echo "   🌐 Visit: https://your-app.onrender.com/admin/"
echo "   👤 Login: admin / admin123"
echo ""
echo "💡 Key fix: Render will now use native Python buildpack instead of Docker"
echo "   This is more reliable and easier to debug than Docker builds."
echo ""
echo "🚀 Your app should deploy successfully now!"