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
