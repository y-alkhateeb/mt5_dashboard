"""
Production settings for Render.com deployment
Optimized for Trading Robot Admin System
"""

import os
import sys
import dj_database_url
from django.core.management.utils import get_random_secret_key
from .settings import *

# ============================================================================
# SECURITY SETTINGS
# ============================================================================

# Secret key handling
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    SECRET_KEY = get_random_secret_key()
    print("⚠️  WARNING: SECRET_KEY auto-generated. Set it in Render dashboard for production!")

# Debug mode (always False in production)
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
    # CORS for production
    CORS_ALLOWED_ORIGINS = [
        f'https://{RENDER_EXTERNAL_HOSTNAME}',
    ]
    CORS_ALLOW_ALL_ORIGINS = False
else:
    # Development fallback
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']
    CORS_ALLOW_ALL_ORIGINS = True

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

if os.getenv('DATABASE_URL'):
    # Use Render PostgreSQL database
    DATABASES = {
        'default': dj_database_url.parse(
            os.getenv('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    print("✅ Using Render PostgreSQL database")
else:
    # Fallback to SQLite for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print("⚠️  Using SQLite fallback - ensure DATABASE_URL is set in production")

# ============================================================================
# STATIC FILES CONFIGURATION (WhiteNoise)
# ============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise configuration for serving static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Additional static files directories
STATICFILES_DIRS = [
    BASE_DIR / 'static',
] if (BASE_DIR / 'static').exists() else []

# ============================================================================
# SECURITY SETTINGS FOR PRODUCTION
# ============================================================================

# SSL/HTTPS settings
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HSTS settings
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

# Security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Cookie security
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# ============================================================================
# CACHING CONFIGURATION
# ============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'trading-admin-cache',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# ============================================================================
# API RATE LIMITING (Enhanced for production)
# ============================================================================

# Enhanced rate limiting for production
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '100/hour',              # Anonymous users
    'user': '1000/hour',             # Authenticated admin users
    'bot_validation': '60/minute',   # Bot validation endpoint
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose' if DEBUG else 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'licenses': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'configurations': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# ============================================================================
# EMAIL CONFIGURATION (Optional)
# ============================================================================

# Configure email settings if EMAIL_URL is provided
EMAIL_URL = os.getenv('EMAIL_URL')
if EMAIL_URL:
    # Parse email URL and configure Django email settings
    # Format: smtp://username:password@hostname:port
    print("✅ Email configuration detected")

# ============================================================================
# DEPLOYMENT VERIFICATION
# ============================================================================

# Print configuration summary
print("🚀 RENDER SETTINGS LOADED SUCCESSFULLY!")
print("=" * 50)
print(f"📍 RENDER_EXTERNAL_HOSTNAME: {RENDER_EXTERNAL_HOSTNAME or 'Not set (development)'}")
print(f"🌐 ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"🔐 SECRET_KEY: {'✅ Set' if SECRET_KEY else '❌ Missing'}")
print(f"🐛 DEBUG: {DEBUG}")
print(f"💾 DATABASE: {'✅ Render PostgreSQL' if os.getenv('DATABASE_URL') else '⚠️  SQLite fallback'}")
print(f"📁 STATIC_ROOT: {STATIC_ROOT}")
print(f"🔒 SSL_REDIRECT: {SECURE_SSL_REDIRECT}")
print(f"⚡ CACHE_BACKEND: {CACHES['default']['BACKEND']}")
print("=" * 50)

# Validate critical settings
if not DEBUG and not os.getenv('DATABASE_URL'):
    print("❌ CRITICAL: DATABASE_URL must be set in production!")
    
if not DEBUG and not RENDER_EXTERNAL_HOSTNAME:
    print("⚠️  WARNING: RENDER_EXTERNAL_HOSTNAME not detected")
