"""
WSGI config for trading_admin project.
"""

import os
from django.core.wsgi import get_wsgi_application

# SIMPLIFIED: Render-only detection

# Priority 1: Explicit environment variable (for Render dashboard setting)
if os.getenv('DJANGO_SETTINGS_MODULE'):
    # Already set by Render dashboard, use it
    pass
    
# Priority 2: Render platform detection
elif os.getenv('RENDER_EXTERNAL_HOSTNAME'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
    
# Priority 3: Local development fallback
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings')

application = get_wsgi_application()
