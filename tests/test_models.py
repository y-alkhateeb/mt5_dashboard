from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from licenses.models import License
from configurations.models import TradingConfiguration

class LicenseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        
    def test_license_creation(self):
        license = License.objects.create(
            account_id='TEST001',
            account_hash='test_hash',
            account_trade_mode=0,
            broker_server='test.broker.com',
            expires_at=timezone.now() + timedelta(days=365),
            created_by=self.user
        )
        
        self.assertTrue(license.license_key)
        self.assertEqual(license.account_id, 'TEST001')
        self.assertEqual(license.status, 'Active')
        
    def test_license_expiration(self):
        license = License.objects.create(
            account_id='TEST002',
            account_hash='test_hash',
            account_trade_mode=0,
            broker_server='test.broker.com',
            expires_at=timezone.now() - timedelta(days=1),
            created_by=self.user
        )
        
        self.assertTrue(license.is_expired)
        self.assertEqual(license.status, 'Expired')