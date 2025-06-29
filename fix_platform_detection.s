#!/bin/bash
# File: fix_platform_detection.sh
# Purpose: Fix platform detection loading wrong settings

echo "🔧 Fixing Platform Detection Issue"
echo "================================="
echo ""

echo "The issue: Your app is loading Railway settings instead of Render settings!"
echo ""

# Fix 1: Update manage.py with better detection
echo "📝 Fixing manage.py..."
cat > manage.py << 'EOF'
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

if __name__ == '__main__':
    # FIXED: Better platform detection for Render vs Railway
    
    # Check for explicit settings module first
    if os.getenv('DJANGO_SETTINGS_MODULE'):
        print(f"⚙️ Using explicitly set settings: {os.getenv('DJANGO_SETTINGS_MODULE')}")
    # Check for Render (Render sets RENDER_EXTERNAL_HOSTNAME)
    elif os.getenv('RENDER_EXTERNAL_HOSTNAME'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
        print("🚀 Using Render settings (detected RENDER_EXTERNAL_HOSTNAME)")
    # Check for Railway (Railway sets RAILWAY_ENVIRONMENT) 
    elif os.getenv('RAILWAY_ENVIRONMENT'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_railway')
        print("🚂 Using Railway settings (detected RAILWAY_ENVIRONMENT)")
    else:
        # Local development
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

# Fix 2: Update wsgi.py with better detection
echo "📝 Fixing wsgi.py..."
cat > trading_admin/wsgi.py << 'EOF'
"""
WSGI config for trading_admin project.
"""

import os
from django.core.wsgi import get_wsgi_application

# FIXED: Better platform detection for Render vs Railway

# Check for explicit settings module first
if os.getenv('DJANGO_SETTINGS_MODULE'):
    # Already set, don't override
    pass
# Check for Render (Render sets RENDER_EXTERNAL_HOSTNAME)
elif os.getenv('RENDER_EXTERNAL_HOSTNAME'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
# Check for Railway (Railway sets RAILWAY_ENVIRONMENT)
elif os.getenv('RAILWAY_ENVIRONMENT'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_railway')
else:
    # Local development
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings')

application = get_wsgi_application()
EOF

echo "✅ wsgi.py fixed"

# Fix 3: Ensure Render settings exist and are correct
echo "📝 Creating/fixing Render settings..."
cat > trading_admin/settings_render.py << 'EOF'
import os
import sys
import dj_database_url
from .settings import *

# Environment validation for production
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    # Auto-generate SECRET_KEY if not provided (for easier deployment)
    from django.core.management.utils import get_random_secret_key
    SECRET_KEY = get_random_secret_key()
    print(f"⚠️  WARNING: SECRET_KEY not provided, auto-generated one for this session")

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

echo "✅ Render settings fixed"

# Fix 4: Update Render dashboard environment variable
echo ""
echo "🎯 CRITICAL: Update Render Dashboard Settings"
echo "============================================="
echo ""
echo "Go to Render Dashboard → Your Web Service → Environment"
echo "Make sure this environment variable is set:"
echo ""
echo "   Key: DJANGO_SETTINGS_MODULE"
echo "   Value: trading_admin.settings_render"
echo ""
echo "If it's set to 'trading_admin.settings_railway', change it!"

# Commit changes
echo "📤 Committing fixes..."
git add manage.py trading_admin/wsgi.py trading_admin/settings_render.py
git commit -m "Fix platform detection - use Render settings not Railway"
git push origin main

echo "✅ Changes pushed to GitHub"
echo ""
echo "🚀 NEXT STEPS:"
echo "1. ✅ Go to Render Dashboard → Your Service → Environment"
echo "2. ✅ Verify DJANGO_SETTINGS_MODULE = trading_admin.settings_render"
echo "3. ✅ Manual Deploy → Deploy latest commit"
echo "4. ✅ Watch logs - should show '🚀 Render Settings Loaded:'"
echo "5. ✅ Try admin login again"
echo ""
echo "🔍 The issue was: Platform detection was loading Railway settings"
echo "   instead of Render settings, causing authentication problems."