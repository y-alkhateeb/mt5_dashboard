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

# Dynamic ALLOWED_HOSTS from environment
RAILWAY_DOMAIN = os.getenv('RAILWAY_STATIC_URL', 'tradingadmin-production.up.railway.app')
ALLOWED_HOSTS = [
    RAILWAY_DOMAIN,
    '*.up.railway.app', 
    '*.railway.app'
]

# Dynamic CORS origins
CORS_ALLOWED_ORIGINS = [
    f'https://{RAILWAY_DOMAIN}',
    f'http://{RAILWAY_DOMAIN}',  # For development if needed
]

print(f"🔧 Railway Settings Loaded:")
print(f"   RAILWAY_DOMAIN: {RAILWAY_DOMAIN}")
print(f"   ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"   SECRET_KEY: {'✅ Set' if SECRET_KEY else '❌ Missing'}")