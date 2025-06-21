# File: app.py

import os
import sys
from django.core.wsgi import get_wsgi_application

# Add your project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set Django settings module for SmarterASP.net
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_smarterasp')

# Get WSGI application
application = get_wsgi_application()