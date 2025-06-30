# File: configurations/serializers.py
# Updated to return only new field names in API responses

from rest_framework import serializers
from .models import TradingConfiguration

class TradingConfigurationSerializer(serializers.ModelSerializer):
    """
    Serializer for Trading Configuration - New field names only
    """
    
    class Meta:
        model = TradingConfiguration
        fields = [
            'id',
            'name', 
            'description',
            'allowed_symbol',
            'strict_symbol_check',
            'session_start',
            'session_end',
            'fib_primary_buy_tp',
            'fib_primary_buy_entry',
            'fib_session_high',
            'fib_primary_buy_sl',
            'fib_primary_sell_sl',
            'fib_level_hedge_buy',
            'fib_level_hedge_sell',
            'fib_level_hedge_buy_sl',
            'fib_level_hedge_sell_sl',
            'fib_session_low',
            'fib_primary_sell_entry',
            'fib_primary_sell_tp',
            'fib_hedge_buy_tp',
            'fib_hedge_sell_tp',
            'primary_pending_timeout',
            'primary_position_timeout',
            'hedging_pending_timeout',
            'hedging_position_timeout',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """
        Convert decimal fields to float for MT5 compatibility
        """
        data = super().to_representation(instance)
        
        # Convert decimal fields to float for MT5 compatibility
        decimal_fields = [
            'fib_primary_buy_tp', 'fib_primary_buy_entry', 'fib_session_high',
            'fib_primary_buy_sl', 'fib_primary_sell_sl',
            'fib_level_hedge_buy', 'fib_level_hedge_sell',
            'fib_level_hedge_buy_sl', 'fib_level_hedge_sell_sl',
            'fib_session_low', 'fib_primary_sell_entry', 'fib_primary_sell_tp',
            'fib_hedge_buy_tp', 'fib_hedge_sell_tp',
        ]
        
        for field in decimal_fields:
            if field in data and data[field] is not None:
                data[field] = float(data[field])
        
        return data
    
    def create(self, validated_data):
        """Create configuration with proper field mapping"""
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update configuration with proper field mapping"""
        return super().update(instance, validated_data)


# Legacy serializer for complete backward compatibility (if needed)
class LegacyTradingConfigurationSerializer(serializers.ModelSerializer):
    """
    Legacy serializer that only uses the old field names
    Keeps existing API consumers working without changes
    """
    
    inp_AllowedSymbol = serializers.CharField(source='allowed_symbol')
    inp_StrictSymbolCheck = serializers.BooleanField(source='strict_symbol_check')
    inp_SessionStart = serializers.CharField(source='session_start')
    inp_SessionEnd = serializers.CharField(source='session_end')
    inp_FibLevel_1_1 = serializers.DecimalField(source='fib_primary_buy_tp', max_digits=8, decimal_places=5)
    inp_FibLevel_1_05 = serializers.DecimalField(source='fib_primary_buy_entry', max_digits=8, decimal_places=5)
    inp_FibLevel_1_0 = serializers.DecimalField(source='fib_session_high', max_digits=8, decimal_places=5)
    inp_FibLevel_PrimaryBuySL = serializers.DecimalField(source='fib_primary_buy_sl', max_digits=8, decimal_places=5)
    inp_FibLevel_PrimarySellSL = serializers.DecimalField(source='fib_primary_sell_sl', max_digits=8, decimal_places=5)
    inp_FibLevel_HedgeBuy = serializers.DecimalField(source='fib_level_hedge_buy', max_digits=8, decimal_places=5)
    inp_FibLevel_HedgeSell = serializers.DecimalField(source='fib_level_hedge_sell', max_digits=8, decimal_places=5)
    inp_FibLevel_HedgeBuySL = serializers.DecimalField(source='fib_level_hedge_buy_sl', max_digits=8, decimal_places=5)
    inp_FibLevel_HedgeSellSL = serializers.DecimalField(source='fib_level_hedge_sell_sl', max_digits=8, decimal_places=5)
    inp_FibLevel_0_0 = serializers.DecimalField(source='fib_session_low', max_digits=8, decimal_places=5)
    inp_FibLevel_Neg_05 = serializers.DecimalField(source='fib_primary_sell_entry', max_digits=8, decimal_places=5)
    inp_FibLevel_Neg_1 = serializers.DecimalField(source='fib_primary_sell_tp', max_digits=8, decimal_places=5)
    inp_FibLevel_HedgeBuyTP = serializers.DecimalField(source='fib_hedge_buy_tp', max_digits=8, decimal_places=5)
    inp_FibLevel_HedgeSellTP = serializers.DecimalField(source='fib_hedge_sell_tp', max_digits=8, decimal_places=5)
    inp_PrimaryPendingTimeout = serializers.IntegerField(source='primary_pending_timeout')
    inp_PrimaryPositionTimeout = serializers.IntegerField(source='primary_position_timeout')
    inp_HedgingPendingTimeout = serializers.IntegerField(source='hedging_pending_timeout')
    inp_HedgingPositionTimeout = serializers.IntegerField(source='hedging_position_timeout')
    
    class Meta:
        model = TradingConfiguration
        fields = [
            'inp_AllowedSymbol',
            'inp_StrictSymbolCheck',
            'inp_SessionStart',
            'inp_SessionEnd',
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
            'inp_PrimaryPendingTimeout',
            'inp_PrimaryPositionTimeout',
            'inp_HedgingPendingTimeout',
            'inp_HedgingPositionTimeout',
        ]
    
    def to_representation(self, instance):
        """Convert decimal fields to float for MT5 compatibility"""
        data = super().to_representation(instance)
        
        decimal_fields = [
            'inp_FibLevel_1_1', 'inp_FibLevel_1_05', 'inp_FibLevel_1_0',
            'inp_FibLevel_PrimaryBuySL', 'inp_FibLevel_PrimarySellSL',
            'inp_FibLevel_HedgeBuy', 'inp_FibLevel_HedgeSell',
            'inp_FibLevel_HedgeBuySL', 'inp_FibLevel_HedgeSellSL',
            'inp_FibLevel_0_0', 'inp_FibLevel_Neg_05', 'inp_FibLevel_Neg_1',
            'inp_FibLevel_HedgeBuyTP', 'inp_FibLevel_HedgeSellTP'
        ]
        
        for field in decimal_fields:
            if field in data and data[field] is not None:
                data[field] = float(data[field])
        
        return data