#!/usr/bin/env python
"""
Fixed Python script to fix missing database tables
Run: python fix_migrations.py
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def get_all_tables():
    """Get all tables in the database"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row[0] for row in cursor.fetchall()]

def check_table_exists(table_name, existing_tables):
    """Check if a table exists in the list of existing tables"""
    return table_name in existing_tables

def create_migrations():
    """Create migrations for all apps"""
    print("🔨 Creating migrations...")
    
    apps = ['licenses', 'configurations', 'core']
    
    for app in apps:
        try:
            print(f"   📱 Creating {app} migrations...")
            call_command('makemigrations', app, verbosity=1)
        except Exception as e:
            print(f"   ⚠️  Warning for {app}: {e}")

def apply_migrations():
    """Apply all migrations"""
    print("🚀 Applying migrations...")
    try:
        call_command('migrate', verbosity=1)
        print("   ✅ Migrations applied successfully")
    except Exception as e:
        print(f"   ❌ Error applying migrations: {e}")
        return False
    return True

def verify_tables():
    """Verify that required tables exist"""
    print("✅ Verifying database tables...")
    
    # Get all existing tables
    try:
        existing_tables = get_all_tables()
        print(f"   📊 Found {len(existing_tables)} tables in database")
    except Exception as e:
        print(f"   ❌ Error getting table list: {e}")
        return False
    
    required_tables = {
        'licenses_client': 'Client model table',
        'licenses_license': 'License model table',
        'configurations_tradingconfiguration': 'TradingConfiguration model table'
    }
    
    all_good = True
    
    for table, description in required_tables.items():
        if check_table_exists(table, existing_tables):
            print(f"   ✅ {table} - {description}")
        else:
            print(f"   ❌ {table} - {description} (MISSING)")
            all_good = False
    
    if existing_tables:
        print(f"\n   📋 All tables in database:")
        for table in sorted(existing_tables):
            status = "✅" if table in required_tables else "ℹ️"
            print(f"      {status} {table}")
    
    return all_good

def show_migration_status():
    """Show current migration status"""
    print("📋 Migration status:")
    try:
        call_command('showmigrations', verbosity=1)
    except Exception as e:
        print(f"   ❌ Error showing migrations: {e}")

def main():
    print("🔧 Django Migration Fix Tool v2")
    print("=" * 45)
    
    # Step 1: Check current state
    print("\n📊 Step 1: Checking current state...")
    if verify_tables():
        print("✅ All required tables exist! No fix needed.")
        return
    
    # Step 2: Show current migration status
    print("\n📋 Step 2: Current migration status...")
    show_migration_status()
    
    # Step 3: Create migrations
    print("\n🔨 Step 3: Creating missing migrations...")
    create_migrations()
    
    # Step 4: Apply migrations
    print("\n🚀 Step 4: Applying migrations...")
    if not apply_migrations():
        print("❌ Migration failed. Please check the error messages above.")
        return
    
    # Step 5: Verify final state
    print("\n✅ Step 5: Final verification...")
    if verify_tables():
        print("\n🎉 SUCCESS! All required tables are now present.")
        print("\n📱 Next steps:")
        print("   1. Start the server: python manage.py runserver")
        print("   2. Visit admin: http://localhost:8000/admin/")
        print("   3. Visit dashboard: http://localhost:8000/dashboard/")
        print("   4. Test configurations: http://localhost:8000/admin/configurations/tradingconfiguration/")
    else:
        print("\n❌ Some tables are still missing. Manual intervention may be required.")
        print("\n🔧 Try these manual commands:")
        print("   python manage.py makemigrations")
        print("   python manage.py migrate --run-syncdb")

if __name__ == "__main__":
    main()