from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Create admin user for production deployment'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            default='admin',
            help='Admin username (default: admin)'
        )
        parser.add_argument(
            '--email',
            default='admin@example.com',
            help='Admin email (default: admin@example.com)'
        )
        parser.add_argument(
            '--password',
            help='Admin password (if not provided, will use default)'
        )
    
    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password'] or 'admin123'
        
        # Check if admin user already exists
        if User.objects.filter(username=username).exists():
            existing_user = User.objects.get(username=username)
            self.stdout.write(
                self.style.WARNING(f'Admin user "{username}" already exists')
            )
            self.stdout.write(f'Email: {existing_user.email}')
            self.stdout.write(f'Last login: {existing_user.last_login or "Never"}')
            return
        
        # Create admin user
        try:
            admin_user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Admin',
                last_name='User'
            )
            
            self.stdout.write(
                self.style.SUCCESS('✅ Admin user created successfully!')
            )
            self.stdout.write('=' * 40)
            self.stdout.write(f'Username: {username}')
            self.stdout.write(f'Password: {password}')
            self.stdout.write(f'Email: {email}')
            self.stdout.write('=' * 40)
            self.stdout.write(f'🌐 Admin URL: https://your-app.onrender.com/admin/')
            self.stdout.write(f'🏠 Dashboard: https://your-app.onrender.com/dashboard/')
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING('⚠️  IMPORTANT: Change the password after first login!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating admin user: {e}')
            )
