from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Client, License
from .serializers import (
    ClientSerializer, LicenseSerializer, 
    BotValidationRequestSerializer, BotValidationResponseSerializer
)
from configurations.models import TradingConfiguration
from configurations.serializers import TradingConfigurationSerializer
import logging

logger = logging.getLogger(__name__)

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class LicenseViewSet(viewsets.ModelViewSet):
    queryset = License.objects.all()
    serializer_class = LicenseSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def bot_validate(self, request):
        """
        Main endpoint for trading bot validation with system hash as primary identifier
        
        POST /api/licenses/bot_validate/
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
        timestamp = serializer.validated_data['timestamp']
        account_hash = serializer.validated_data.get('account_hash', '')
        
        try:
            # Step 1: Find license by license_key
            try:
                license_obj = License.objects.get(license_key=license_key)
            except License.DoesNotExist:
                logger.warning(f"License not found: {license_key}")
                return Response({
                    'success': False,
                    'message': 'Invalid license key',
                    'license_key': license_key
                })
            
            # Step 2: Check if license is valid (active and not expired)
            if not license_obj.is_valid:
                reason = "expired" if license_obj.is_expired else "inactive"
                logger.warning(f"License validation failed for {license_key}: {reason}")
                return Response({
                    'success': False,
                    'message': f'License is {reason}',
                    'license_key': license_key,
                    'client_name': license_obj.client.full_name,
                    'expires_at': license_obj.expires_at
                })
            
            # Step 3: PRIMARY VALIDATION - System Hash (Most Important)
            system_valid, system_message = license_obj.validate_system_hash(system_hash)
            
            if not system_valid:
                logger.warning(f"System hash validation failed for {license_key}: {system_message}")
                return Response({
                    'success': False,
                    'message': system_message,
                    'license_key': license_key,
                    'client_name': license_obj.client.full_name
                })
            
            # Step 4: Check account trade mode compatibility
            if license_obj.system_hash and license_obj.account_trade_mode != account_trade_mode:
                logger.warning(f"Account trade mode mismatch for {license_key}: expected {license_obj.account_trade_mode}, got {account_trade_mode}")
                return Response({
                    'success': False,
                    'message': f'Account trade mode mismatch. License is configured for mode {license_obj.account_trade_mode}, but bot requested mode {account_trade_mode}',
                    'license_key': license_key,
                    'client_name': license_obj.client.full_name
                })
            
            # Step 5: Bind account and track account hash changes
            first_time_use = not license_obj.is_account_bound
            old_account_hash = license_obj.account_hash
            
            license_obj.bind_account(
                system_hash=system_hash,
                account_trade_mode=account_trade_mode,
                broker_server=broker_server,
                account_hash=account_hash if account_hash else None
            )
            
            # Check if account login changed
            account_login_changed = (
                not first_time_use and 
                account_hash and 
                old_account_hash and 
                old_account_hash != account_hash
            )
            
            # Step 6: Get or create configuration
            config, created = TradingConfiguration.objects.get_or_create(license=license_obj)
            config_serializer = TradingConfigurationSerializer(config)
            
            # Step 7: Prepare successful response
            response_data = {
                'success': True,
                'message': 'License validated and account authorized successfully',
                'license_key': license_obj.license_key,
                'client_name': license_obj.client.full_name,
                'configuration': config_serializer.data,
                'expires_at': license_obj.expires_at,
                'account_trade_mode': license_obj.account_trade_mode,
                'first_time_use': first_time_use,
                'account_login_changed': account_login_changed,
                'usage_count': license_obj.usage_count,
                'last_used_at': license_obj.last_used_at
            }
            
            if account_login_changed:
                logger.info(f"Account login changed for {license_key}: {old_account_hash[:8]}... -> {account_hash[:8]}...")
            
            logger.info(f"License validation successful for {license_key} (client: {license_obj.client.full_name}, first_time: {first_time_use})")
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"License validation error for {license_key}: {str(e)}")
            return Response({
                'success': False,
                'message': 'Internal server error during license validation'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get', 'put', 'patch'])
    def configuration(self, request, pk=None):
        """Get or update trading configuration for a license"""
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
        active_licenses = self.queryset.filter(is_active=True, expires_at__gt=timezone.now())
        serializer = self.get_serializer(active_licenses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Get all expired licenses"""
        expired_licenses = self.queryset.filter(expires_at__lt=timezone.now())
        serializer = self.get_serializer(expired_licenses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unbound(self, request):
        """Get all unbound licenses (not bound to any account yet)"""
        unbound_licenses = self.queryset.filter(system_hash__isnull=True, is_active=True)
        serializer = self.get_serializer(unbound_licenses, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def account_hash_history(self, request, pk=None):
        """Get account hash change history for a license"""
        license_instance = self.get_object()
        return Response({
            'license_key': license_instance.license_key,
            'client_name': license_instance.client.full_name,
            'current_account_hash': license_instance.account_hash[:8] + '...' if license_instance.account_hash else None,
            'changes_count': license_instance.account_hash_changes_count,
            'history': license_instance.get_account_hash_history()
        })
