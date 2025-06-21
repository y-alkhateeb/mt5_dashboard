# File: trading_admin/settings_railway.py

import os
import dj_database_url
from .settings import *

# Railway environment detection
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-change-this')
# ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',') if os.getenv('ALLOWED_HOSTS') else ['*']
ALLOWED_HOSTS = "http://production-europe-west4-drams3a.railway-registry.com/"
# Railway PostgreSQL Database with fallback
if os.getenv('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback to SQLite for testing (Railway should provide DATABASE_URL)
    print("⚠️ WARNING: No DATABASE_URL found, using SQLite fallback")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/db.sqlite3',  # Use /tmp for Railway
        }
    }

# Static files configuration for Railway
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Create staticfiles directory if it doesn't exist
import pathlib
pathlib.Path(STATIC_ROOT).mkdir(parents=True, exist_ok=True)

# Use WhiteNoise for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Middleware with WhiteNoise
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Security settings for Railway
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS settings
# RAILWAY_PUBLIC_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN')
RAILWAY_PUBLIC_DOMAIN = "http://production-europe-west4-drams3a.railway-registry.com/"
if RAILWAY_PUBLIC_DOMAIN:
    CORS_ALLOWED_ORIGINS = [
        f"https://{RAILWAY_PUBLIC_DOMAIN}",
    ]
else:
    CORS_ALLOW_ALL_ORIGINS = True  # For development

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
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
}

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

print(f"🔧 Django Settings Loaded:")
print(f"   DEBUG: {DEBUG}")
print(f"   DATABASE: {'PostgreSQL' if os.getenv('DATABASE_URL') else 'SQLite Fallback'}")
print(f"   STATIC_ROOT: {STATIC_ROOT}")
print(f"   ALLOWED_HOSTS: {ALLOWED_HOSTS}")