from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from licenses.models import Client, License
from configurations.models import TradingConfiguration
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Create comprehensive sample data for testing and demonstration'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Delete existing data before creating new sample data'
        )
        parser.add_argument(
            '--clients',
            type=int,
            default=8,
            help='Number of clients to create (default: 8)'
        )
        parser.add_argument(
            '--licenses-per-client',
            type=int,
            default=2,
            help='Average number of licenses per client (default: 2)'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Creating Enhanced Sample Data'))
        self.stdout.write('=' * 50)
        
        # Clean existing data if requested
        if options['clean']:
            self.clean_existing_data()
        
        # Create or get admin user
        admin_user = self.create_admin_user()
        
        # Create trading configurations
        configurations = self.create_trading_configurations()
        
        # Create clients
        clients = self.create_clients(options['clients'], admin_user)
        
        # Create licenses
        licenses = self.create_licenses(clients, configurations, options['licenses_per_client'], admin_user)
        
        # Add usage data to some licenses
        self.add_usage_data(licenses)
        
        # Show summary
        self.show_summary()
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Sample data creation completed!'))
        self.stdout.write(self.style.SUCCESS('📱 Admin: http://localhost:8000/admin/ (admin/admin123)'))
        self.stdout.write(self.style.SUCCESS('🏠 Dashboard: http://localhost:8000/dashboard/'))
    
    def clean_existing_data(self):
        """Clean existing sample data"""
        self.stdout.write('🧹 Cleaning existing data...')
        
        # Delete in correct order (respecting foreign keys)
        License.objects.all().delete()
        Client.objects.all().delete()
        TradingConfiguration.objects.all().delete()
        
        self.stdout.write('   ✅ Existing data cleaned')
    
    def create_admin_user(self):
        """Create or update admin user"""
        self.stdout.write('👤 Creating admin user...')
        
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_superuser': True,
                'is_staff': True,
                'is_active': True,
                'first_name': 'Admin',
                'last_name': 'User'
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()
        
        if created:
            self.stdout.write('   ✅ Created admin user')
        else:
            self.stdout.write('   ✅ Updated admin user password')
        
        return admin_user
    
    def create_trading_configurations(self):
        """Create various trading configurations"""
        self.stdout.write('⚙️ Creating trading configurations...')
        
        config_data = [
            {
                'name': 'US30 Conservative',
                'description': 'Conservative US30 trading with tight risk management',
                'inp_AllowedSymbol': 'US30',
                'inp_StrictSymbolCheck': True,
                'inp_SessionStart': '09:00',
                'inp_SessionEnd': '16:00',
                'inp_FibLevel_1_05': 1.02,  # More conservative
                'inp_FibLevel_Neg_05': -0.02,
                'inp_PrimaryPendingTimeout': 15,
                'inp_PrimaryPositionTimeout': 45,
            },
            {
                'name': 'US30 Standard',
                'description': 'Standard US30 trading configuration',
                'inp_AllowedSymbol': 'US30',
                'inp_StrictSymbolCheck': True,
                'inp_SessionStart': '08:45',
                'inp_SessionEnd': '10:00',
                'inp_FibLevel_1_05': 1.05,
                'inp_FibLevel_Neg_05': -0.05,
                'inp_PrimaryPendingTimeout': 30,
                'inp_PrimaryPositionTimeout': 60,
            },
            {
                'name': 'US30 Aggressive',
                'description': 'Aggressive US30 trading with wider targets',
                'inp_AllowedSymbol': 'US30',
                'inp_StrictSymbolCheck': True,
                'inp_SessionStart': '08:30',
                'inp_SessionEnd': '10:30',
                'inp_FibLevel_1_05': 1.08,  # More aggressive
                'inp_FibLevel_Neg_05': -0.08,
                'inp_PrimaryPendingTimeout': 45,
                'inp_PrimaryPositionTimeout': 90,
            },
            {
                'name': 'EURUSD Scalping',
                'description': 'Fast scalping strategy for EURUSD',
                'inp_AllowedSymbol': 'EURUSD',
                'inp_StrictSymbolCheck': True,
                'inp_SessionStart': '07:00',
                'inp_SessionEnd': '18:00',
                'inp_FibLevel_1_05': 1.03,
                'inp_FibLevel_Neg_05': -0.03,
                'inp_PrimaryPendingTimeout': 10,
                'inp_PrimaryPositionTimeout': 30,
            },
            {
                'name': 'XAUUSD Gold Trading',
                'description': 'Specialized configuration for gold trading',
                'inp_AllowedSymbol': 'XAUUSD',
                'inp_StrictSymbolCheck': True,
                'inp_SessionStart': '06:00',
                'inp_SessionEnd': '17:00',
                'inp_FibLevel_1_05': 1.06,
                'inp_FibLevel_Neg_05': -0.06,
                'inp_PrimaryPendingTimeout': 60,
                'inp_PrimaryPositionTimeout': 120,
            }
        ]
        
        configurations = []
        for config_info in config_data:
            config, created = TradingConfiguration.objects.get_or_create(
                name=config_info['name'],
                defaults=config_info
            )
            configurations.append(config)
            
            if created:
                self.stdout.write(f'   ✅ Created configuration: {config.name}')
            else:
                self.stdout.write(f'   ℹ️  Configuration exists: {config.name}')
        
        return configurations
    
    def create_clients(self, num_clients, admin_user):
        """Create diverse clients from different countries"""
        self.stdout.write(f'👥 Creating {num_clients} clients...')
        
        # Sample client data with realistic names and countries
        client_templates = [
            {'first_name': 'John', 'last_name': 'Smith', 'country': 'United States', 'email': 'john.smith@email.com'},
            {'first_name': 'Maria', 'last_name': 'Garcia', 'country': 'Spain', 'email': 'maria.garcia@email.com'},
            {'first_name': 'Ahmed', 'last_name': 'Hassan', 'country': 'Egypt', 'email': 'ahmed.hassan@email.com'},
            {'first_name': 'Li', 'last_name': 'Chen', 'country': 'China', 'email': 'li.chen@email.com'},
            {'first_name': 'Hans', 'last_name': 'Mueller', 'country': 'Germany', 'email': 'hans.mueller@email.com'},
            {'first_name': 'Priya', 'last_name': 'Sharma', 'country': 'India', 'email': 'priya.sharma@email.com'},
            {'first_name': 'Jean', 'last_name': 'Dubois', 'country': 'France', 'email': 'jean.dubois@email.com'},
            {'first_name': 'Yuki', 'last_name': 'Tanaka', 'country': 'Japan', 'email': 'yuki.tanaka@email.com'},
            {'first_name': 'Carlos', 'last_name': 'Silva', 'country': 'Brazil', 'email': 'carlos.silva@email.com'},
            {'first_name': 'Emma', 'last_name': 'Wilson', 'country': 'United Kingdom', 'email': 'emma.wilson@email.com'},
            {'first_name': 'Mohammed', 'last_name': 'Al-Rashid', 'country': 'Saudi Arabia', 'email': 'mohammed.rashid@email.com'},
            {'first_name': 'Olga', 'last_name': 'Petrov', 'country': 'Russia', 'email': 'olga.petrov@email.com'},
        ]
        
        clients = []
        for i in range(num_clients):
            # Use templates cyclically, but add variation
            template = client_templates[i % len(client_templates)]
            
            # Add number suffix if we're cycling through templates
            if i >= len(client_templates):
                suffix = f" {i // len(client_templates) + 1}"
                first_name = template['first_name'] + suffix
                last_name = template['last_name']
                email = template['email'].replace('@', f'{i+1}@')
            else:
                first_name = template['first_name']
                last_name = template['last_name']
                email = template['email']
            
            client, created = Client.objects.get_or_create(
                first_name=first_name,
                last_name=last_name,
                country=template['country'],
                defaults={
                    'email': email,
                    'created_by': admin_user
                }
            )
            clients.append(client)
            
            if created:
                self.stdout.write(f'   ✅ Created client: {client.full_name} ({client.country})')
        
        return clients
    
    def create_licenses(self, clients, configurations, avg_licenses_per_client, admin_user):
        """Create licenses with various statuses and configurations"""
        self.stdout.write('🔑 Creating licenses...')
        
        licenses = []
        now = timezone.now()
        
        for client in clients:
            # Randomize number of licenses per client (1-3)
            num_licenses = random.randint(1, avg_licenses_per_client + 1)
            
            for i in range(num_licenses):
                # Randomize license characteristics
                trade_mode = random.choice([0, 1, 2])  # Demo, Restricted, Live
                
                # Create different expiration scenarios
                expiry_scenarios = [
                    now + timedelta(days=30),   # Expiring soon
                    now + timedelta(days=90),   # Short term
                    now + timedelta(days=180),  # Medium term
                    now + timedelta(days=365),  # Long term
                    now - timedelta(days=30),   # Recently expired
                    now - timedelta(days=90),   # Expired
                ]
                expires_at = random.choice(expiry_scenarios)
                
                # Some licenses should be inactive
                is_active = random.choice([True, True, True, False])  # 75% active
                
                # Select random configuration
                configuration = random.choice(configurations)
                
                license = License.objects.create(
                    client=client,
                    trading_configuration=configuration,
                    account_trade_mode=trade_mode,
                    expires_at=expires_at,
                    is_active=is_active,
                    created_by=admin_user
                )
                licenses.append(license)
                
                # Add some bound accounts (simulate usage)
                if random.choice([True, False]):  # 50% chance of being bound
                    system_hash = f"system_hash_{license.id}_{random.randint(1000, 9999)}"
                    account_hash = f"account_hash_{license.id}_{random.randint(1000, 9999)}"
                    broker_server = random.choice(['demo.broker.com', 'live.broker.com', 'eu.broker.com'])
                    
                    license.bind_account(
                        system_hash=system_hash,
                        account_trade_mode=trade_mode,
                        broker_server=broker_server,
                        account_hash=account_hash
                    )
                
                self.stdout.write(f'   ✅ Created license: {license.license_key[:8]}... for {client.full_name} ({license.status})')
        
        return licenses
    
    def add_usage_data(self, licenses):
        """Add realistic usage data to licenses"""
        self.stdout.write('📊 Adding usage data...')
        
        for license in licenses:
            if license.system_hash:  # Only for bound licenses
                # Add random usage count
                usage_count = random.randint(5, 100)
                daily_usage = random.randint(0, 20)
                
                # Simulate some historical usage
                days_ago = random.randint(1, 30)
                last_used = timezone.now() - timedelta(days=days_ago)
                
                license.usage_count = usage_count
                license.daily_usage_count = daily_usage
                license.last_used_at = last_used
                license.save()
                
                # Simulate account hash changes for some licenses
                if random.choice([True, False, False]):  # 33% chance
                    new_account_hash = f"new_account_hash_{license.id}_{random.randint(1000, 9999)}"
                    license.account_hash_history.append({
                        'account_hash': license.account_hash,
                        'timestamp': (timezone.now() - timedelta(days=5)).isoformat(),
                        'action': 'replaced'
                    })
                    license.account_hash = new_account_hash
                    license.account_hash_history.append({
                        'account_hash': new_account_hash,
                        'timestamp': timezone.now().isoformat(),
                        'action': 'updated'
                    })
                    license.save()
        
        self.stdout.write('   ✅ Usage data added')
    
    def show_summary(self):
        """Show summary of created data"""
        self.stdout.write('\n📈 Sample Data Summary:')
        self.stdout.write('=' * 30)
        
        # Count statistics
        total_clients = Client.objects.count()
        total_licenses = License.objects.count()
        total_configs = TradingConfiguration.objects.count()
        
        # License statistics
        active_licenses = License.objects.filter(is_active=True).count()
        expired_licenses = License.objects.filter(expires_at__lt=timezone.now()).count()
        bound_licenses = License.objects.exclude(system_hash__isnull=True).count()
        
        # Configuration usage
        config_usage = {}
        for config in TradingConfiguration.objects.all():
            config_usage[config.name] = config.licenses.count()
        
        # Trade mode distribution
        demo_count = License.objects.filter(account_trade_mode=0).count()
        restricted_count = License.objects.filter(account_trade_mode=1).count()
        live_count = License.objects.filter(account_trade_mode=2).count()
        
        self.stdout.write(f'👥 Clients: {total_clients}')
        self.stdout.write(f'🔑 Licenses: {total_licenses}')
        self.stdout.write(f'⚙️  Configurations: {total_configs}')
        self.stdout.write('')
        self.stdout.write(f'📊 License Status:')
        self.stdout.write(f'   Active: {active_licenses}')
        self.stdout.write(f'   Expired: {expired_licenses}')
        self.stdout.write(f'   Bound to accounts: {bound_licenses}')
        self.stdout.write('')
        self.stdout.write(f'🎯 Trade Modes:')
        self.stdout.write(f'   Demo: {demo_count}')
        self.stdout.write(f'   Restricted: {restricted_count}')
        self.stdout.write(f'   Live: {live_count}')
        self.stdout.write('')
        self.stdout.write(f'⚙️  Configuration Usage:')
        for config_name, count in config_usage.items():
            self.stdout.write(f'   {config_name}: {count} licenses')