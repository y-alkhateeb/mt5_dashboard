# File: licenses/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import License
from .serializers import BotValidationRequestSerializer
from configurations.models import TradingConfiguration
from configurations.serializers import TradingConfigurationSerializer
import logging

logger = logging.getLogger(__name__)

class BotValidationAPIView(APIView):
    """
    🤖 Simple API for trading bot license validation
    Only provides what's needed - nothing more!
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Validate trading bot license and return configuration
        
        POST /api/validate/
        {
            "license_key": "abc123...",
            "system_hash": "primary_account_identifier",
            "account_trade_mode": 0,
            "broker_server": "demo.broker.com",
            "timestamp": "2025-06-20T10:30:00Z",
            "account_hash": "hashed_account_login_id"  // optional
        }
        """
        serializer = BotValidationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        license_key = serializer.validated_data['license_key']
        system_hash = serializer.validated_data['system_hash']
        account_trade_mode = serializer.validated_data['account_trade_mode']
        broker_server = serializer.validated_data.get('broker_server', '')
        account_hash = serializer.validated_data.get('account_hash', '')
        
        try:
            # Find license
            try:
                license_obj = License.objects.get(license_key=license_key)
            except License.DoesNotExist:
                logger.warning(f"License not found: {license_key}")
                return Response({
                    'success': False,
                    'message': 'Invalid license key'
                })
            
            # Check if license is valid
            if not license_obj.is_valid:
                reason = "expired" if license_obj.is_expired else "inactive"
                logger.warning(f"License validation failed for {license_key}: {reason}")
                return Response({
                    'success': False,
                    'message': f'License is {reason}'
                })
            
            # Validate system hash
            system_valid, system_message = license_obj.validate_system_hash(system_hash)
            if not system_valid:
                logger.warning(f"System hash validation failed for {license_key}: {system_message}")
                return Response({
                    'success': False,
                    'message': system_message
                })
            
            # Check account trade mode compatibility
            if license_obj.system_hash and license_obj.account_trade_mode != account_trade_mode:
                logger.warning(f"Account trade mode mismatch for {license_key}")
                return Response({
                    'success': False,
                    'message': f'Account trade mode mismatch. Expected {license_obj.account_trade_mode}, got {account_trade_mode}'
                })
            
            # Bind account (internal tracking)
            license_obj.bind_account(
                system_hash=system_hash,
                account_trade_mode=account_trade_mode,
                broker_server=broker_server,
                account_hash=account_hash if account_hash else None
            )
            
            # Get configuration
            config, created = TradingConfiguration.objects.get_or_create(license=license_obj)
            config_serializer = TradingConfigurationSerializer(config)
            
            # Return clean response
            response_data = {
                'success': True,
                'message': 'License validated successfully',
                'configuration': config_serializer.data,
                'expires_at': license_obj.expires_at
            }
            
            logger.info(f"License validation successful for {license_key}")
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"License validation error for {license_key}: {str(e)}")
            return Response({
                'success': False,
                'message': 'Internal server error during license validation'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class APIInfoView(APIView):
    """
    📖 API Information
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'api_name': 'Trading Robot License Validation API',
            'version': '2.0',
            'available_endpoints': {
                'validate': {
                    'url': '/api/validate/',
                    'method': 'POST',
                    'description': 'Validate trading bot license and get configuration'
                },
                'info': {
                    'url': '/api/info/',
                    'method': 'GET',
                    'description': 'API information'
                }
            },
            'admin_panel': '/admin/',
            'notes': [
                'All license management is done through Django Admin',
                'Only validation functionality is provided via API',
                'No sensitive information is returned'
            ]
        })