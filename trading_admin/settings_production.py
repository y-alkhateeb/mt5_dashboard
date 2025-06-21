# File: trading_admin/settings_production.py

from .settings import *
import secrets
import string

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY: Generate a strong SECRET_KEY
SECRET_KEY = 'django-trading-robot-' + ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*') for i in range(50))

# SECURITY: Set your domain
ALLOWED_HOSTS = [
    'your-domain.com',
    'www.your-domain.com', 
    'localhost',
    '127.0.0.1',
    # Add your server IP here
]

# SECURITY: SSL/HTTPS Settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# SECURITY: Secure Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# SECURITY: Additional Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'same-origin'

# Database for production (PostgreSQL recommended)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'trading_admin_prod',
        'USER': 'trading_admin_user',
        'PASSWORD': 'your-secure-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files for production
STATIC_ROOT = '/var/www/trading_admin/static/'
MEDIA_ROOT = '/var/www/trading_admin/media/'

# Logging for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/trading_admin/django.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}