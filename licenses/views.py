from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import License, Client
from .serializers import (
    LicenseSerializer, 
    ClientSerializer,
    BotValidationRequestSerializer, 
    BotValidationResponseSerializer
)
from configurations.models import TradingConfiguration
from configurations.serializers import TradingConfigurationSerializer
import logging

logger = logging.getLogger(__name__)

# ✅ FIXED: Added rate limiting for bot validation
class BotValidationThrottle(AnonRateThrottle):
    scope = 'bot_validation'

class BotValidationAPIView(APIView):
    """🤖 API for trading bot license validation with rate limiting"""
    permission_classes = [AllowAny]
    throttle_classes = [BotValidationThrottle]  # ✅ FIXED: Added rate limiting
    
    def post(self, request):
        """Validate trading bot license and return configuration"""
        serializer = BotValidationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Invalid request data',
                    'details': serializer.errors
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        license_key = serializer.validated_data['license_key']
        system_hash = serializer.validated_data['system_hash']
        account_trade_mode = serializer.validated_data['account_trade_mode']
        broker_server = serializer.validated_data.get('broker_server', '')
        account_hash = serializer.validated_data.get('account_hash', '')
        
        try:
            # Find license
            try:
                license_obj = License.objects.select_related('trading_configuration').get(
                    license_key=license_key
                )
            except License.DoesNotExist:
                logger.warning(f"License not found: {license_key[:8]}...")
                return Response({
                    'success': False,
                    'error': {
                        'code': 'INVALID_LICENSE',
                        'message': 'Invalid license key'
                    }
                })
            
            # Check if license is valid
            if not license_obj.is_valid:
                if license_obj.is_expired:
                    error_code = 'LICENSE_EXPIRED'
                    error_message = 'License has expired'
                elif not license_obj.is_active:
                    error_code = 'LICENSE_INACTIVE'
                    error_message = 'License is inactive'
                else:
                    error_code = 'NO_CONFIGURATION'
                    error_message = 'No trading configuration assigned to this license'
                
                logger.warning(f"License validation failed for {license_key[:8]}...: {error_message}")
                return Response({
                    'success': False,
                    'error': {
                        'code': error_code,
                        'message': error_message
                    }
                })
            
            # Validate system hash
            system_valid, system_message = license_obj.validate_system_hash(system_hash)
            if not system_valid:
                logger.warning(f"System hash validation failed for {license_key[:8]}...: {system_message}")
                return Response({
                    'success': False,
                    'error': {
                        'code': 'SYSTEM_MISMATCH',
                        'message': system_message
                    }
                })
            
            # Check account trade mode compatibility
            if license_obj.system_hash and license_obj.account_trade_mode != account_trade_mode:
                logger.warning(f"Account trade mode mismatch for {license_key[:8]}...")
                return Response({
                    'success': False,
                    'error': {
                        'code': 'TRADE_MODE_MISMATCH',
                        'message': f'Account trade mode mismatch. Expected {license_obj.account_trade_mode}, got {account_trade_mode}'
                    }
                })
            
            # Bind account (internal tracking)
            license_obj.bind_account(
                system_hash=system_hash,
                account_trade_mode=account_trade_mode,
                broker_server=broker_server,
                account_hash=account_hash if account_hash else None
            )
            
            # ✅ FIXED: Consistent configuration retrieval
            if not license_obj.trading_configuration:
                logger.error(f"No trading configuration assigned to license {license_key[:8]}...")
                return Response({
                    'success': False,
                    'error': {
                        'code': 'NO_CONFIGURATION',
                        'message': 'No trading configuration assigned to this license'
                    }
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Serialize configuration
            config_serializer = TradingConfigurationSerializer(license_obj.trading_configuration)
            
            # Return success response
            response_data = {
                'success': True,
                'message': 'License validated successfully',
                'configuration': config_serializer.data,
                'expires_at': license_obj.expires_at,
                'license_info': {
                    'usage_count': license_obj.usage_count,
                    'daily_usage': license_obj.daily_usage_count,
                    'first_time_use': license_obj.first_used_at is None,
                    'account_login_changed': license_obj.account_hash_changes_count > 1
                }
            }
            
            logger.info(f"License validation successful for {license_key[:8]}...")
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"License validation error for {license_key[:8]}...: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': 'Internal server error during license validation'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LicenseViewSet(viewsets.ModelViewSet):
    """Admin ViewSet for License management"""
    queryset = License.objects.select_related('client', 'trading_configuration').all()
    serializer_class = LicenseSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
    def perform_create(self, serializer):
        license_instance = serializer.save(created_by=self.request.user)
        # Note: Configuration should be assigned manually or via signal
    
    @action(detail=True, methods=['get', 'put', 'patch'])
    def configuration(self, request, pk=None):
        """Get or update license configuration"""
        license_instance = self.get_object()
        
        if request.method == 'GET':
            if not license_instance.trading_configuration:
                return Response({
                    'error': 'No configuration assigned to this license'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = TradingConfigurationSerializer(license_instance.trading_configuration)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            if not license_instance.trading_configuration:
                return Response({
                    'error': 'No configuration assigned to this license. Assign a configuration first.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            partial = request.method == 'PATCH'
            serializer = TradingConfigurationSerializer(
                license_instance.trading_configuration, 
                data=request.data, 
                partial=partial
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def assign_configuration(self, request, pk=None):
        """Assign a trading configuration to a license"""
        license_instance = self.get_object()
        config_id = request.data.get('configuration_id')
        
        if not config_id:
            return Response({
                'error': 'configuration_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            config = TradingConfiguration.objects.get(id=config_id, is_active=True)
            license_instance.trading_configuration = config
            license_instance.save()
            
            return Response({
                'message': f'Configuration "{config.name}" assigned successfully',
                'configuration': TradingConfigurationSerializer(config).data
            })
        except TradingConfiguration.DoesNotExist:
            return Response({
                'error': 'Configuration not found or inactive'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active licenses"""
        active_licenses = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active_licenses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Get all expired licenses"""
        expired_licenses = self.queryset.filter(expires_at__lt=timezone.now())
        serializer = self.get_serializer(expired_licenses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get licenses expiring within 30 days"""
        thirty_days_from_now = timezone.now() + timezone.timedelta(days=30)
        expiring_licenses = self.queryset.filter(
            expires_at__lt=thirty_days_from_now,
            expires_at__gt=timezone.now(),
            is_active=True
        )
        serializer = self.get_serializer(expiring_licenses, many=True)
        return Response(serializer.data)

class ClientViewSet(viewsets.ModelViewSet):
    """Admin ViewSet for Client management"""
    queryset = Client.objects.prefetch_related('licenses').all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)