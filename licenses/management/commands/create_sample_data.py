from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from licenses.models import Client, License
from configurations.models import TradingConfiguration
from datetime import timedelta

class Command(BaseCommand):
    help = 'Create sample data for testing'
    
    def handle(self, *args, **options):
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_superuser': True,
                'is_staff': True,
                'is_active': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()
        
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Created admin user'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Updated admin user password'))
        
        # Sample clients data
        clients_data = [
            {'first_name': 'John', 'last_name': 'Smith', 'country': 'United States', 'email': 'john@example.com'},
            {'first_name': 'Maria', 'last_name': 'Garcia', 'country': 'Spain', 'email': 'maria@example.com'},
            {'first_name': 'Ahmed', 'last_name': 'Hassan', 'country': 'Egypt', 'email': 'ahmed@example.com'},
            {'first_name': 'Li', 'last_name': 'Chen', 'country': 'China', 'email': 'li@example.com'},
            {'first_name': 'Hans', 'last_name': 'Mueller', 'country': 'Germany', 'email': 'hans@example.com'},
        ]
        
        for i, client_data in enumerate(clients_data):
            # Create or get client
            client, client_created = Client.objects.get_or_create(
                first_name=client_data['first_name'],
                last_name=client_data['last_name'],
                country=client_data['country'],
                defaults={
                    'email': client_data['email'],
                    'created_by': admin_user
                }
            )
            
            if client_created:
                self.stdout.write(f'✅ Created client: {client.full_name}')
            
            # Create license for client if it doesn't exist
            if not client.licenses.exists():
                license_obj = License.objects.create(
                    client=client,
                    account_trade_mode=i % 3,  # Mix of demo, restricted, live
                    expires_at=timezone.now() + timedelta(days=365),
                    is_active=True,
                    created_by=admin_user
                )
                
                # ✅ REMOVED: Manual configuration creation - signal handles this!
                # Configuration is created automatically by the signal
                
                self.stdout.write(f'✅ Created license {license_obj.license_key[:8]}... for {client.full_name}')
            else:
                self.stdout.write(f'ℹ️  License already exists for {client.full_name}')
        
        # Show summary
        total_clients = Client.objects.count()
        total_licenses = License.objects.count() 
        total_configs = TradingConfiguration.objects.count()
        
        self.stdout.write(self.style.SUCCESS(f'\n📊 Summary:'))
        self.stdout.write(f'   Clients: {total_clients}')
        self.stdout.write(f'   Licenses: {total_licenses}')
        self.stdout.write(f'   Configurations: {total_configs}')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Setup complete!'))
        self.stdout.write(self.style.SUCCESS('Admin: http://localhost:8000/admin/ (admin/admin123)'))
        self.stdout.write(self.style.SUCCESS('API: POST http://localhost:8000/api/licenses/validate/'))