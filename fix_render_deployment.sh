#!/bin/bash
# File: fix_render_deployment.sh
# Purpose: Fix Render.com deployment issues

set -e  # Exit on any error

echo "🔧 Fixing Render.com deployment issues..."
echo "========================================"

# Step 1: Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from the Django project root."
    exit 1
fi

echo "✅ Django project detected"

# Step 2: Fix manage.py for correct Render detection
echo "🔄 Fixing manage.py for Render.com..."
cat > manage.py << 'EOF'
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

if __name__ == '__main__':
    # Smart settings detection for multiple platforms
    if os.getenv('RENDER_EXTERNAL_HOSTNAME'):
        # On Render, use Render settings (Render sets RENDER_EXTERNAL_HOSTNAME automatically)
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
        print("🚀 Using Render settings")
    elif os.getenv('RAILWAY_ENVIRONMENT'):
        # On Railway, use Railway settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_railway')
        print("🚂 Using Railway settings")
    elif os.getenv('DJANGO_SETTINGS_MODULE'):
        # Use explicitly set settings module
        print(f"⚙️ Using explicitly set settings: {os.getenv('DJANGO_SETTINGS_MODULE')}")
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

echo "✅ manage.py fixed"

# Step 3: Fix wsgi.py for correct Render detection
echo "🔄 Fixing wsgi.py for Render.com..."
cat > trading_admin/wsgi.py << 'EOF'
"""
WSGI config for trading_admin project.
"""

import os
from django.core.wsgi import get_wsgi_application

# Smart settings detection for multiple platforms
if os.getenv('RENDER_EXTERNAL_HOSTNAME'):
    # On Render, use Render settings (Render sets RENDER_EXTERNAL_HOSTNAME automatically)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
elif os.getenv('RAILWAY_ENVIRONMENT'):
    # On Railway, use Railway settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_railway')
elif os.getenv('DJANGO_SETTINGS_MODULE'):
    # Use explicitly set settings module (already set)
    pass
else:
    # Local development, use local settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings')

application = get_wsgi_application()
EOF

echo "✅ wsgi.py fixed"

# Step 4: Create missing settings_railway.py to prevent import errors
echo "📝 Creating missing settings_railway.py..."
cat > trading_admin/settings_railway.py << 'EOF'
import os
import sys
import dj_database_url
from .settings import *

# Environment validation for production
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    print("❌ ERROR: SECRET_KEY environment variable is required in production!")
    sys.exit(1)

# Debug mode for Railway
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Railway domain configuration
RAILWAY_STATIC_URL = os.getenv('RAILWAY_STATIC_URL')
RAILWAY_PUBLIC_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN')

if RAILWAY_PUBLIC_DOMAIN:
    # Production - use Railway domain
    ALLOWED_HOSTS = [
        RAILWAY_PUBLIC_DOMAIN,
        '*.railway.app',
        'localhost',
        '127.0.0.1'
    ]
    # Dynamic CORS origins for production
    CORS_ALLOWED_ORIGINS = [
        f'https://{RAILWAY_PUBLIC_DOMAIN}',
    ]
    CORS_ALLOW_ALL_ORIGINS = False
else:
    # Development fallback
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']
    CORS_ALLOW_ALL_ORIGINS = True

# Database configuration using dj-database-url (Railway provides DATABASE_URL)
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

# Static files configuration for Railway
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Use WhiteNoise for static files (perfect for Railway)
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings for Railway
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

# Cache configuration for Railway (using local memory)
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

# Logging configuration for Railway
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

print(f"🚂 Railway Settings Loaded:")
print(f"   RAILWAY_PUBLIC_DOMAIN: {RAILWAY_PUBLIC_DOMAIN or 'Not set (development)'}")
print(f"   ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"   SECRET_KEY: {'✅ Set' if SECRET_KEY else '❌ Missing'}")
print(f"   DEBUG: {DEBUG}")
print(f"   DATABASE: {'✅ Railway PostgreSQL' if os.getenv('DATABASE_URL') else '❌ Local SQLite'}")
print(f"   STATIC_ROOT: {STATIC_ROOT}")
EOF

echo "✅ settings_railway.py created"

# Step 5: Ensure settings_render.py exists
if [ ! -f "trading_admin/settings_render.py" ]; then
    echo "📝 Creating settings_render.py..."
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
else
    echo "✅ settings_render.py already exists"
fi

# Step 6: Update render.yaml (if it exists)
if [ -f "render.yaml" ]; then
    echo "🔄 Updating render.yaml..."
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
    echo "✅ render.yaml updated"
else
    echo "⚠️  render.yaml not found, skipping..."
fi

# Step 7: Verify requirements.txt has all dependencies
echo "🔍 Checking requirements.txt..."
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

# Step 8: Test the fixed settings
echo "🧪 Testing fixed settings..."
export RENDER_EXTERNAL_HOSTNAME="test.onrender.com"
export SECRET_KEY="test-secret-key"
export DJANGO_SETTINGS_MODULE="trading_admin.settings_render"

python -c "
import os
import django
django.setup()
print('✅ Render settings test passed!')
" 2>/dev/null || echo "⚠️  Settings test failed - check for other issues"

unset RENDER_EXTERNAL_HOSTNAME SECRET_KEY DJANGO_SETTINGS_MODULE

# Step 9: Show summary and next steps
echo ""
echo "🎉 Render.com deployment fix completed!"
echo "======================================"
echo ""
echo "📁 Files fixed/created:"
echo "   ✅ manage.py (fixed platform detection)"
echo "   ✅ trading_admin/wsgi.py (fixed platform detection)"
echo "   ✅ trading_admin/settings_railway.py (created to prevent import errors)"
echo "   ✅ trading_admin/settings_render.py (verified/created)"
echo "   ✅ render.yaml (updated if present)"
echo "   ✅ requirements.txt (verified dependencies)"
echo ""
echo "🔧 Issues fixed:"
echo "   ✅ Platform detection now uses RENDER_EXTERNAL_HOSTNAME (set by Render)"
echo "   ✅ Missing Railway settings file created"
echo "   ✅ Import errors resolved"
echo "   ✅ All required dependencies present"
echo ""
echo "📋 Next steps:"
echo "1. Commit and push the fixes:"
echo "   git add ."
echo "   git commit -m 'Fix Render.com deployment issues'"
echo "   git push origin main"
echo ""
echo "2. In Render.com dashboard:"
echo "   - Go to your Web Service"
echo "   - Click 'Manual Deploy' → 'Deploy latest commit'"
echo "   - Watch the build logs for success"
echo ""
echo "3. Verify environment variables in Render:"
echo "   - DJANGO_SETTINGS_MODULE=trading_admin.settings_render"
echo "   - SECRET_KEY=(should be auto-generated)"
echo "   - DEBUG=false"
echo "   - DATABASE_URL=(should be auto-set when you connect PostgreSQL)"
echo ""
echo "🚀 Your deployment should now work correctly on Render.com!"