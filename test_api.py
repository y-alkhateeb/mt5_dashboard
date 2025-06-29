#!/usr/bin/env python
"""
API Testing Script for Trading Robot Admin
Run this to test your deployed API endpoints
"""

import requests
import json
import sys
from datetime import datetime

def test_api_endpoints(base_url):
    """Test all API endpoints"""
    print(f"🧪 Testing API endpoints at: {base_url}")
    print("=" * 50)
    
    # Remove trailing slash
    base_url = base_url.rstrip('/')
    
    endpoints = [
        {
            'name': 'Health Check',
            'url': f'{base_url}/api/health/',
            'method': 'GET',
            'auth_required': True
        },
        {
            'name': 'API Documentation', 
            'url': f'{base_url}/api/docs/',
            'method': 'GET',
            'auth_required': True
        },
        {
            'name': 'Bot Validation (Sample)',
            'url': f'{base_url}/api/validate/',
            'method': 'POST',
            'auth_required': False,
            'data': {
                'license_key': 'test-license-key-123456789012',
                'system_hash': 'test-system-hash',
                'account_trade_mode': 0,
                'broker_server': 'demo.broker.com',
                'timestamp': datetime.now().isoformat()
            }
        }
    ]
    
    results = []
    
    for endpoint in endpoints:
        print(f"Testing: {endpoint['name']}")
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], timeout=30)
            else:
                response = requests.post(
                    endpoint['url'], 
                    json=endpoint.get('data', {}),
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
            
            status = "✅ PASS" if response.status_code < 500 else "❌ FAIL"
            print(f"   Status: {response.status_code} - {status}")
            
            if response.status_code < 500:
                try:
                    response_data = response.json()
                    if 'success' in response_data:
                        print(f"   Success: {response_data['success']}")
                    if 'message' in response_data:
                        print(f"   Message: {response_data['message']}")
                except:
                    print(f"   Response length: {len(response.text)} chars")
            else:
                print(f"   Error: {response.text[:100]}...")
            
            results.append({
                'endpoint': endpoint['name'],
                'status_code': response.status_code,
                'success': response.status_code < 500
            })
            
        except requests.RequestException as e:
            print(f"   ❌ ERROR: {str(e)}")
            results.append({
                'endpoint': endpoint['name'],
                'status_code': 0,
                'success': False,
                'error': str(e)
            })
        
        print()
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print("📊 SUMMARY")
    print("=" * 20)
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    
    if successful == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed - check deployment")
    
    return results

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_api.py <base_url>")
        print("Example: python test_api.py https://your-app.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1]
    test_api_endpoints(base_url)

if __name__ == "__main__":
    main()
