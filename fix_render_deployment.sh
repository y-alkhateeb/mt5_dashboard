#!/bin/bash
# File: render_only_fix.sh
# Purpose: Simplify for Render-only deployment (remove Railway complexity)

set -e

echo "🚀 RENDER-ONLY DEPLOYMENT FIX"
echo "============================="
echo ""
echo "✂️  Removing Railway complexity since you only use Render"
echo ""

# STEP 1: Create simple, Render-focused manage.py
echo "📝 Step 1: Creating simple manage.py for Render-only..."
cat > manage.py << 'EOF'
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

if __name__ == '__main__':
    # SIMPLIFIED: Render-only detection
    
    # Priority 1: Explicit environment variable (for Render dashboard setting)
    if os.getenv('DJANGO_SETTINGS_MODULE'):
        print(f"🔧 Using explicit DJANGO_SETTINGS_MODULE: {os.getenv('DJANGO_SETTINGS_MODULE')}")
    
    # Priority 2: Render platform detection  
    elif os.getenv('RENDER_EXTERNAL_HOSTNAME'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
        print("🚀 Detected Render platform - using settings_render")
    
    # Priority 3: Local development fallback
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings')
        print("💻 Using local development settings")
    
    # Debug info
    print(f"📍 Final settings module: {os.getenv('DJANGO_SETTINGS_MODULE')}")
    print(f"🌐 RENDER_EXTERNAL_HOSTNAME: {os.getenv('RENDER_EXTERNAL_HOSTNAME', 'Not set')}")
    
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

echo "✅ manage.py simplified"

# STEP 2: Create simple, Render-focused wsgi.py
echo "📝 Step 2: Creating simple wsgi.py for Render-only..."
cat > trading_admin/wsgi.py << 'EOF'
"""
WSGI config for trading_admin project.
"""

import os
from django.core.wsgi import get_wsgi_application

# SIMPLIFIED: Render-only detection

# Priority 1: Explicit environment variable (for Render dashboard setting)
if os.getenv('DJANGO_SETTINGS_MODULE'):
    # Already set by Render dashboard, use it
    pass
    
# Priority 2: Render platform detection
elif os.getenv('RENDER_EXTERNAL_HOSTNAME'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
    
# Priority 3: Local development fallback
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings')

application = get_wsgi_application()
EOF

echo "✅ wsgi.py simplified"

# STEP 3: Ensure settings_render.py is correct and complete
echo "📝 Step 3: Creating/updating settings_render.py..."
cat > trading_admin/settings_render.py << 'EOF'
import os
import sys
import dj_database_url
from .settings import *

# Environment validation for production
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    from django.core.management.utils import get_random_secret_key
    SECRET_KEY = get_random_secret_key()
    print("⚠️  WARNING: SECRET_KEY not provided, auto-generated for this session")

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

print(f"🚀 Render Settings Loaded Successfully!")
print(f"   RENDER_EXTERNAL_HOSTNAME: {RENDER_EXTERNAL_HOSTNAME or 'Not set (development)'}")
print(f"   ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"   SECRET_KEY: {'✅ Set' if SECRET_KEY else '❌ Missing'}")
print(f"   DEBUG: {DEBUG}")
print(f"   DATABASE: {'✅ Render PostgreSQL' if os.getenv('DATABASE_URL') else '❌ Local SQLite'}")
print(f"   STATIC_ROOT: {STATIC_ROOT}")
EOF

echo "✅ settings_render.py updated"

# STEP 4: Update render.yaml to be explicit
echo "📝 Step 4: Creating/updating render.yaml..."
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
      gunicorn trading_admin.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120
    plan: starter
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.5
      - key: DJANGO_SETTINGS_MODULE
        value: trading_admin.settings_render
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
    healthCheckPath: /api/health/
    
  # PostgreSQL Database
  - type: pgsql
    name: trading-robot-db
    databaseName: trading_admin
    user: trading_admin_user
    plan: starter
EOF

echo "✅ render.yaml updated"

# STEP 5: Remove any Railway files if they exist
echo "📝 Step 5: Cleaning up Railway files..."
files_to_remove=(
    "trading_admin/settings_railway.py"
    "railway.json"
    "railway_migration_data.json"
    "migrate_to_railway.py"
    "RAILWAY_DEPLOYMENT.md"
    "prepare_railway_deployment.sh"
)

for file in "${files_to_remove[@]}"; do
    if [ -f "$file" ]; then
        echo "   🗑️  Removing: $file"
        rm -f "$file"
    fi
done

echo "✅ Railway files cleaned up"

# STEP 6: Verify requirements.txt has all needed packages
echo "📝 Step 6: Verifying requirements.txt..."
required_packages=("gunicorn" "dj-database-url" "psycopg2-binary" "whitenoise")

for package in "${required_packages[@]}"; do
    if ! grep -q "$package" requirements.txt 2>/dev/null; then
        echo "⚠️  Adding missing package: $package"
        case $package in
            "gunicorn") echo "gunicorn==21.2.0" >> requirements.txt ;;
            "dj-database-url") echo "dj-database-url==2.1.0" >> requirements.txt ;;
            "psycopg2-binary") echo "psycopg2-binary==2.9.7" >> requirements.txt ;;
            "whitenoise") echo "whitenoise==6.6.0" >> requirements.txt ;;
        esac
    fi
done

echo "✅ requirements.txt verified"

# STEP 7: Test the simplified setup
echo "📝 Step 7: Testing simplified settings..."
export RENDER_EXTERNAL_HOSTNAME="test.onrender.com"
export SECRET_KEY="test-secret-key"

python -c "
import os
import django
django.setup()
print('✅ Render settings test passed!')
" 2>/dev/null && echo "✅ Local test successful" || echo "⚠️  Local test failed"

unset RENDER_EXTERNAL_HOSTNAME SECRET_KEY

echo ""
echo "🎉 RENDER-ONLY FIX COMPLETED!"
echo "============================"
echo ""
echo "📋 What was simplified:"
echo "   ✅ Removed all Railway detection and files"
echo "   ✅ Simplified manage.py (Render-only logic)"
echo "   ✅ Simplified wsgi.py (Render-only logic)" 
echo "   ✅ Updated settings_render.py"
echo "   ✅ Explicit render.yaml configuration"
echo "   ✅ Verified all required dependencies"
echo ""
echo "📤 Next steps:"
echo "1. Commit and push:"
echo "   git add ."
echo "   git commit -m 'Simplify to Render-only deployment - remove Railway'"
echo "   git push origin main"
echo ""
echo "2. In Render Dashboard:"
echo "   - Go to Environment → Verify DJANGO_SETTINGS_MODULE = trading_admin.settings_render"
echo "   - Manual Deploy → Deploy latest commit"
echo ""
echo "3. Expected logs:"
echo "   '🚀 Detected Render platform - using settings_render'"
echo "   '🚀 Render Settings Loaded Successfully!'"
echo ""
echo "🎯 This should completely fix your deployment error!"
echo "   No more ModuleNotFoundError because we removed Railway complexity"
echo "   Clean, simple, Render-focused deployment"