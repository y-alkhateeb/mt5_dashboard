from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
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

class BotValidationAPIView(APIView):
    """🤖 Simple API for trading bot license validation"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Validate trading bot license and return configuration"""
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
                logger.warning(f"License not found: {license_key[:8]}...")
                return Response({
                    'success': False,
                    'message': 'Invalid license key'
                })
            
            # Check if license is valid
            if not license_obj.is_valid:
                reason = "expired" if license_obj.is_expired else "inactive"
                logger.warning(f"License validation failed for {license_key[:8]}...: {reason}")
                return Response({
                    'success': False,
                    'message': f'License is {reason}'
                })
            
            # Validate system hash
            system_valid, system_message = license_obj.validate_system_hash(system_hash)
            if not system_valid:
                logger.warning(f"System hash validation failed for {license_key[:8]}...: {system_message}")
                return Response({
                    'success': False,
                    'message': system_message
                })
            
            # Check account trade mode compatibility
            if license_obj.system_hash and license_obj.account_trade_mode != account_trade_mode:
                logger.warning(f"Account trade mode mismatch for {license_key[:8]}...")
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
            
            logger.info(f"License validation successful for {license_key[:8]}...")
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"License validation error for {license_key[:8]}...: {str(e)}")
            return Response({
                'success': False,
                'message': 'Internal server error during license validation'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LicenseViewSet(viewsets.ModelViewSet):
    """Admin ViewSet for License management"""
    queryset = License.objects.all()
    serializer_class = LicenseSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        license_instance = serializer.save(created_by=self.request.user)
        # Configuration is created automatically by signal
    
    @action(detail=True, methods=['get', 'put', 'patch'])
    def configuration(self, request, pk=None):
        """Get or update license configuration"""
        license_instance = self.get_object()
        config, created = TradingConfiguration.objects.get_or_create(license=license_instance)
        
        if request.method == 'GET':
            serializer = TradingConfigurationSerializer(config)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = TradingConfigurationSerializer(
                config, data=request.data, partial=partial
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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

class ClientViewSet(viewsets.ModelViewSet):
    """Admin ViewSet for Client management"""
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)