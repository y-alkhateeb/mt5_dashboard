from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import TradingConfiguration

@admin.register(TradingConfiguration)
class TradingConfigurationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'inp_AllowedSymbol', 'inp_SessionStart', 'inp_SessionEnd', 
        'license_count_display', 'is_active', 'updated_at'
    ]
    list_filter = ['inp_AllowedSymbol', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'inp_AllowedSymbol']
    readonly_fields = ['created_at', 'updated_at', 'license_count_display']
    
    fieldsets = (
        ('Configuration Identity', {
            'fields': ('name', 'description', 'is_active')
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
