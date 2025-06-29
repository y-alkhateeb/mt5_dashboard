# File: core/management/commands/reset_and_setup.py

import os
import shutil
import glob
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from django.db import connection
from django.conf import settings

class Command(BaseCommand):
    help = 'Reset everything: remove migrations, recreate from scratch, and setup admin user'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            default='admin',
            help='Admin username (default: admin)'
        )
        parser.add_argument(
            '--password',
            default='admin123',
            help='Admin password (default: admin123)'
        )
        parser.add_argument(
            '--email',
            default='admin@example.com',
            help='Admin email (default: admin@example.com)'
        )
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Skip migration reset (useful for production)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reset without confirmation'
        )
    
    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        skip_migrations = options['skip_migrations']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS('🔄 TRADING ROBOT ADMIN - COMPLETE RESET & SETUP')
        )
        self.stdout.write('=' * 60)
        
        # Confirmation for production safety
        if not force and not settings.DEBUG:
            confirm = input('⚠️  This will reset ALL data! Continue? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write('❌ Reset cancelled')
                return
        
        try:
            # Step 1: Remove migration files
            if not skip_migrations:
                self.reset_migrations()
            
            # Step 2: Reset database
            self.reset_database()
            
            # Step 3: Create fresh migrations
            if not skip_migrations:
                self.create_fresh_migrations()
            
            # Step 4: Apply migrations
            self.apply_migrations()
            
            # Step 5: Create admin user
            self.create_admin_user(username, password, email)
            
            # Step 6: Create sample data
            self.create_sample_data()
            
            # Step 7: Summary
            self.show_summary(username, password, email)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Reset failed: {str(e)}')
            )
            raise
    
    def reset_migrations(self):
        """Remove all migration files except __init__.py"""
        self.stdout.write('🗑️  Step 1: Removing migration files...')
        
        apps = ['core', 'licenses', 'configurations']
        
        for app in apps:
            migration_dir = os.path.join(app, 'migrations')
            if os.path.exists(migration_dir):
                # Remove all .py files except __init__.py
                migration_files = glob.glob(os.path.join(migration_dir, '*.py'))
                for file_path in migration_files:
                    if not file_path.endswith('__init__.py'):
                        os.remove(file_path)
                        self.stdout.write(f'   🗑️  Removed: {file_path}')
                
                # Remove __pycache__ directory
                pycache_dir = os.path.join(migration_dir, '__pycache__')
                if os.path.exists(pycache_dir):
                    shutil.rmtree(pycache_dir)
        
        self.stdout.write('   ✅ Migration files removed')
    
    def reset_database(self):
        """Reset the database"""
        self.stdout.write('💾 Step 2: Resetting database...')
        
        # For SQLite, we can just delete the file
        db_path = settings.DATABASES['default']['NAME']
        if isinstance(db_path, str) and db_path.endswith('.sqlite3'):
            if os.path.exists(db_path):
                os.remove(db_path)
                self.stdout.write(f'   🗑️  Removed SQLite database: {db_path}')
        else:
            # For PostgreSQL or other databases, drop and recreate tables
            self.stdout.write('   🔄 Flushing database...')
            try:
                call_command('flush', '--noinput', verbosity=0)
            except Exception as e:
                self.stdout.write(f'   ⚠️  Database flush failed: {e}')
        
        self.stdout.write('   ✅ Database reset complete')
    
    def create_fresh_migrations(self):
        """Create fresh migrations for all apps"""
        self.stdout.write('🔨 Step 3: Creating fresh migrations...')
        
        apps = ['configurations', 'licenses', 'core']  # Order matters for dependencies
        
        for app in apps:
            self.stdout.write(f'   📝 Creating migrations for {app}...')
            call_command('makemigrations', app, verbosity=1)
        
        self.stdout.write('   ✅ Fresh migrations created')
    
    def apply_migrations(self):
        """Apply all migrations"""
        self.stdout.write('🚀 Step 4: Applying migrations...')
        
        call_command('migrate', verbosity=1)
        
        self.stdout.write('   ✅ Migrations applied successfully')
    
    def create_admin_user(self, username, password, email):
        """Create admin user"""
        self.stdout.write('👤 Step 5: Creating admin user...')
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(f'   ⚠️  User "{username}" already exists, updating...')
            user = User.objects.get(username=username)
            user.set_password(password)
            user.email = email
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.save()
        else:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Admin',
                last_name='User'
            )
        
        self.stdout.write(f'   ✅ Admin user ready: {username}')
    
    def create_sample_data(self):
        """Create sample data if commands exist"""
        self.stdout.write('📊 Step 6: Creating sample data...')
        
        try:
            # Try to create default configurations
            call_command('create_default_configs', verbosity=0)
            self.stdout.write('   ✅ Default configurations created')
        except:
            self.stdout.write('   ⚠️  create_default_configs command not found, skipping')
        
        try:
            # Try to create sample data
            call_command('create_sample_data', '--clients', '3', verbosity=0)
            self.stdout.write('   ✅ Sample data created')
        except:
            self.stdout.write('   ⚠️  create_sample_data command not found, skipping')
    
    def show_summary(self, username, password, email):
        """Show completion summary"""
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS('🎉 RESET & SETUP COMPLETED SUCCESSFULLY!')
        )
        self.stdout.write('=' * 50)
        
        # Show database stats
        try:
            from licenses.models import License, Client
            from configurations.models import TradingConfiguration
            
            license_count = License.objects.count()
            client_count = Client.objects.count()
            config_count = TradingConfiguration.objects.count()
            admin_count = User.objects.filter(is_superuser=True).count()
            
            self.stdout.write('📊 Database Statistics:')
            self.stdout.write(f'   👤 Admin users: {admin_count}')
            self.stdout.write(f'   👥 Clients: {client_count}')
            self.stdout.write(f'   🔑 Licenses: {license_count}')
            self.stdout.write(f'   ⚙️  Configurations: {config_count}')
            
        except Exception as e:
            self.stdout.write(f'   ⚠️  Could not fetch stats: {e}')
        
        self.stdout.write('')
        self.stdout.write('🔐 Admin Credentials:')
        self.stdout.write(f'   Username: {username}')
        self.stdout.write(f'   Password: {password}')
        self.stdout.write(f'   Email: {email}')
        
        self.stdout.write('')
        self.stdout.write('🌐 Application URLs:')
        self.stdout.write('   Local: http://localhost:8000/admin/')
        self.stdout.write('   Production: https://mt5-dashboard.onrender.com/admin/')
        
        self.stdout.write('')
        self.stdout.write('📋 Next Steps:')
        self.stdout.write('   1. 🌐 Visit the admin panel')
        self.stdout.write('   2. 🔑 Login with the credentials above')
        self.stdout.write('   3. 🏠 Check the dashboard')
        self.stdout.write('   4. 🧪 Test the API endpoints')
        
        self.stdout.write('')
        self.stdout.write(
            self.style.WARNING('⚠️  IMPORTANT: Change the admin password in production!')
        )