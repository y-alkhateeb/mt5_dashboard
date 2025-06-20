# licenses/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import License
from .serializers import LicenseSerializer
from configurations.models import TradingConfiguration
from configurations.serializers import TradingConfigurationSerializer

class LicenseViewSet(viewsets.ModelViewSet):
    queryset = License.objects.all()
    serializer_class = LicenseSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        license_instance = serializer.save(created_by=self.request.user)
        # Create default configuration
        TradingConfiguration.objects.create(license=license_instance)
    
    @action(detail=True, methods=['get', 'put', 'patch'])
    def configuration(self, request, pk=None):
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
        from django.utils import timezone
        expired_licenses = self.queryset.filter(expires_at__lt=timezone.now())
        serializer = self.get_serializer(expired_licenses, many=True)
        return Response(serializer.data)