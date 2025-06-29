import os
import sys
import dj_database_url
from .settings import *

# Environment validation for production
if os.getenv('RAILWAY_ENVIRONMENT'):
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        print("❌ ERROR: SECRET_KEY environment variable is required in production!")
        sys.exit(1)
else:
    SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-for-development')

# ✅ FIXED: Dynamic ALLOWED_HOSTS configuration
RAILWAY_DOMAIN = os.getenv('RAILWAY_STATIC_URL')
if RAILWAY_DOMAIN:
    # Production - use Railway domain
    ALLOWED_HOSTS = [
        RAILWAY_DOMAIN,
        '*.up.railway.app', 
        '*.railway.app'
    ]
    # Dynamic CORS origins for production
    CORS_ALLOWED_ORIGINS = [
        f'https://{RAILWAY_DOMAIN}',
    ]
    CORS_ALLOW_ALL_ORIGINS = False
else:
    # Development fallback
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']
    CORS_ALLOW_ALL_ORIGINS = True

# ✅ FIXED: Database configuration using dj-database-url
if os.getenv('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.parse(os.getenv('DATABASE_URL'))
    }
else:
    # Keep original database settings for local development
    pass

# ✅ FIXED: Static files configuration for Railway
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Use WhiteNoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ✅ FIXED: Security settings for Railway
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Security settings appropriate for Railway
SECURE_SSL_REDIRECT = False  # Railway handles SSL termination
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 0  # Railway handles this
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# ✅ FIXED: Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
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
    },
}

print(f"🔧 Railway Settings Loaded:")
print(f"   RAILWAY_DOMAIN: {RAILWAY_DOMAIN or 'Not set (development)'}")
print(f"   ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"   SECRET_KEY: {'✅ Set' if SECRET_KEY else '❌ Missing'}")
print(f"   DEBUG: {DEBUG}")
print(f"   DATABASE: {'✅ Railway PostgreSQL' if os.getenv('DATABASE_URL') else '❌ Local SQLite'}")
