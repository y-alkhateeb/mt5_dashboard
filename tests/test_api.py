from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from licenses.models import License

class LicenseAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
    def test_create_license(self):
        data = {
            'account_id': 'API001',
            'account_hash': 'api_test_hash',
            'account_trade_mode': 0,
            'broker_server': 'api.broker.com',
            'expires_at': '2025-12-31T23:59:59Z',
            'is_active': True
        }
        
        response = self.client.post('/api/licenses/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(License.objects.count(), 1)
        
    def test_list_licenses(self):
        License.objects.create(
            account_id='LIST001',
            account_hash='list_hash',
            account_trade_mode=0,
            broker_server='list.broker.com',
            created_by=self.user
        )
        
        response = self.client.get('/api/licenses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)