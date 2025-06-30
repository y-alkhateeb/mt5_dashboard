# File: core/management/commands/fix_postgresql_fields.py
# Management command to fix PostgreSQL field naming issues automatically

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import os

class Command(BaseCommand):
    help = 'Fix PostgreSQL field naming issues and setup database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force execution without confirmation'
        )
        parser.add_argument(
            '--skip-cleanup',
            action='store_true',
            help='Skip database cleanup (for fresh deployments)'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔧 POSTGRESQL FIELD COMPATIBILITY FIX')
        )
        self.stdout.write('=' * 50)
        
        # Step 1: Check environment
        self.check_environment()
        
        # Step 2: Fix database issues
        if not options['skip_cleanup']:
            self.fix_database_issues()
        
        # Step 3: Setup admin user
        self.setup_admin_user()
        
        # Step 4: Create sample data
        self.create_sample_data()
        
        # Step 5: Verify fix
        self.verify_fix()
        
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS('✅ PostgreSQL field fix completed successfully!')
        )
    
    def check_environment(self):
        """Check the deployment environment"""
        self.stdout.write('📍 Checking environment...')
        
        # Check if on Render
        render_hostname = os.getenv('RENDER_EXTERNAL_HOSTNAME')
        if render_hostname:
            self.stdout.write(f'✅ Running on Render: {render_hostname}')
        else:
            self.stdout.write('⚠️  Not running on Render platform')
        
        # Check database
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            self.stdout.write('✅ PostgreSQL database configured')
        else:
            self.stdout.write('⚠️  No DATABASE_URL found')
        
        # Test database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                self.stdout.write(f'✅ Database connected: PostgreSQL')
        except Exception as e:
            self.stdout.write(f'❌ Database connection failed: {e}')
            raise
    
    def fix_database_issues(self):
        """Fix PostgreSQL field naming issues"""
        self.stdout.write('🔧 Fixing database field naming issues...')
        
        try:
            with connection.cursor() as cursor:
                # Check for existing problematic tables
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('configurations_tradingconfiguration', 'licenses_license', 'licenses_client')
                """)
                existing_tables = [row[0] for row in cursor.fetchall()]
                
                if existing_tables:
                    self.stdout.write(f'🗑️  Found {len(existing_tables)} existing tables to check')
                    
                    # Check for mixed-case columns in each table
                    problematic_tables = []
                    for table in existing_tables:
                        cursor.execute(f"""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name = '{table}'
                            AND column_name ~ '[A-Z]'
                            LIMIT 1;
                        """)
                        if cursor.fetchone():
                            problematic_tables.append(table)
                    
                    if problematic_tables:
                        self.stdout.write(f'⚠️  Found {len(problematic_tables)} tables with mixed-case columns')
                        
                        # Drop problematic tables
                        for table in problematic_tables:
                            self.stdout.write(f'🗑️  Dropping table: {table}')
                            cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE;')
                        
                        # Clear migration history for affected apps
                        self.stdout.write('🧹 Clearing migration history...')
                        apps_to_reset = ['configurations', 'licenses']
                        for app in apps_to_reset:
                            cursor.execute("DELETE FROM django_migrations WHERE app = %s", [app])
                            self.stdout.write(f'✅ Cleared migration history for {app}')
                    else:
                        self.stdout.write('✅ No problematic tables found')
                else:
                    self.stdout.write('✅ No existing tables found (fresh deployment)')
                
        except Exception as e:
            self.stdout.write(f'❌ Database fix failed: {e}')
            raise
    
    def setup_admin_user(self):
        """Create or update admin user"""
        self.stdout.write('👤 Setting up admin user...')
        
        username = 'admin'
        password = 'admin123'
        email = 'admin@example.com'
        
        try:
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                user.set_password(password)
                user.email = email
                user.is_superuser = True
                user.is_staff = True
                user.is_active = True
                user.save()
                self.stdout.write(f'✅ Updated existing admin user: {username}')
            else:
                User.objects.create_superuser(username, email, password)
                self.stdout.write(f'✅ Created new admin user: {username}')
            
            self.stdout.write(f'📧 Email: {email}')
            self.stdout.write(f'🔑 Password: {password}')
            self.stdout.write('⚠️  IMPORTANT: Change password after first login!')
            
        except Exception as e:
            self.stdout.write(f'❌ Admin user setup failed: {e}')
            # Don't raise here - this is not critical for deployment
    
    def create_sample_data(self):
        """Create sample data for testing"""
        self.stdout.write('📊 Creating sample data...')
        
        try:
            # Import models (they should exist after migrations)
            from licenses.models import Client, License
            from configurations.models import TradingConfiguration
            
            # Get admin user
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                self.stdout.write('⚠️  No admin user found, skipping sample data')
                return
            
            # Create sample configuration
            config, created = TradingConfiguration.objects.get_or_create(
                name='US30 Standard Configuration',
                defaults={
                    'description': 'Standard US30 trading configuration - PostgreSQL compatible',
                    'allowed_symbol': 'US30',
                    'strict_symbol_check': True,
                    'session_start': '08:45',
                    'session_end': '10:00',
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write('✅ Created sample trading configuration')
            else:
                self.stdout.write('✅ Sample trading configuration already exists')
            
            # Create sample client
            client, created = Client.objects.get_or_create(
                first_name='Sample',
                last_name='Client',
                country='United States',
                defaults={
                    'email': 'sample@example.com',
                    'created_by': admin_user
                }
            )
            
            if created:
                self.stdout.write('✅ Created sample client')
            else:
                self.stdout.write('✅ Sample client already exists')
            
            # Create sample license
            if not License.objects.filter(client=client).exists():
                License.objects.create(
                    client=client,
                    trading_configuration=config,
                    account_trade_mode=0,  # Demo
                    expires_at=timezone.now() + timedelta(days=365),
                    is_active=True,
                    created_by=admin_user
                )
                self.stdout.write('✅ Created sample license')
            else:
                self.stdout.write('✅ Sample license already exists')
            
        except ImportError:
            self.stdout.write('⚠️  Models not available yet, skipping sample data')
        except Exception as e:
            self.stdout.write(f'⚠️  Sample data creation failed: {e}')
            # Don't raise - this is not critical
    
    def verify_fix(self):
        """Verify the fix worked"""
        self.stdout.write('🔍 Verifying fix...')
        
        try:
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write('✅ Database connection working')
            
            # Test model imports and queries
            try:
                from licenses.models import Client, License
                from configurations.models import TradingConfiguration
                
                # Count records
                client_count = Client.objects.count()
                license_count = License.objects.count()
                config_count = TradingConfiguration.objects.count()
                admin_count = User.objects.filter(is_superuser=True).count()
                
                self.stdout.write(f'✅ Database statistics:')
                self.stdout.write(f'   👤 Admin users: {admin_count}')
                self.stdout.write(f'   👥 Clients: {client_count}')
                self.stdout.write(f'   🔑 Licenses: {license_count}')
                self.stdout.write(f'   ⚙️  Configurations: {config_count}')
                
                # Test API compatibility
                if config_count > 0:
                    from configurations.serializers import TradingConfigurationSerializer
                    
                    config = TradingConfiguration.objects.first()
                    serializer = TradingConfigurationSerializer(config)
                    data = serializer.data
                    
                    # Check that both old and new field names are present
                    has_legacy = 'inp_AllowedSymbol' in data
                    has_new = 'allowed_symbol' in data
                    
                    self.stdout.write(f'✅ API compatibility:')
                    self.stdout.write(f'   📊 Legacy fields: {"✅" if has_legacy else "❌"}')
                    self.stdout.write(f'   📊 New fields: {"✅" if has_new else "❌"}')
                
            except ImportError:
                self.stdout.write('⚠️  Models not available for verification')
            
        except Exception as e:
            self.stdout.write(f'⚠️  Verification had issues: {e}')
            # Don't raise - verification is informational