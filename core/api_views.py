from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_documentation(request):
    """
    API Documentation endpoint providing information about available endpoints
    """
    documentation = {
        'api_version': '1.0',
        'endpoints': {
            'licenses': {
                'list': 'GET /api/licenses/',
                'create': 'POST /api/licenses/',
                'detail': 'GET /api/licenses/{id}/',
                'update': 'PUT /api/licenses/{id}/',
                'partial_update': 'PATCH /api/licenses/{id}/',
                'delete': 'DELETE /api/licenses/{id}/',
                'configuration': 'GET/PUT/PATCH /api/licenses/{id}/configuration/',
                'active': 'GET /api/licenses/active/',
                'expired': 'GET /api/licenses/expired/',
            },
            'filters': {
                'account_id': 'Filter by account ID (contains)',
                'broker_server': 'Filter by broker server (contains)', 
                'is_active': 'Filter by active status (true/false)',
                'account_trade_mode': 'Filter by trade mode (0=demo, 1=restricted, 2=live)',
                'expires_at_after': 'Filter by expiration date (after)',
                'expires_at_before': 'Filter by expiration date (before)',
            }
        },
        'authentication': 'Session or Basic Authentication required',
        'pagination': 'Page-based pagination (20 items per page)',
        'example_requests': {
            'create_license': {
                'url': '/api/licenses/',
                'method': 'POST',
                'data': {
                    'account_id': 'DEMO001',
                    'account_hash': 'secure_hash_here',
                    'account_trade_mode': 0,
                    'broker_server': 'demo.broker.com',
                    'expires_at': '2025-12-31T23:59:59Z',
                    'is_active': True
                }
            },
            'update_configuration': {
                'url': '/api/licenses/1/configuration/',
                'method': 'PATCH',
                'data': {
                    'allowed_symbol': 'EURUSD',
                    'inp_session_start': '09:00',
                    'inp_session_end': '17:00'
                }
            }
        }
    }
    
    return Response(documentation)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def health_check(request):
    """Health check endpoint for monitoring"""
    from django.db import connection
    from licenses.models import License
    
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Test model access
        license_count = License.objects.count()
        
        return Response({
            'status': 'healthy',
            'database': 'connected',
            'total_licenses': license_count,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)