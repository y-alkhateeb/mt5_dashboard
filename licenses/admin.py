from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Client, License

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'country', 'email', 'phone', 'license_count', 'created_at']
    list_filter = ['country', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'country']
    readonly_fields = ['created_at', 'updated_at']
    
    def license_count(self, obj):
        count = obj.licenses.count()
        if count > 0:
            url = reverse('admin:licenses_license_changelist') + f'?client__id__exact={obj.id}'
            return format_html('<a href="{}">{} licenses</a>', url, count)
        return "0 licenses"
    license_count.short_description = "Licenses"
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = [
        'license_key_short', 'client_name', 'configuration_name', 'status_badge', 
        'account_status', 'login_status', 'account_trade_mode_display', 
        'login_changes_count', 'expires_at', 'usage_count', 'created_at'
    ]
    list_filter = [
        'account_trade_mode', 'is_active', 'created_at', 'expires_at', 
        'client__country', 'trading_configuration'
    ]
    search_fields = [
        'license_key', 'client__first_name', 'client__last_name', 
        'system_hash', 'account_hash', 'trading_configuration__name'
    ]
    readonly_fields = [
        'license_key', 'system_hash', 'account_hash', 'account_hash_history', 'broker_server',
        'first_used_at', 'last_used_at', 'usage_count', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('License Information', {
            'fields': ('license_key', 'client', 'trading_configuration')
        }),
        ('Trading Configuration', {
            'fields': ('account_trade_mode', 'expires_at', 'is_active')
        }),
        ('Account Binding (Auto-filled on first use)', {
            'fields': ('system_hash', 'broker_server'),
            'description': 'System hash is the primary account identifier'
        }),
        ('Account Login Tracking (Auto-filled and tracked)', {
            'fields': ('account_hash', 'account_hash_history'),
            'classes': ('collapse',),
            'description': 'Account hash tracks login changes with history'
        }),
        ('Usage Statistics', {
            'fields': ('first_used_at', 'last_used_at', 'usage_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def license_key_short(self, obj):
        return f"{obj.license_key[:12]}..."
    license_key_short.short_description = "License Key"
    
    def client_name(self, obj):
        return obj.client.full_name
    client_name.short_description = "Client"
    
    def configuration_name(self, obj):
        if obj.trading_configuration:
            url = reverse('admin:configurations_tradingconfiguration_change', args=[obj.trading_configuration.id])
            return format_html('<a href="{}">{}</a>', url, obj.trading_configuration.name)
        return "No Configuration"
    configuration_name.short_description = "Configuration"
    
    def account_status(self, obj):
        if obj.system_hash:
            return format_html('<span style="color: green;">🔒 Bound</span><br><small>{}</small>', obj.system_hash[:8] + '...')
        else:
            return format_html('<span style="color: orange;">🔓 Unbound</span>')
    account_status.short_description = "Account (Primary)"
    
    def login_status(self, obj):
        if obj.account_hash:
            changes = obj.account_hash_changes_count
            if changes > 1:
                return format_html('<span style="color: blue;">📝 Tracked</span><br><small>{} ({}x)</small>', obj.account_hash[:8] + '...', changes)
            else:
                return format_html('<span style="color: green;">📝 Set</span><br><small>{}</small>', obj.account_hash[:8] + '...')
        else:
            return format_html('<span style="color: gray;">➖ No Login</span>')
    login_status.short_description = "Login (Tracking)"
    
    def login_changes_count(self, obj):
        count = obj.account_hash_changes_count
        if count > 1:
            return format_html('<span style="color: orange;">{}</span>', count)
        elif count == 1:
            return format_html('<span style="color: green;">{}</span>', count)
        else:
            return format_html('<span style="color: gray;">0</span>')
    login_changes_count.short_description = "Login Changes"
    
    def account_trade_mode_display(self, obj):
        return obj.get_account_trade_mode_display()
    account_trade_mode_display.short_description = "Trade Mode"
    
    def status_badge(self, obj):
        status = obj.status
        color_map = {
            "Active": "green",
            "Expired": "red", 
            "Inactive": "gray",
            "Not Bound": "orange",
            "Bound - No Login": "blue"
        }
        color = color_map.get(status, "gray")
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )
    status_badge.short_description = "Status"
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
