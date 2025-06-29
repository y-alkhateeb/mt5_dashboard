"""
WSGI config for trading_admin project.
"""

import os
from django.core.wsgi import get_wsgi_application

# Smart settings detection for multiple platforms
if os.getenv('RENDER_EXTERNAL_HOSTNAME'):
    # On Render, use Render settings (Render sets RENDER_EXTERNAL_HOSTNAME automatically)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
elif os.getenv('RAILWAY_ENVIRONMENT'):
    # On Railway, use Railway settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_railway')
elif os.getenv('DJANGO_SETTINGS_MODULE'):
    # Use explicitly set settings module (already set)
    pass
else:
    # Local development, use local settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings')

application = get_wsgi_application()
