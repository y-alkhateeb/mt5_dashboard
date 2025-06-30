# File: configurations/admin.py
# Fixed for PostgreSQL field names

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import TradingConfiguration

@admin.register(TradingConfiguration)
class TradingConfigurationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'allowed_symbol', 'session_start', 'session_end', 
        'license_count_display', 'is_active', 'updated_at'
    ]
    list_filter = ['allowed_symbol', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'allowed_symbol']
    readonly_fields = ['created_at', 'updated_at', 'license_count_display']
    
    fieldsets = (
        ('Configuration Identity', {
            'fields': ('name', 'description', 'is_active')
        }),
        
        ('═══ Symbol Validation ═══', {
            'fields': ('allowed_symbol', 'strict_symbol_check'),
            'description': 'Configure symbol validation settings for MT5 robot'
        }),
        
        ('═══ Session Configuration ═══', {
            'fields': ('session_start', 'session_end'),
            'description': 'Set trading session times (HH:MM format)'
        }),
        
        ('═══ Enhanced Fibonacci Levels ═══', {
            'fields': (
                ('fib_primary_buy_tp', 'fib_primary_buy_entry', 'fib_session_high'),
                ('fib_primary_buy_sl', 'fib_primary_sell_sl'),
                ('fib_level_hedge_buy', 'fib_level_hedge_sell'),
                ('fib_level_hedge_buy_sl', 'fib_level_hedge_sell_sl'),
                ('fib_session_low', 'fib_primary_sell_entry', 'fib_primary_sell_tp'),
                ('fib_hedge_buy_tp', 'fib_hedge_sell_tp'),
            ),
            'description': 'Configure Fibonacci retracement levels for trading strategy',
            'classes': ('collapse',)
        }),
        
        ('═══ Timeout Configuration (Minutes) ═══', {
            'fields': (
                ('primary_pending_timeout', 'primary_position_timeout'),
                ('hedging_pending_timeout', 'hedging_position_timeout'),
            ),
            'description': 'Set timeout values in minutes for different order types'
        }),
        
        ('Usage Information', {
            'fields': ('license_count_display',),
            'classes': ('collapse',)
        }),
        
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def license_count_display(self, obj):
        count = obj.license_count
        if count > 0:
            url = reverse('admin:licenses_license_changelist') + f'?trading_configuration__id__exact={obj.id}'
            return format_html('<a href="{}">{} licenses</a>', url, count)
        return "0 licenses"
    license_count_display.short_description = "Licenses Using This Config"