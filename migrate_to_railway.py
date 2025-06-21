#!/usr/bin/env python
"""
Migration script to move data from SmarterASP.net to Railway
"""
import os
import django
import json

def migrate_data():
    """Migrate data to Railway PostgreSQL"""
    
    print("🚀 Starting data migration to Railway...")
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings_railway')
    django.setup()
    
    from django.core.management import call_command
    from django.db import transaction
    
    try:
        with transaction.atomic():
            print("📊 Loading data into Railway database...")
            
            # Load the data
            call_command('loaddata', 'railway_migration_data.json')
            
            print("✅ Data migration completed successfully!")
            
            # Show summary
            from licenses.models import License, Client
            from configurations.models import TradingConfiguration
            from django.contrib.auth.models import User
            
            print(f"📈 Migration Summary:")
            print(f"   Users: {User.objects.count()}")
            print(f"   Clients: {Client.objects.count()}")
            print(f"   Licenses: {License.objects.count()}")
            print(f"   Configurations: {TradingConfiguration.objects.count()}")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("🔧 Try running migrations first: python manage.py migrate")

if __name__ == "__main__":
    migrate_data()