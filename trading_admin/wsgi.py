import os
from django.core.wsgi import get_wsgi_application

# Use Railway settings by default
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_railway')

application = get_wsgi_application()