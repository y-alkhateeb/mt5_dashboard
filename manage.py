#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

if __name__ == '__main__':
    # Smart settings detection for multiple platforms
    if os.getenv('RENDER_EXTERNAL_HOSTNAME'):
        # On Render, use Render settings (Render sets RENDER_EXTERNAL_HOSTNAME automatically)
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
        print("🚀 Using Render settings")
    elif os.getenv('RAILWAY_ENVIRONMENT'):
        # On Railway, use Railway settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_railway')
        print("🚂 Using Railway settings")
    elif os.getenv('DJANGO_SETTINGS_MODULE'):
        # Use explicitly set settings module
        print(f"⚙️ Using explicitly set settings: {os.getenv('DJANGO_SETTINGS_MODULE')}")
    else:
        # Local development, use local settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings')
        print("💻 Using local development settings")
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
