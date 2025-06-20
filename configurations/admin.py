# File: configurations/admin.py

from django.contrib import admin
from .models import TradingConfiguration

@admin.register(TradingConfiguration)
class TradingConfigurationAdmin(admin.ModelAdmin):
    list_display = [
        'license', 'inp_AllowedSymbol', 'inp_SessionStart', 'inp_SessionEnd', 
        'inp_StrictSymbolCheck', 'updated_at'
    ]
    list_filter = ['inp_AllowedSymbol', 'inp_StrictSymbolCheck', 'created_at']
    search_fields = [
        'license__license_key', 'license__client__first_name', 
        'license__client__last_name', 'inp_AllowedSymbol'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('License', {
            'fields': ('license',),
            'description': 'Associated trading license'
        }),
        
        ('═══ Symbol Validation ═══', {
            'fields': ('inp_AllowedSymbol', 'inp_StrictSymbolCheck'),
            'description': 'Configure symbol validation settings for MT5 robot'
        }),
        
        ('═══ Session Configuration ═══', {
            'fields': ('inp_SessionStart', 'inp_SessionEnd'),
            'description': 'Set trading session times (HH:MM format)'
        }),
        
        ('═══ Enhanced Fibonacci Levels ═══', {
            'fields': (
                ('inp_FibLevel_1_1', 'inp_FibLevel_1_05', 'inp_FibLevel_1_0'),
                ('inp_FibLevel_PrimaryBuySL', 'inp_FibLevel_PrimarySellSL'),
                ('inp_FibLevel_HedgeBuy', 'inp_FibLevel_HedgeSell'),
                ('inp_FibLevel_HedgeBuySL', 'inp_FibLevel_HedgeSellSL'),
                ('inp_FibLevel_0_0', 'inp_FibLevel_Neg_05', 'inp_FibLevel_Neg_1'),
                ('inp_FibLevel_HedgeBuyTP', 'inp_FibLevel_HedgeSellTP'),
            ),
            'description': 'Configure Fibonacci retracement levels for trading strategy',
            'classes': ('collapse',)
        }),
        
        ('═══ Timeout Configuration (Minutes) ═══', {
            'fields': (
                ('inp_PrimaryPendingTimeout', 'inp_PrimaryPositionTimeout'),
                ('inp_HedgingPendingTimeout', 'inp_HedgingPositionTimeout'),
            ),
            'description': 'Set timeout values in minutes for different order types'
        }),
        
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        # Make license field readonly when editing existing configuration
        if obj:  # editing an existing object
            return self.readonly_fields + ('license',)
        return self.readonly_fields
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)