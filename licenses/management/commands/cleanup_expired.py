from django.core.management.base import BaseCommand
from django.utils import timezone
from licenses.models import License

class Command(BaseCommand):
    help = 'Cleanup expired licenses and mark them as inactive'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days after expiration to keep licenses (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
    
    def handle(self, *args, **options):
        days_threshold = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timezone.timedelta(days=days_threshold)
        expired_licenses = License.objects.filter(
            expires_at__lt=cutoff_date,
            is_active=True
        )
        
        count = expired_licenses.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would deactivate {count} expired licenses')
            )
            for license in expired_licenses[:10]:  # Show first 10
                self.stdout.write(f'  - {license.license_key} (expired: {license.expires_at})')
            if count > 10:
                self.stdout.write(f'  ... and {count - 10} more')
        else:
            expired_licenses.update(is_active=False)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deactivated {count} expired licenses')
            )
