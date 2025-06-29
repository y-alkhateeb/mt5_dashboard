#!/bin/bash
# File: prepare_render_deployment.sh

set -e  # Exit on any error

echo "🚀 Preparing project for Render deployment..."
echo "=============================================="

# Step 1: Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from the Django project root."
    exit 1
fi

echo "✅ Django project detected"

# Step 2: Create logs directory if it doesn't exist
echo "📁 Creating logs directory..."
mkdir -p logs
echo "✅ Logs directory created"

# Step 3: Check for required files
echo "🔍 Checking required files..."

required_files=(
    "requirements.txt"
    "trading_admin/settings.py"
    "licenses/models.py"
    "configurations/models.py"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "❌ Missing required files:"
    printf '%s\n' "${missing_files[@]}"
    exit 1
fi

echo "✅ All required files present"

# Step 4: Update manage.py for Render
echo "🔄 Updating manage.py for multi-platform support..."
cat > manage.py << 'EOF'
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

if __name__ == '__main__':
    # Smart settings detection for multiple platforms
    if os.getenv('RENDER'):
        # On Render, use Render settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
        print("🚀 Using Render settings")
    elif os.getenv('RAILWAY_ENVIRONMENT'):
        # On Railway, use Railway settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_railway')
        print("🚂 Using Railway settings")
    else:
        # Local development, use local settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings')
        print("💻 Using local development settings")
    
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

echo "✅ manage.py updated"

# Step 5: Update wsgi.py for Render
echo "🔄 Updating wsgi.py for multi-platform support..."
cat > trading_admin/wsgi.py << 'EOF'
"""
WSGI config for trading_admin project.
"""

import os
from django.core.wsgi import get_wsgi_application

# Smart settings detection for multiple platforms (same as manage.py)
if os.getenv('RENDER'):
    # On Render, use Render settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
elif os.getenv('RAILWAY_ENVIRONMENT'):
    # On Railway, use Railway settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_railway')
else:
    # Local development, use local settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings')

application = get_wsgi_application()
EOF

echo "✅ wsgi.py updated"

# Step 6: Create Render settings file
echo "⚙️ Creating Render settings file..."
cat > trading_admin/settings_render.py << 'EOF'
import os
import sys
import dj_database_url
from .settings import *

# Environment validation for production
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    print("❌ ERROR: SECRET_KEY environment variable is required in production!")
    sys.exit(1)

# Debug mode for Render
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Render domain configuration
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')

if RENDER_EXTERNAL_HOSTNAME:
    # Production - use Render domain
    ALLOWED_HOSTS = [
        RENDER_EXTERNAL_HOSTNAME,
        '*.onrender.com',
        'localhost',
        '127.0.0.1'
    ]
    # Dynamic CORS origins for production
    CORS_ALLOWED_ORIGINS = [
        f'https://{RENDER_EXTERNAL_HOSTNAME}',
    ]
    CORS_ALLOW_ALL_ORIGINS = False
else:
    # Development fallback
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']
    CORS_ALLOW_ALL_ORIGINS = True

# Database configuration using dj-database-url (Render provides DATABASE_URL)
if os.getenv('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.parse(
            os.getenv('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback to default SQLite for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files configuration for Render
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Use WhiteNoise for static files (perfect for Render)
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings for Render
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Session security
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Cache configuration for Render (using local memory)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Enhanced rate limiting for production
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '50/hour',              # Reduced for production
    'user': '500/hour',             # Reasonable limit for admin users
    'bot_validation': '30/minute',  # Conservative limit for bot validation
}

# Logging configuration for Render
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose' if DEBUG else 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'licenses': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'configurations': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

print(f"🚀 Render Settings Loaded:")
print(f"   RENDER_EXTERNAL_HOSTNAME: {RENDER_EXTERNAL_HOSTNAME or 'Not set (development)'}")
print(f"   ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"   SECRET_KEY: {'✅ Set' if SECRET_KEY else '❌ Missing'}")
print(f"   DEBUG: {DEBUG}")
print(f"   DATABASE: {'✅ Render PostgreSQL' if os.getenv('DATABASE_URL') else '❌ Local SQLite'}")
print(f"   STATIC_ROOT: {STATIC_ROOT}")
EOF

echo "✅ Render settings created"

# Step 7: Create render.yaml
echo "📝 Creating render.yaml configuration..."
cat > render.yaml << 'EOF'
services:
  # Web Service (Django App)
  - type: web
    name: trading-robot-admin
    runtime: python3
    buildCommand: |
      pip install --upgrade pip &&
      pip install -r requirements.txt &&
      python manage.py collectstatic --noinput &&
      python manage.py migrate --noinput
    startCommand: |
      python manage.py migrate --noinput &&
      gunicorn trading_admin.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120 --max-requests 1000 --max-requests-jitter 50
    plan: starter  # Can upgrade to standard/pro for production
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.5
      - key: DJANGO_SETTINGS_MODULE
        value: trading_admin.settings_render
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
      - key: WEB_CONCURRENCY
        value: 3
    healthCheckPath: /api/health/
    
  # PostgreSQL Database
  - type: pgsql
    name: trading-robot-db
    databaseName: trading_admin
    user: trading_admin_user
    plan: starter  # Free tier, upgrade for production
EOF

echo "✅ render.yaml created"

# Step 8: Update .gitignore for Render
echo "📝 Updating .gitignore..."
cat >> .gitignore << 'EOF'

# Render specific
staticfiles/
.render/

# Render deployment files
render.toml
EOF

echo "✅ .gitignore updated"

# Step 9: Verify requirements.txt
echo "🔍 Checking requirements.txt..."
if ! grep -q "gunicorn" requirements.txt; then
    echo "⚠️  Adding gunicorn to requirements.txt..."
    echo "gunicorn==21.2.0" >> requirements.txt
fi

if ! grep -q "dj-database-url" requirements.txt; then
    echo "⚠️  Adding dj-database-url to requirements.txt..."
    echo "dj-database-url==2.1.0" >> requirements.txt
fi

if ! grep -q "psycopg2-binary" requirements.txt; then
    echo "⚠️  Adding psycopg2-binary to requirements.txt..."
    echo "psycopg2-binary==2.9.7" >> requirements.txt
fi

if ! grep -q "whitenoise" requirements.txt; then
    echo "⚠️  Adding whitenoise to requirements.txt..."
    echo "whitenoise==6.6.0" >> requirements.txt
fi

echo "✅ requirements.txt verified"

# Step 10: Test local settings
echo "🧪 Testing settings configuration..."
python -c "
import os
os.environ['RENDER'] = 'true'
os.environ['SECRET_KEY'] = 'test-key'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
import django
django.setup()
print('✅ Render settings loaded successfully')
" 2>/dev/null || echo "⚠️  Settings test failed - check configuration"

# Step 11: Create deployment checklist
echo "📋 Creating deployment checklist..."
cat > RENDER_DEPLOYMENT_CHECKLIST.md << 'EOF'
# Render Deployment Checklist

## Pre-deployment Steps
- [x] Updated manage.py for multi-platform detection
- [x] Updated wsgi.py for multi-platform detection  
- [x] Created settings_render.py with Render configuration
- [x] Created render.yaml for service configuration
- [x] Updated requirements.txt with necessary dependencies
- [x] Updated .gitignore for Render

## Render Setup Steps
1. **Create Render Account** at https://render.com
2. **Connect GitHub Repository**
3. **Create Web Service** with these settings:
   - Runtime: Python 3
   - Build Command: `pip install --upgrade pip && pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput`
   - Start Command: `python manage.py migrate --noinput && gunicorn trading_admin.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120`
4. **Create PostgreSQL Database** (name: trading-robot-db)
5. **Set Environment Variables:**
   - DJANGO_SETTINGS_MODULE=trading_admin.settings_render
   - SECRET_KEY=(auto-generated by Render)
   - DEBUG=false

## Post-deployment Steps
1. Create superuser: `python manage.py createsuperuser`
2. Create sample data: `python manage.py create_sample_data`
3. Create default configs: `python manage.py create_default_configs`
4. Test admin access: https://your-app.onrender.com/admin/
5. Test dashboard: https://your-app.onrender.com/dashboard/
6. Test API health: https://your-app.onrender.com/api/health/

## URLs After Deployment
- Admin: https://your-app.onrender.com/admin/
- Dashboard: https://your-app.onrender.com/dashboard/  
- API Health: https://your-app.onrender.com/api/health/
- API Docs: https://your-app.onrender.com/api/docs/
EOF

echo "✅ Deployment checklist created"

# Step 12: Show summary
echo ""
echo "🎉 Render deployment preparation completed!"
echo "========================================="
echo ""
echo "📁 Files created/updated:"
echo "   ✅ manage.py (updated for multi-platform)"
echo "   ✅ trading_admin/wsgi.py (updated for multi-platform)"
echo "   ✅ trading_admin/settings_render.py (Render settings)"
echo "   ✅ render.yaml (Render service configuration)"
echo "   ✅ RENDER_DEPLOYMENT_CHECKLIST.md (deployment guide)"
echo "   ✅ .gitignore (updated for Render)"
echo "   ✅ requirements.txt (verified dependencies)"
echo ""
echo "📋 Next steps:"
echo "1. Review and commit all changes:"
echo "   git add ."
echo "   git commit -m 'Add Render deployment configuration'"
echo "   git push origin main"
echo ""
echo "2. Go to https://render.com and create account"
echo "3. Connect your GitHub repository"
echo "4. Create Web Service with the settings from the checklist"
echo "5. Create PostgreSQL database"
echo "6. Deploy and test!"
echo ""
echo "📖 Full deployment guide: RENDER_DEPLOYMENT_CHECKLIST.md"
echo ""
echo "🚀 Ready for Render deployment!"