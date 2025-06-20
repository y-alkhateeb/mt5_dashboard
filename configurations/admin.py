from django.contrib import admin
from .models import TradingConfiguration

@admin.register(TradingConfiguration)
class TradingConfigurationAdmin(admin.ModelAdmin):
    list_display = ['license', 'allowed_symbol', 'inp_session_start', 'inp_session_end', 'updated_at']
    list_filter = ['allowed_symbol', 'strict_symbol_check', 'created_at']
    search_fields = ['license__account_id', 'allowed_symbol']
    
    fieldsets = (
        ('Symbol Validation', {
            'fields': ('license', 'allowed_symbol', 'strict_symbol_check'),
            'description': 'Configure symbol validation settings'
        }),
        ('Session Configuration', {
            'fields': ('inp_session_start', 'inp_session_end'),
            'description': 'Set trading session times'
        }),
        ('Enhanced Fibonacci Levels', {
            'fields': (
                'inp_fib_level_1_1', 'inp_fib_level_1_05', 'inp_fib_level_1_0',
                'inp_fib_level_primary_buy_sl', 'inp_fib_level_primary_sell_sl',
                'inp_fib_level_hedge_buy', 'inp_fib_level_hedge_sell',
                'inp_fib_level_hedge_buy_sl', 'inp_fib_level_hedge_sell_sl',
                'inp_fib_level_0_0', 'inp_fib_level_neg_05', 'inp_fib_level_neg_1',
                'inp_fib_level_hedge_buy_tp', 'inp_fib_level_hedge_sell_tp'
            ),
            'description': 'Configure Fibonacci retracement levels',
            'classes': ('collapse',)
        }),
        ('Timeout Configuration (Minutes)', {
            'fields': (
                'inp_primary_pending_timeout', 'inp_primary_position_timeout',
                'inp_hedging_pending_timeout', 'inp_hedging_position_timeout'
            ),
            'description': 'Set timeout values in minutes'
        }),
    )