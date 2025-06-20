#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_admin.settings')
django.setup()

from licenses.models import Client, License
from configurations.models import TradingConfiguration

def explore_database():
    print("🗄️  DATABASE EXPLORATION")
    print("=" * 50)
    
    # Clients
    print(f"\n👥 CLIENTS ({Client.objects.count()})")
    for client in Client.objects.all():
        license_count = client.licenses.count()
        print(f"  • {client.full_name} ({client.country}) - {license_count} licenses")
    
    # Licenses
    print(f"\n🔑 LICENSES ({License.objects.count()})")
    for license in License.objects.all():
        status_emoji = "✅" if license.status == "Active" else "❌" if license.status == "Expired" else "⏳"
        account_info = license.account_id or "Not used"
        print(f"  • {license.license_key[:12]}... | {license.client.full_name} | {status_emoji} {license.status} | Account: {account_info}")
    
    # Unused licenses
    unused = License.objects.filter(account_id__isnull=True)
    print(f"\n🆕 UNUSED LICENSES ({unused.count()})")
    for license in unused:
        print(f"  • {license.license_key[:12]}... | {license.client.full_name}")

if __name__ == "__main__":
    explore_database()