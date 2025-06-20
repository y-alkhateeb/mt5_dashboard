from rest_framework import serializers
from .models import TradingConfiguration

class TradingConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradingConfiguration
        exclude = ['id', 'license', 'created_at', 'updated_at']
