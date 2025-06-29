from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.utils import timezone  # ← ADDED: Missing import

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_documentation(request):
    """API Documentation endpoint providing information about available endpoints"""
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
            'validation': {
                'validate': 'POST /api/validate/',
            }
        },
        'authentication': 'Session or Basic Authentication required',
        'pagination': 'Page-based pagination (20 items per page)',
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
            'timestamp': timezone.now().isoformat()  # ← FIXED: Now works
        })
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()  # ← FIXED: Now works
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)