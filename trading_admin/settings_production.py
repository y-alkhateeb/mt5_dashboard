# File: trading_admin/settings_production.py

from .settings import *
import os
from decouple import config

# Security
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='trading_admin_prod'),
        'USER': config('DB_USER', default='trading_admin_user'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='db'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'sslmode': 'prefer',
        },
    }
}

# Redis
REDIS_URL = config('REDIS_URL', default='redis://redis:6379/0')

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
    }
}

# Security settings (without SSL)
# SECURE_SSL_REDIRECT = True  # Disabled - no SSL yet
# SECURE_HSTS_SECONDS = 31536000  # Disabled - no SSL yet
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Disabled - no SSL yet
# SECURE_HSTS_PRELOAD = True  # Disabled - no SSL yet
# SESSION_COOKIE_SECURE = True  # Disabled - no SSL yet
# CSRF_COOKIE_SECURE = True  # Disabled - no SSL yet

# Basic security (without SSL)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Static files
STATIC_ROOT = '/app/staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Logging
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
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
}