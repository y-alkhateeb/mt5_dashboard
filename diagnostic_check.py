#!/usr/bin/env python
"""
Database diagnostic script to check migration status and fix issues
Run: python diagnostic_check.py
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.apps import apps

def check_database_tables():
    """Check which tables exist in the database"""
    print("🔍 Checking existing database tables...")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
    
    print(f"📊 Found {len(tables)} tables:")
    for table in sorted(tables):
        print(f"   ✅ {table}")
    
    return tables

def check_migrations():
    """Check migration status"""
    print("\n🔍 Checking migration status...")
    
    try:
        call_command('showmigrations', verbosity=0)
    except Exception as e:
        print(f"❌ Error checking migrations: {e}")

def check_apps():
    """Check installed apps"""
    print("\n🔍 Checking installed apps...")
    
    for app_config in apps.get_app_configs():
        print(f"   📱 {app_config.name}")

def check_models():
    """Check if models can be imported"""
    print("\n🔍 Checking model imports...")
    
    try:
        from licenses.models import License, Client
        print("   ✅ licenses.models imported successfully")
    except Exception as e:
        print(f"   ❌ licenses.models import failed: {e}")
    
    try:
        from configurations.models import TradingConfiguration
        print("   ✅ configurations.models imported successfully")
    except Exception as e:
        print(f"   ❌ configurations.models import failed: {e}")

def check_migration_files():
    """Check if migration files exist"""
    print("\n🔍 Checking migration files...")
    
    apps_to_check = ['licenses', 'configurations', 'core']
    
    for app in apps_to_check:
        migrations_dir = f"{app}/migrations"
        if os.path.exists(migrations_dir):
            files = [f for f in os.listdir(migrations_dir) if f.endswith('.py') and f != '__init__.py']
            print(f"   📁 {app}/migrations/: {len(files)} files")
            for file in files:
                print(f"      📄 {file}")
        else:
            print(f"   ❌ {app}/migrations/ directory not found")

def main():
    print("🚀 Django Database Diagnostic")
    print("=" * 50)
    
    # Check migration files first
    check_migration_files()
    
    # Check apps
    check_apps()
    
    # Check model imports
    check_models()
    
    # Check database tables
    tables = check_database_tables()
    
    # Check what tables we expect
    expected_tables = [
        'licenses_client',
        'licenses_license', 
        'configurations_tradingconfiguration'
    ]
    
    print(f"\n🎯 Expected tables vs Found:")
    for table in expected_tables:
        if table in tables:
            print(f"   ✅ {table} - EXISTS")
        else:
            print(f"   ❌ {table} - MISSING")
    
    # Check migrations
    print(f"\n📋 Migration Status:")
    check_migrations()
    
    # Provide recommendations
    print(f"\n💡 Recommendations:")
    
    missing_tables = [table for table in expected_tables if table not in tables]
    if missing_tables:
        print(f"   🔧 Missing tables detected: {missing_tables}")
        print(f"   📝 Run the following commands:")
        print(f"      python manage.py makemigrations")
        print(f"      python manage.py migrate")
    else:
        print(f"   ✅ All expected tables are present!")

if __name__ == "__main__":
    main()