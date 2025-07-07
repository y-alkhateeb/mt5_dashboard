# File: configurations/serializers.py
# Updated to exclude Fibonacci and Session fields

from rest_framework import serializers
from .models import TradingConfiguration

class TradingConfigurationSerializer(serializers.ModelSerializer):
    """
    Simplified Serializer for Trading Configuration
    """
    
    class Meta:
        model = TradingConfiguration
        fields = [
            'id',
            'name', 
            'description',
            'allowed_symbol',
            'strict_symbol_check',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create configuration"""
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update configuration"""
        return super().update(instance, validated_data)


# Legacy serializer for backward compatibility (simplified)
class LegacyTradingConfigurationSerializer(serializers.ModelSerializer):
    """
    Legacy serializer that only uses the old field names for essential fields
    """
    
    inp_AllowedSymbol = serializers.CharField(source='allowed_symbol')
    inp_StrictSymbolCheck = serializers.BooleanField(source='strict_symbol_check')
    
    class Meta:
        model = TradingConfiguration
        fields = [
            'inp_AllowedSymbol',
            'inp_StrictSymbolCheck',
        ]