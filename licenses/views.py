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

class BotValidationThrottle(AnonRateThrottle):
    scope = 'bot_validation'

class BotValidationAPIView(APIView):
    """🤖 API for trading bot license validation with enhanced error handling"""
    permission_classes = [AllowAny]
    throttle_classes = [BotValidationThrottle]
    
    def get_friendly_validation_message(self, serializer_errors):
        """Convert serializer errors to user-friendly messages"""
        field_messages = {
            'license_key': 'You should enter a license key',
            'system_hash': 'System hash is required',
            'account_trade_mode': 'Account trade mode is required',
            'broker_server': 'Broker server information is required',
            'timestamp': 'Timestamp is required',
            'account_hash': 'Account hash is required'
        }
        
        # Get the first error field and return appropriate message
        for field, errors in serializer_errors.items():
            if field in field_messages:
                return field_messages[field]
        
        # Fallback message
        return "Some required data is missing"
    
    def post(self, request):
        """Validate trading bot license and return configuration"""
        try:
            serializer = BotValidationRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'code': 'INVALID_REQUEST',
                    'message': self.get_friendly_validation_message(serializer.errors)
                }, status=status.HTTP_400_BAD_REQUEST)
            
            license_key = serializer.validated_data['license_key']
            system_hash = serializer.validated_data['system_hash']
            account_trade_mode = serializer.validated_data['account_trade_mode']
            broker_server = serializer.validated_data.get('broker_server', '')
            account_hash = serializer.validated_data.get('account_hash', '')
            
            # Find license
            try:
                license_obj = License.objects.select_related('trading_configuration').get(
                    license_key=license_key
                )
            except License.DoesNotExist:
                logger.warning(f"License not found: {license_key[:8]}...")
                return Response({
                    'success': False,
                    'code': 'INVALID_LICENSE',
                    'message': 'Invalid license key'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
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
                    'code': error_code,
                    'message': error_message
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Validate system hash
            system_valid, system_message = license_obj.validate_system_hash(system_hash)
            if not system_valid:
                logger.warning(f"System hash validation failed for {license_key[:8]}...: {system_message}")
                return Response({
                    'success': False,
                    'code': 'SYSTEM_MISMATCH',
                    'message': system_message
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Check account trade mode compatibility
            if license_obj.system_hash and license_obj.account_trade_mode != account_trade_mode:
                logger.warning(f"Account trade mode mismatch for {license_key[:8]}...")
                return Response({
                    'success': False,
                    'code': 'TRADE_MODE_MISMATCH',
                    'message': f'Account trade mode mismatch. Expected {license_obj.account_trade_mode}, got {account_trade_mode}'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Bind account (internal tracking)
            license_obj.bind_account(
                system_hash=system_hash,
                account_trade_mode=account_trade_mode,
                broker_server=broker_server,
                account_hash=account_hash if account_hash else None
            )
            
            # Get configuration
            if not license_obj.trading_configuration:
                logger.error(f"No trading configuration assigned to license {license_key[:8]}...")
                return Response({
                    'success': False,
                    'code': 'NO_CONFIGURATION',
                    'message': 'No trading configuration assigned to this license'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Serialize configuration and flatten into response
            config_serializer = TradingConfigurationSerializer(license_obj.trading_configuration)
            config_data = config_serializer.data
            
            # Build flattened response with configuration fields at root level
            response_data = {
                'success': True,
                'message': 'License validated successfully',
                'expires_at': license_obj.expires_at,
            }
            
            # Add all configuration fields to root level
            response_data.update(config_data)
            
            logger.info(f"License validation successful for {license_key[:8]}...")
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"License validation error: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error during license validation'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LicenseViewSet(viewsets.ModelViewSet):
    """Admin ViewSet for License management"""
    queryset = License.objects.select_related('client', 'trading_configuration').all()
    serializer_class = LicenseSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
    def perform_create(self, serializer):
        license_instance = serializer.save(created_by=self.request.user)
    
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
        page = self.paginate_queryset(active_licenses)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(active_licenses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Get all expired licenses"""
        expired_licenses = self.queryset.filter(expires_at__lt=timezone.now())
        page = self.paginate_queryset(expired_licenses)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
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
        page = self.paginate_queryset(expiring_licenses)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
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