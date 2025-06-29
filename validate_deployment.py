#!/usr/bin/env python
"""
Deployment validation script for Trading Robot Admin
Run this after deployment to verify everything works
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_render')
django.setup()

def validate_deployment():
    """Validate deployment configuration"""
    print("🔍 DEPLOYMENT VALIDATION")
    print("=" * 30)
    
    # Check Django settings
    from django.conf import settings
    print(f"✅ Django settings: {settings.SETTINGS_MODULE}")
    print(f"✅ Debug mode: {settings.DEBUG}")
    print(f"✅ Allowed hosts: {settings.ALLOWED_HOSTS}")
    
    # Check database connection
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    # Check models
    try:
        from licenses.models import License, Client
        from configurations.models import TradingConfiguration
        print(f"✅ License model: {License.objects.count()} records")
        print(f"✅ Client model: {Client.objects.count()} records")
        print(f"✅ Configuration model: {TradingConfiguration.objects.count()} records")
    except Exception as e:
        print(f"❌ Model validation failed: {e}")
    
    # Check admin user
    try:
        from django.contrib.auth.models import User
        admin_count = User.objects.filter(is_superuser=True).count()
        print(f"✅ Admin users: {admin_count}")
    except Exception as e:
        print(f"❌ Admin user check failed: {e}")
    
    # Check static files
    import os
    static_root = getattr(settings, 'STATIC_ROOT', None)
    if static_root and os.path.exists(static_root):
        print("✅ Static files directory exists")
    else:
        print("⚠️  Static files directory not found")
    
    print("=" * 30)
    print("🎉 Validation completed!")

if __name__ == '__main__':
    validate_deployment()
