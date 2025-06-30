# File: configurations/serializers.py
# Updated for PostgreSQL field name compatibility

from rest_framework import serializers
from .models import TradingConfiguration

class TradingConfigurationSerializer(serializers.ModelSerializer):
    """
    Serializer for Trading Configuration - Updated for PostgreSQL compatibility
    Provides both new field names and legacy API compatibility
    """
    
    # Legacy field names for API compatibility (read-only)
    inp_AllowedSymbol = serializers.CharField(source='allowed_symbol', read_only=True)
    inp_StrictSymbolCheck = serializers.BooleanField(source='strict_symbol_check', read_only=True)
    inp_SessionStart = serializers.CharField(source='session_start', read_only=True)
    inp_SessionEnd = serializers.CharField(source='session_end', read_only=True)
    inp_FibLevel_1_1 = serializers.DecimalField(source='fib_level_1_1', max_digits=8, decimal_places=5, read_only=True)
    inp_FibLevel_1_05 = serializers.DecimalField(source='fib_level_1_05', max_digits=8, decimal_places=5, read_only=True)
    inp_FibLevel_1_0 = serializers.DecimalField(source='fib_level_1_0', max_digits=8, decimal_places=5, read_only=True)
    inp_FibLevel_PrimaryBuySL = serializers.DecimalField(source='fib_level_primary_buy_sl', max_digits=8, decimal_places=5, read_only=True)
    inp_FibLevel_PrimarySellSL = serializers.DecimalField(source='fib_level_primary_sell_sl', max_digits=8, decimal_places=5, read_only=True)
    inp_FibLevel_HedgeBuy = serializers.DecimalField(source='fib_level_hedge_buy', max_digits=8, decimal_places=5, read_only=True)
    inp_FibLevel_HedgeSell = serializers.DecimalField(source='fib_level_hedge_sell', max_digits=8, decimal_places=5, read_only=True)
    inp_FibLevel_HedgeBuySL = serializers.DecimalField(source='fib_level_hedge_buy_sl', max_digits=8, decimal_places=5, read_only=True)
    inp_FibLevel_HedgeSellSL = serializers.DecimalField(source='fib_level_hedge_sell_sl', max_digits=8, decimal_places=5, read_only=True)
    inp_FibLevel_0_0 = serializers.DecimalField(source='fib_level_0_0', max_digits=8, decimal_places=5, read_only=True)
    inp_FibLevel_Neg_05 = serializers.DecimalField(source='fib_level_neg_05', max_digits=8, decimal_places=5, read_only=True)
    inp_FibLevel_Neg_1 = serializers.DecimalField(source='fib_level_neg_1', max_digits=8, decimal_places=5, read_only=True)
    inp_FibLevel_HedgeBuyTP = serializers.DecimalField(source='fib_level_hedge_buy_tp', max_digits=8, decimal_places=5, read_only=True)
    inp_FibLevel_HedgeSellTP = serializers.DecimalField(source='fib_level_hedge_sell_tp', max_digits=8, decimal_places=5, read_only=True)
    inp_PrimaryPendingTimeout = serializers.IntegerField(source='primary_pending_timeout', read_only=True)
    inp_PrimaryPositionTimeout = serializers.IntegerField(source='primary_position_timeout', read_only=True)
    inp_HedgingPendingTimeout = serializers.IntegerField(source='hedging_pending_timeout', read_only=True)
    inp_HedgingPositionTimeout = serializers.IntegerField(source='hedging_position_timeout', read_only=True)
    
    class Meta:
        model = TradingConfiguration
        fields = [
            # New field names (write/read)
            'id',
            'name',
            'description',
            'allowed_symbol',
            'strict_symbol_check',
            'session_start',
            'session_end',
            'fib_level_1_1',
            'fib_level_1_05',
            'fib_level_1_0',
            'fib_level_primary_buy_sl',
            'fib_level_primary_sell_sl',
            'fib_level_hedge_buy',
            'fib_level_hedge_sell',
            'fib_level_hedge_buy_sl',
            'fib_level_hedge_sell_sl',
            'fib_level_0_0',
            'fib_level_neg_05',
            'fib_level_neg_1',
            'fib_level_hedge_buy_tp',
            'fib_level_hedge_sell_tp',
            'primary_pending_timeout',
            'primary_position_timeout',
            'hedging_pending_timeout',
            'hedging_position_timeout',
            'is_active',
            'created_at',
            'updated_at',
            
            # Legacy field names (read-only for API compatibility)
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
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """
        Convert decimal fields to float for MT5 compatibility
        Maintains backward compatibility with existing API consumers
        """
        data = super().to_representation(instance)
        
        # Convert decimal fields to float for MT5 compatibility
        decimal_fields = [
            # New field names
            'fib_level_1_1', 'fib_level_1_05', 'fib_level_1_0',
            'fib_level_primary_buy_sl', 'fib_level_primary_sell_sl',
            'fib_level_hedge_buy', 'fib_level_hedge_sell',
            'fib_level_hedge_buy_sl', 'fib_level_hedge_sell_sl',
            'fib_level_0_0', 'fib_level_neg_05', 'fib_level_neg_1',
            'fib_level_hedge_buy_tp', 'fib_level_hedge_sell_tp',
            
            # Legacy field names for compatibility
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
    
    def create(self, validated_data):
        """Create configuration with proper field mapping"""
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update configuration with proper field mapping"""
        return super().update(instance, validated_data)


# Legacy serializer for complete backward compatibility
class LegacyTradingConfigurationSerializer(serializers.ModelSerializer):
    """
    Legacy serializer that only uses the old field names
    Keeps existing API consumers working without changes
    """
    
    inp_AllowedSymbol = serializers.CharField(source='allowed_symbol')
    inp_StrictSymbolCheck = serializers.BooleanField(source='strict_symbol_check')
    inp_SessionStart = serializers.CharField(source='session_start')
    inp_SessionEnd = serializers.CharField(source='session_end')
    inp_FibLevel_1_1 = serializers.DecimalField(source='fib_level_1_1', max_digits=8, decimal_places=5)
    inp_FibLevel_1_05 = serializers.DecimalField(source='fib_level_1_05', max_digits=8, decimal_places=5)
    inp_FibLevel_1_0 = serializers.DecimalField(source='fib_level_1_0', max_digits=8, decimal_places=5)
    inp_FibLevel_PrimaryBuySL = serializers.DecimalField(source='fib_level_primary_buy_sl', max_digits=8, decimal_places=5)
    inp_FibLevel_PrimarySellSL = serializers.DecimalField(source='fib_level_primary_sell_sl', max_digits=8, decimal_places=5)
    inp_FibLevel_HedgeBuy = serializers.DecimalField(source='fib_level_hedge_buy', max_digits=8, decimal_places=5)
    inp_FibLevel_HedgeSell = serializers.DecimalField(source='fib_level_hedge_sell', max_digits=8, decimal_places=5)
    inp_FibLevel_HedgeBuySL = serializers.DecimalField(source='fib_level_hedge_buy_sl', max_digits=8, decimal_places=5)
    inp_FibLevel_HedgeSellSL = serializers.DecimalField(source='fib_level_hedge_sell_sl', max_digits=8, decimal_places=5)
    inp_FibLevel_0_0 = serializers.DecimalField(source='fib_level_0_0', max_digits=8, decimal_places=5)
    inp_FibLevel_Neg_05 = serializers.DecimalField(source='fib_level_neg_05', max_digits=8, decimal_places=5)
    inp_FibLevel_Neg_1 = serializers.DecimalField(source='fib_level_neg_1', max_digits=8, decimal_places=5)
    inp_FibLevel_HedgeBuyTP = serializers.DecimalField(source='fib_level_hedge_buy_tp', max_digits=8, decimal_places=5)
    inp_FibLevel_HedgeSellTP = serializers.DecimalField(source='fib_level_hedge_sell_tp', max_digits=8, decimal_places=5)
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