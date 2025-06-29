#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

if __name__ == '__main__':
    # SIMPLIFIED: Render-only detection
    
    # Priority 1: Explicit environment variable (for Render dashboard setting)
    if os.getenv('DJANGO_SETTINGS_MODULE'):
        print(f"🔧 Using explicit DJANGO_SETTINGS_MODULE: {os.getenv('DJANGO_SETTINGS_MODULE')}")
    
    # Priority 2: Render platform detection  
    elif os.getenv('RENDER_EXTERNAL_HOSTNAME'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
        print("🚀 Detected Render platform - using settings_render")
    
    # Priority 3: Local development fallback
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings')
        print("💻 Using local development settings")
    
    # Debug info
    print(f"📍 Final settings module: {os.getenv('DJANGO_SETTINGS_MODULE')}")
    print(f"🌐 RENDER_EXTERNAL_HOSTNAME: {os.getenv('RENDER_EXTERNAL_HOSTNAME', 'Not set')}")
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    execute_from_command_line(sys.argv)
