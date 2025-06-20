from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Q
from licenses.models import License
import json

class Command(BaseCommand):
    help = 'Generate license usage report'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['json', 'csv', 'text'],
            default='text',
            help='Output format (default: text)'
        )
        parser.add_argument(
            '--output',
            help='Output file path (optional)'
        )
    
    def handle(self, *args, **options):
        now = timezone.now()
        
        # Generate statistics
        stats = {
            'total_licenses': License.objects.count(),
            'active_licenses': License.objects.filter(is_active=True).count(),
            'expired_licenses': License.objects.filter(expires_at__lt=now).count(),
            'demo_accounts': License.objects.filter(account_trade_mode=0).count(),
            'restricted_accounts': License.objects.filter(account_trade_mode=1).count(),
            'live_accounts': License.objects.filter(account_trade_mode=2).count(),
            'licenses_expiring_soon': License.objects.filter(
                expires_at__gt=now,
                expires_at__lt=now + timezone.timedelta(days=30),
                is_active=True
            ).count(),
            'generation_time': now.isoformat(),
        }
        
        # Format output
        if options['format'] == 'json':
            output = json.dumps(stats, indent=2)
        elif options['format'] == 'csv':
            output = 'Metric,Value\n'
            for key, value in stats.items():
                output += f'{key},{value}\n'
        else:  # text format
            output = f"""
Trading Robot License Report
Generated: {stats['generation_time']}

📊 OVERVIEW
Total Licenses: {stats['total_licenses']}
Active Licenses: {stats['active_licenses']}
Expired Licenses: {stats['expired_licenses']}
Expiring Soon (30 days): {stats['licenses_expiring_soon']}

🎯 ACCOUNT TYPES
Demo Accounts: {stats['demo_accounts']}
Restricted Accounts: {stats['restricted_accounts']}
Live Accounts: {stats['live_accounts']}

⚠️  ALERTS
{stats['expired_licenses']} licenses have expired
{stats['licenses_expiring_soon']} licenses expire in the next 30 days
"""
        
        # Output to file or stdout
        if options['output']:
            with open(options['output'], 'w') as f:
                f.write(output)
            self.stdout.write(
                self.style.SUCCESS(f'Report saved to {options["output"]}')
            )
        else:
            self.stdout.write(output)
