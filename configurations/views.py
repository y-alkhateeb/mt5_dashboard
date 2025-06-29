    
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import TradingConfiguration
from .serializers import TradingConfigurationSerializer

class TradingConfigurationViewSet(viewsets.ModelViewSet):
    """ViewSet for Trading Configuration management"""
    queryset = TradingConfiguration.objects.all()
    serializer_class = TradingConfigurationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter configurations by license if specified"""
        queryset = super().get_queryset()
        license_id = self.request.query_params.get('license_id')
        if license_id:
            queryset = queryset.filter(license_id=license_id)
        return queryset