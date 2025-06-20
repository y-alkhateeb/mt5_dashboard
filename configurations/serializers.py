# File: configurations/serializers.py

from rest_framework import serializers
from .models import TradingConfiguration

class TradingConfigurationSerializer(serializers.ModelSerializer):
    """
    Serializer for Trading Configuration - matches MT5 input parameters exactly
    """
    class Meta:
        model = TradingConfiguration
        fields = [
            # ═══ Symbol Validation ═══
            'inp_AllowedSymbol',
            'inp_StrictSymbolCheck',
            
            # ═══ Session Configuration ═══
            'inp_SessionStart',
            'inp_SessionEnd',
            
            # ═══ Enhanced Fibonacci Levels ═══
            'inp_FibLevel_1_1',
            'inp_FibLevel_1_05',
            'inp_FibLevel_1_0',
            'inp_FibLevel_PrimaryBuySL',
            'inp_FibLevel_PrimarySellSL',
            'inp_FibLevel_HedgeBuy',
            'inp_FibLevel_HedgeSell',
            'inp_FibLevel_HedgeBuySL',
            'inp_FibLevel_HedgeSellSL',
            'inp_FibLevel_0_0',
            'inp_FibLevel_Neg_05',
            'inp_FibLevel_Neg_1',
            'inp_FibLevel_HedgeBuyTP',
            'inp_FibLevel_HedgeSellTP',
            
            # ═══ Timeout Configuration (Minutes) ═══
            'inp_PrimaryPendingTimeout',
            'inp_PrimaryPositionTimeout',
            'inp_HedgingPendingTimeout',
            'inp_HedgingPositionTimeout',
        ]
        
    def to_representation(self, instance):
        """
        Convert decimal fields to float for MT5 compatibility
        """
        data = super().to_representation(instance)
        
        # Convert decimal fields to float
        decimal_fields = [
            'inp_FibLevel_1_1', 'inp_FibLevel_1_05', 'inp_FibLevel_1_0',
            'inp_FibLevel_PrimaryBuySL', 'inp_FibLevel_PrimarySellSL',
            'inp_FibLevel_HedgeBuy', 'inp_FibLevel_HedgeSell',
            'inp_FibLevel_HedgeBuySL', 'inp_FibLevel_HedgeSellSL',
            'inp_FibLevel_0_0', 'inp_FibLevel_Neg_05', 'inp_FibLevel_Neg_1',
            'inp_FibLevel_HedgeBuyTP', 'inp_FibLevel_HedgeSellTP'
        ]
        
        for field in decimal_fields:
            if data[field] is not None:
                data[field] = float(data[field])
        
        return data