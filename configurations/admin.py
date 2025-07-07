# File: configurations/admin.py
# Simplified admin interface without Fibonacci and Session fields

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import TradingConfiguration

@admin.register(TradingConfiguration)
class TradingConfigurationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'allowed_symbol', 'license_count_display', 'is_active', 'updated_at'
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
            'description': 'Configure symbol validation settings for MT5 EA'
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