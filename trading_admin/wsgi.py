"""
WSGI config for trading_admin project.
"""

import os
from django.core.wsgi import get_wsgi_application

# Smart settings detection for multiple platforms (same as manage.py)
if os.getenv('RENDER'):
    # On Render, use Render settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
elif os.getenv('RAILWAY_ENVIRONMENT'):
    # On Railway, use Railway settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_railway')
else:
    # Local development, use local settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings')

application = get_wsgi_application()
