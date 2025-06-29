import os
from django.core.wsgi import get_wsgi_application

# Smart settings detection (same as manage.py)
if os.getenv('RAILWAY_ENVIRONMENT'):
    # On Railway, use Railway settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_railway')
else:
    # Local development, use local settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings')

application = get_wsgi_application()